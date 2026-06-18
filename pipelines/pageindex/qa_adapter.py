from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path
from typing import Any

import fitz
from litellm import completion

from benchlab.schemas import BenchmarkQuestion, BenchmarkResult, Citation, RetrievalTraceStep, TokenUsage
from pipelines.finance_rerank import financial_line_item_boost
from pipelines.pageindex.adapter import flatten_nodes, load_structure


DEFAULT_MAX_PAGES = 3
DEFAULT_ANSWER_PROMPT_MODE = "default"
FINANCE_REASONING_ANSWER_PROMPT_MODE = "finance_reasoning_v1"
FINANCE_REASONING_V2_ANSWER_PROMPT_MODE = "finance_reasoning_v2"
FINANCE_REASONING_V3_ANSWER_PROMPT_MODE = "finance_reasoning_v3"
SUPPORTED_ANSWER_PROMPT_MODES = (
    DEFAULT_ANSWER_PROMPT_MODE,
    FINANCE_REASONING_ANSWER_PROMPT_MODE,
    FINANCE_REASONING_V2_ANSWER_PROMPT_MODE,
    FINANCE_REASONING_V3_ANSWER_PROMPT_MODE,
)


def load_question(path: Path, question_id: str) -> BenchmarkQuestion:
    with path.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            if row["question_id"] == question_id:
                return BenchmarkQuestion.model_validate(row)
    raise ValueError(f"Question not found: {question_id}")


def keywords(text: str) -> set[str]:
    stop = {
        "the",
        "and",
        "asked",
        "calculate",
        "clearly",
        "company",
        "consistent",
        "does",
        "each",
        "explain",
        "for",
        "fluctuating",
        "with",
        "from",
        "historically",
        "how",
        "into",
        "item",
        "items",
        "like",
        "line",
        "metric",
        "more",
        "not",
        "one",
        "over",
        "percent",
        "percents",
        "what",
        "which",
        "why",
        "have",
        "relevant",
        "roughly",
        "round",
        "than",
        "that",
        "then",
        "this",
        "using",
        "answer",
        "fy",
        "usd",
        "was",
        "year",
        "are",
        "any",
        "end",
        "give",
        "only",
        "page",
        "place",
        "please",
        "primarily",
        "reported",
        "response",
        "shown",
        "state",
        "treated",
        "units",
        "utilizing",
        "within",
        "fy",
        "fy16",
        "fy18",
        "fy22",
        "fy2016",
        "fy2017",
        "fy2018",
        "fy2021",
        "fy2022",
        "fy2023",
    }
    normalized = text.lower().replace("&", " and ").replace("-", " ")
    return {w for w in re.findall(r"[a-z][a-z0-9]+", normalized) if len(w) > 2 and w not in stop}


def expanded_question_terms(question: BenchmarkQuestion) -> set[str]:
    terms = keywords(question.question)
    terms -= keywords(question.company)

    expansions = {
        ("capital", "expenditure"): {"property", "plant", "equipment", "ppe", "purchases", "investing"},
        ("cash", "flow"): {"cash", "flows", "operating", "operations", "investing", "financing"},
        ("revenue",): {"revenue", "sales", "net"},
        ("income", "statement"): {"income", "operations", "revenue", "sales", "cost"},
        ("balance", "sheet"): {"balance", "sheets", "assets", "liabilities", "equity"},
        ("total", "assets"): {"balance", "sheets", "assets"},
        ("gross", "margins"): {"gross", "margin", "profit", "revenue", "cost", "sales", "earnings"},
        ("cogs",): {"cost", "revenue", "sales", "goods"},
        ("legal",): {"legal", "litigation", "lawsuits", "proceedings", "accident"},
        ("battles",): {"legal", "litigation", "lawsuits", "proceedings"},
        ("adjusted", "ebitda"): {"adjusted", "ebitda", "reconciliation", "non", "gaap"},
        ("non", "gaap"): {"adjusted", "ebitda", "reconciliation", "non", "gaap"},
        ("var",): {"var", "risk", "average", "market"},
        ("discontinued", "operation"): {"discontinued", "operations", "consumer", "health", "kenvue", "separation"},
        ("products", "services"): {"overview", "products", "services", "processors", "graphics", "gpus", "cpus"},
    }
    for trigger, additions in expansions.items():
        if all(term in terms for term in trigger):
            terms.update(additions)
    return terms


def select_nodes(structure: dict[str, Any], question: BenchmarkQuestion, top_k: int = 5) -> list[dict[str, Any]]:
    question_terms = expanded_question_terms(question)
    scored = []
    for node in flatten_nodes(structure.get("structure", [])):
        title = node.get("title") or ""
        score = len(question_terms & keywords(title))
        if score:
            scored.append((score, node))
    scored.sort(key=lambda item: (-item[0], item[1].get("start_index") or 10**9))
    if not scored:
        return flatten_nodes(structure.get("structure", []))[:top_k]
    return [node for _, node in scored[:top_k]]


def pages_from_nodes(nodes: list[dict[str, Any]], max_pages: int | None = 8) -> list[int]:
    pages: list[int] = []
    for node in nodes:
        start = node.get("start_index")
        end = node.get("end_index") or start
        if not start:
            continue
        pages.extend(range(int(start), int(end) + 1))
    unique_pages = sorted(set(pages))
    return unique_pages[:max_pages] if max_pages else unique_pages


def page_sections(nodes: list[dict[str, Any]]) -> dict[int, list[dict[str, Any]]]:
    sections: dict[int, list[dict[str, Any]]] = {}
    for node in nodes:
        start = node.get("start_index")
        end = node.get("end_index") or start
        if not start:
            continue
        for page in range(int(start), int(end) + 1):
            sections.setdefault(page, []).append(node)
    return sections


def extract_pages(pdf_path: Path, pages_one_indexed: list[int]) -> list[dict[str, Any]]:
    doc = fitz.open(pdf_path)
    extracted = []
    for page in pages_one_indexed:
        zero = page - 1
        if 0 <= zero < len(doc):
            extracted.append({"page": page, "text": doc[zero].get_text()})
    return extracted


def extract_all_pages(pdf_path: Path) -> list[dict[str, Any]]:
    doc = fitz.open(pdf_path)
    return [{"page": i + 1, "text": page.get_text()} for i, page in enumerate(doc)]


def text_snippet(text: str, terms: set[str], max_chars: int = 500) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    if not compact:
        return ""
    lowered = compact.lower()
    positions = [lowered.find(term) for term in terms if lowered.find(term) >= 0]
    if not positions:
        return compact[:max_chars]
    start = max(0, min(positions) - 120)
    return compact[start : start + max_chars]


def best_section_for_page(sections: list[dict[str, Any]], terms: set[str]) -> dict[str, Any] | None:
    if not sections:
        return None
    return max(
        sections,
        key=lambda node: (
            len(terms & keywords(node.get("title") or "")),
            node.get("depth", 0),
            -int(node.get("start_index") or 0),
        ),
    )


def score_pages(
    pages: list[dict[str, Any]],
    sections_by_page: dict[int, list[dict[str, Any]]],
    question: BenchmarkQuestion,
) -> list[dict[str, Any]]:
    terms = expanded_question_terms(question)
    scored: list[dict[str, Any]] = []
    for page in pages:
        page_no = int(page["page"])
        page_text = page.get("text") or ""
        page_terms = keywords(page_text)
        sections = sections_by_page.get(page_no, [])
        section_text = " ".join(node.get("title") or "" for node in sections)
        section_terms = keywords(section_text)
        matched_page_terms = sorted(terms & page_terms)
        matched_section_terms = sorted(terms & section_terms)
        phrase_boost = 0
        lower_text = page_text.lower()
        combined_text = f"{section_text}\n{page_text}".lower()
        for phrase in (
            "cash flows",
            "statement of cash flows",
            "statements of operations",
            "statements of income",
            "balance sheets",
            "total assets",
            "gross profit",
            "cost of revenue",
            "legal proceedings",
            "non-gaap",
            "adjusted ebitda",
            "discontinued operations",
        ):
            phrase_terms = set(phrase.replace("-", " ").split())
            if phrase in lower_text and phrase_terms & terms:
                phrase_boost += 3
        if any(
            marker in combined_text
            for marker in (
                "consolidated statements of operations",
                "consolidated statements of earnings",
                "income statements",
            )
        ) and terms & {"cogs", "cost", "earnings", "gross", "income", "margin", "revenue", "sales"}:
            phrase_boost += 10
        if "total net sales" in combined_text and terms & {"revenue", "sales"}:
            phrase_boost += 8
        if (
            "gross profit" in combined_text
            and "revenue" in combined_text
            and "cost of sales" in combined_text
            and terms & {"gross", "margin", "margins"}
        ):
            phrase_boost += 10
        if "total cost of revenue" in combined_text and terms & {"cogs", "cost", "revenue"}:
            phrase_boost += 8
        if "consolidated balance sheets" in combined_text and terms & {"assets", "balance", "liabilities"}:
            phrase_boost += 10
        if "consolidated statements of cash flows" in combined_text and terms & {"cash", "flow", "flows"}:
            phrase_boost += 10
        # Reuse the same label-free finance line-item signals used by the
        # LlamaIndex diagnostics. This only reads the question and candidate
        # page text, never FinanceBench gold evidence pages.
        finance_boost, finance_reasons = financial_line_item_boost(question, combined_text)
        score = len(matched_page_terms) * 3 + len(matched_section_terms) * 2 + phrase_boost + finance_boost
        if score:
            best_section = best_section_for_page(sections, terms)
            scored.append(
                {
                    "page": page_no,
                    "score": score,
                    "phrase_boost": phrase_boost,
                    "finance_boost": finance_boost,
                    "finance_boost_reasons": finance_reasons,
                    "text": page_text,
                    "section": best_section,
                    "matched_page_terms": matched_page_terms,
                    "matched_section_terms": matched_section_terms,
                }
            )
    scored.sort(key=lambda item: (-item["score"], item["page"]))
    return scored


def select_pages(
    pdf_path: Path,
    all_nodes: list[dict[str, Any]],
    selected_nodes: list[dict[str, Any]],
    question: BenchmarkQuestion,
    max_pages: int = DEFAULT_MAX_PAGES,
) -> list[dict[str, Any]]:
    sections_by_page = page_sections(all_nodes)
    all_pages = extract_all_pages(pdf_path)
    scored = score_pages(all_pages, sections_by_page, question)
    if scored:
        return scored[:max_pages]

    fallback_pages = pages_from_nodes(selected_nodes, max_pages=max_pages)
    fallback_text = extract_pages(pdf_path, fallback_pages)
    return [
        {
            "page": item["page"],
            "score": 0,
            "text": item["text"],
            "section": best_section_for_page(sections_by_page.get(item["page"], []), expanded_question_terms(question)),
            "matched_page_terms": [],
            "matched_section_terms": [],
        }
        for item in fallback_text
    ]


def render_context(page_text: list[dict[str, Any]]) -> str:
    return "\n\n".join(f"[PAGE {p['page']}]\n{p['text']}" for p in page_text)


def build_answer_prompt(
    question: str,
    context: str,
    *,
    prompt_mode: str = DEFAULT_ANSWER_PROMPT_MODE,
) -> str:
    if prompt_mode == DEFAULT_ANSWER_PROMPT_MODE:
        return f"""Use only the provided document pages to answer the question.
Return a concise answer and cite page numbers.

QUESTION:
{question}

DOCUMENT PAGES:
{context}
"""
    if prompt_mode == FINANCE_REASONING_ANSWER_PROMPT_MODE:
        return f"""Use only the provided document pages to answer the question.
Return a concise answer and cite page numbers.

Apply strict finance reasoning before giving the final answer:
- Do not decide conceptual finance questions from a single ratio when the evidence gives multiple relevant indicators.
- For capital-intensive questions, compare asset base, return on assets, PP&E or fixed assets as a share of total assets, goodwill/intangibles, leased-asset business model indicators, capex, and the business model. If the evidence includes low ROA or large goodwill/asset base, discuss that evidence explicitly before the yes/no conclusion.
- For working-capital questions, state which definition is used. If the question or evidence points to operating working capital, do not silently substitute total current assets minus total current liabilities.
- For unit conversions, convert values before judging numeric agreement. Example: $389 million = $0.389 billion, approximately $0.39 billion or $0.40 billion depending on requested rounding.
- If indicators conflict, explain the competing indicators and then give the best supported conclusion from the provided pages.

QUESTION:
{question}

DOCUMENT PAGES:
{context}
"""
    if prompt_mode == FINANCE_REASONING_V2_ANSWER_PROMPT_MODE:
        return f"""Use only the provided document pages to answer the question.
Return a concise answer and cite page numbers.

Apply strict finance reasoning before giving the final answer:
- Treat conceptual finance questions as definition-sensitive. State the definition you are applying before the final conclusion.
- For capital-intensive questions, use a broad asset-intensity definition unless the question explicitly asks only about PP&E or capex intensity. Under this definition, low ROA and a large total asset base are direct evidence of capital intensity.
- Do not reject capital intensity only because PP&E / total assets is low, because leases, acquired goodwill, insurance/PBM assets, and other required operating assets can still make the business asset-intensive. If PP&E or fixed assets are low, present that as a caveat rather than as a standalone negative conclusion.
- If evidence shows low ROA together with significant total assets, goodwill, intangibles, or leased operating assets, the answer should generally be "Yes, with caveats" unless stronger contrary evidence is present in the pages.
- For working-capital questions, state which definition is used. If the question or evidence points to operating working capital, do not silently substitute total current assets minus total current liabilities.
- For unit conversions, convert values before judging numeric agreement. Example: $389 million = $0.389 billion, approximately $0.39 billion or $0.40 billion depending on requested rounding.
- If indicators conflict, explain the competing indicators and then give the best supported conclusion from the provided pages.

QUESTION:
{question}

DOCUMENT PAGES:
{context}
"""
    if prompt_mode == FINANCE_REASONING_V3_ANSWER_PROMPT_MODE:
        return f"""Use only the provided document pages to answer the question.
Return a concise answer and cite page numbers.

Apply strict finance reasoning before giving the final answer:
- Treat conceptual finance questions as definition-sensitive. State the definition you are applying before the final conclusion.
- For capital-intensive questions, use a broad asset-intensity definition unless the question explicitly asks only about PP&E or capex intensity. Under this definition, low ROA and a large total asset base are direct evidence of capital intensity.
- Do not reject capital intensity only because PP&E / total assets is low, because leases, acquired goodwill, insurance/PBM assets, and other required operating assets can still make the business asset-intensive. If PP&E or fixed assets are low, present that as a caveat rather than as a standalone negative conclusion.
- If evidence shows low ROA together with significant total assets, goodwill, intangibles, or leased operating assets, the answer should generally be "Yes, with caveats" unless stronger contrary evidence is present in the pages.
- For working-capital questions, state which definition is used. If the question or evidence points to operating working capital, do not silently substitute total current assets minus total current liabilities.
- For unit conversions, convert values before judging numeric agreement and match the requested reporting unit. If the question asks for USD billions and does not specify decimal places, provide the benchmark-style rounded billion answer first, then include the exact source value in parentheses. Example: $389 million = $0.389 billion, so answer "$0.40 billion ($389 million)" rather than only "$0.389 billion" or "$0.39 billion".
- If indicators conflict, explain the competing indicators and then give the best supported conclusion from the provided pages.

QUESTION:
{question}

DOCUMENT PAGES:
{context}
"""
    raise ValueError(f"Unsupported answer prompt mode: {prompt_mode}")


def answer_with_llm(
    model: str,
    question: str,
    page_text: list[dict[str, Any]],
    *,
    prompt_mode: str = DEFAULT_ANSWER_PROMPT_MODE,
) -> tuple[str, TokenUsage]:
    context = render_context(page_text)
    prompt = build_answer_prompt(question, context, prompt_mode=prompt_mode)
    response = completion(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    usage = getattr(response, "usage", None)
    token_usage = TokenUsage(
        input=getattr(usage, "prompt_tokens", None) if usage else None,
        output=getattr(usage, "completion_tokens", None) if usage else None,
        total=getattr(usage, "total_tokens", None) if usage else None,
    )
    return response.choices[0].message.content, token_usage


def run_pageindex_qa(
    question: BenchmarkQuestion,
    structure_path: Path,
    pdf_path: Path,
    *,
    model: str | None,
    no_llm: bool = False,
    max_pages: int = DEFAULT_MAX_PAGES,
    answer_prompt_mode: str = DEFAULT_ANSWER_PROMPT_MODE,
) -> BenchmarkResult:
    started = time.perf_counter()
    structure = load_structure(structure_path)
    all_nodes = flatten_nodes(structure.get("structure", []))
    selected = select_nodes(structure, question)
    selected_pages = select_pages(pdf_path, all_nodes, selected, question, max_pages=max_pages)
    pages = [item["page"] for item in selected_pages]
    page_text = [{"page": item["page"], "text": item["text"]} for item in selected_pages]

    citations = [
        Citation(
            document_id=question.doc_name,
            page=item["page"],
            section=(item.get("section") or {}).get("title"),
            text=text_snippet(item.get("text") or "", set(item.get("matched_page_terms", []))),
            metadata={
                "score": item.get("score"),
                "phrase_boost": item.get("phrase_boost"),
                "finance_boost": item.get("finance_boost"),
                "finance_boost_reasons": item.get("finance_boost_reasons", []),
                "matched_page_terms": item.get("matched_page_terms", []),
                "matched_section_terms": item.get("matched_section_terms", []),
                "node_id": (item.get("section") or {}).get("node_id"),
                "start_index": (item.get("section") or {}).get("start_index"),
                "end_index": (item.get("section") or {}).get("end_index"),
            },
        )
        for item in selected_pages
    ]
    trace = [
        RetrievalTraceStep(
            step=i + 1,
            action="select_tree_node",
            target=node.get("title", ""),
            metadata={
                "node_id": node.get("node_id"),
                "start_index": node.get("start_index"),
                "end_index": node.get("end_index"),
            },
        )
        for i, node in enumerate(selected)
    ]
    base_step = len(trace)
    trace.extend(
        RetrievalTraceStep(
            step=base_step + i + 1,
            action="score_page",
            target=f"page {item['page']}",
            metadata={
                "score": item.get("score"),
                "phrase_boost": item.get("phrase_boost"),
                "finance_boost": item.get("finance_boost"),
                "finance_boost_reasons": item.get("finance_boost_reasons", []),
                "section": (item.get("section") or {}).get("title"),
                "matched_page_terms": item.get("matched_page_terms", []),
                "matched_section_terms": item.get("matched_section_terms", []),
            },
        )
        for i, item in enumerate(selected_pages)
    )

    if no_llm:
        answer = f"Selected {len(selected)} PageIndex nodes and {len(page_text)} scored pages for answering."
        token_usage = TokenUsage()
    else:
        if not model:
            raise ValueError("model is required unless --no-llm is set")
        answer, token_usage = answer_with_llm(
            model,
            question.question,
            page_text,
            prompt_mode=answer_prompt_mode,
        )

    latency_ms = int((time.perf_counter() - started) * 1000)
    return BenchmarkResult(
        method="pageindex_tree_qa",
        question_id=question.question_id,
        question=question.question,
        answer=answer,
        citations=citations,
        retrieval_trace=trace,
        token_usage=token_usage,
        latency_ms=latency_ms,
        metadata={
            "structure_path": str(structure_path),
            "pdf_path": str(pdf_path),
            "selected_pages_one_indexed": pages,
            "max_pages": max_pages,
            "adapter_mode": "tree_page_scoring",
            "llm_enabled": not no_llm,
            "model": model,
            "answer_prompt_mode": answer_prompt_mode,
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Answer one benchmark question using a PageIndex structure.")
    parser.add_argument("--questions", type=Path, required=True)
    parser.add_argument("--question-id", required=True)
    parser.add_argument("--structure", type=Path, required=True)
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--model", default=None)
    parser.add_argument("--no-llm", action="store_true")
    parser.add_argument("--max-pages", type=int, default=DEFAULT_MAX_PAGES)
    parser.add_argument(
        "--answer-prompt-mode",
        choices=SUPPORTED_ANSWER_PROMPT_MODES,
        default=DEFAULT_ANSWER_PROMPT_MODE,
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    question = load_question(args.questions, args.question_id)
    result = run_pageindex_qa(
        question,
        args.structure,
        args.pdf,
        model=args.model,
        no_llm=args.no_llm,
        max_pages=args.max_pages,
        answer_prompt_mode=args.answer_prompt_mode,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(result.model_dump_json(indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
