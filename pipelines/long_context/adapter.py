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


DEFAULT_MAX_CITATIONS = 3


def load_question(path: Path, question_id: str) -> BenchmarkQuestion:
    with path.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            question = BenchmarkQuestion.model_validate_json(line)
            if question.question_id == question_id:
                return question
    raise ValueError(f"Question not found: {question_id}")


def keywords(text: str) -> set[str]:
    stop = {
        "the",
        "and",
        "for",
        "with",
        "from",
        "what",
        "which",
        "have",
        "does",
        "using",
        "answer",
        "please",
        "state",
        "give",
        "response",
        "question",
        "year",
        "fy",
        "usd",
        "company",
        "calculate",
        "shown",
        "line",
        "items",
        "only",
        "within",
        "reported",
        "treated",
        "units",
        "percent",
        "percents",
        "round",
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
    terms = keywords(question.question) - keywords(question.company)
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


def extract_pages(pdf_path: Path) -> list[dict[str, Any]]:
    doc = fitz.open(pdf_path)
    return [{"page": i + 1, "text": page.get_text()} for i, page in enumerate(doc)]


def trim_pages_to_char_budget(pages: list[dict[str, Any]], max_document_chars: int | None) -> list[dict[str, Any]]:
    if not max_document_chars:
        return pages

    trimmed: list[dict[str, Any]] = []
    total = 0
    for page in pages:
        text = page.get("text") or ""
        if total + len(text) <= max_document_chars:
            trimmed.append(page)
            total += len(text)
            continue
        remaining = max_document_chars - total
        if remaining > 0:
            trimmed.append({"page": page["page"], "text": text[:remaining]})
        break
    return trimmed


def render_context(pages: list[dict[str, Any]]) -> str:
    return "\n\n".join(f"[PAGE {page['page']}]\n{page.get('text') or ''}" for page in pages)


def score_pages(question: BenchmarkQuestion, pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    terms = expanded_question_terms(question)
    scored: list[dict[str, Any]] = []
    for page in pages:
        text = page.get("text") or ""
        page_terms = keywords(text)
        matched_terms = sorted(terms & page_terms)
        phrase_boost = 0
        lower_text = text.lower()
        for phrase in (
            "cash flows",
            "statement of cash flows",
            "statements of operations",
            "statements of income",
            "consolidated statements of earnings",
            "balance sheets",
            "total net sales",
            "total assets",
            "gross profit",
            "cost of sales",
            "cost of revenue",
            "legal proceedings",
            "non-gaap",
            "adjusted ebitda",
            "discontinued operations",
        ):
            phrase_terms = set(phrase.replace("-", " ").split())
            if phrase in lower_text and phrase_terms & terms:
                phrase_boost += 3
        score = len(matched_terms) * 3 + phrase_boost
        if score:
            scored.append(
                {
                    "page": int(page["page"]),
                    "score": score,
                    "text": text,
                    "matched_terms": matched_terms,
                }
            )
    scored.sort(key=lambda item: (-item["score"], item["page"]))
    return scored


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


def parse_cited_pages(answer: str) -> list[int]:
    patterns = [
        r"\[PAGE\s+(\d+)\]",
        r"\b[Pp]age\s+(\d+)\b",
        r"\b[Pp]\.\s*(\d+)\b",
    ]
    pages: list[int] = []
    for pattern in patterns:
        for match in re.finditer(pattern, answer):
            page = int(match.group(1))
            if page not in pages:
                pages.append(page)
    return pages


def answer_with_llm(model: str, question: str, pages: list[dict[str, Any]]) -> tuple[str, TokenUsage]:
    context = render_context(pages)
    prompt = f"""Use only the provided document pages to answer the question.
The document is provided with page markers like [PAGE 12].
Return a concise answer and cite supporting pages using [PAGE n].

QUESTION:
{question}

DOCUMENT:
{context}
"""
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


def build_citations(
    question: BenchmarkQuestion,
    pages: list[dict[str, Any]],
    scored_pages: list[dict[str, Any]],
    cited_pages: list[int],
    max_citations: int,
) -> list[Citation]:
    by_page = {int(page["page"]): page for page in pages}
    scored_by_page = {int(page["page"]): page for page in scored_pages}
    selected_pages = [page for page in cited_pages if page in by_page]
    for scored_page in scored_pages:
        page = int(scored_page["page"])
        if page not in selected_pages:
            selected_pages.append(page)
        if len(selected_pages) >= max_citations:
            break

    citations = []
    for page in selected_pages[:max_citations]:
        scored = scored_by_page.get(page, {})
        terms = set(scored.get("matched_terms", []))
        citations.append(
            Citation(
                document_id=question.doc_name,
                page=page,
                text=text_snippet(by_page[page].get("text") or "", terms),
                metadata={
                    "score": scored.get("score"),
                    "matched_terms": scored.get("matched_terms", []),
                    "citation_source": "llm_answer" if page in cited_pages else "lexical_fallback",
                },
            )
        )
    return citations


def run_long_context_qa(
    question: BenchmarkQuestion,
    pdf_path: Path,
    *,
    model: str | None,
    no_llm: bool = False,
    max_citations: int = DEFAULT_MAX_CITATIONS,
    max_document_chars: int | None = None,
) -> BenchmarkResult:
    started = time.perf_counter()
    all_pages = extract_pages(pdf_path)
    context_pages = trim_pages_to_char_budget(all_pages, max_document_chars)
    scored_pages = score_pages(question, context_pages)

    if no_llm:
        answer = f"Loaded {len(context_pages)} document pages into long-context mode without LLM generation."
        token_usage = TokenUsage()
        cited_pages: list[int] = []
    else:
        if not model:
            raise ValueError("model is required unless --no-llm is set")
        answer, token_usage = answer_with_llm(model, question.question, context_pages)
        cited_pages = parse_cited_pages(answer)

    citations = build_citations(question, context_pages, scored_pages, cited_pages, max_citations)
    trace = [
        RetrievalTraceStep(
            step=1,
            action="load_full_document_context",
            target=question.doc_name,
            metadata={
                "page_count": len(context_pages),
                "original_page_count": len(all_pages),
                "context_chars": sum(len(page.get("text") or "") for page in context_pages),
                "max_document_chars": max_document_chars,
            },
        )
    ]
    trace.extend(
        RetrievalTraceStep(
            step=i + 2,
            action="score_page_for_citation",
            target=f"page {page['page']}",
            metadata={
                "score": page.get("score"),
                "matched_terms": page.get("matched_terms", []),
            },
        )
        for i, page in enumerate(scored_pages[:max_citations])
    )

    return BenchmarkResult(
        method="long_context_llm",
        question_id=question.question_id,
        question=question.question,
        answer=answer,
        citations=citations,
        retrieval_trace=trace,
        token_usage=token_usage,
        latency_ms=int((time.perf_counter() - started) * 1000),
        metadata={
            "pdf_path": str(pdf_path),
            "adapter_mode": "full_document_context",
            "llm_enabled": not no_llm,
            "model": model,
            "context_page_count": len(context_pages),
            "original_page_count": len(all_pages),
            "context_chars": sum(len(page.get("text") or "") for page in context_pages),
            "max_document_chars": max_document_chars,
            "max_citations": max_citations,
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Answer one benchmark question with a long-context LLM baseline.")
    parser.add_argument("--questions", type=Path, required=True)
    parser.add_argument("--question-id", required=True)
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--model", default=None)
    parser.add_argument("--no-llm", action="store_true")
    parser.add_argument("--max-citations", type=int, default=DEFAULT_MAX_CITATIONS)
    parser.add_argument("--max-document-chars", type=int, default=None)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    question = load_question(args.questions, args.question_id)
    result = run_long_context_qa(
        question,
        args.pdf,
        model=args.model,
        no_llm=args.no_llm,
        max_citations=args.max_citations,
        max_document_chars=args.max_document_chars,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(result.model_dump_json(indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
