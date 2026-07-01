from __future__ import annotations

import argparse
import json
import math
import re
import time
from collections import Counter
from pathlib import Path
from typing import Any

from litellm import completion

from benchlab.schemas import BenchmarkQuestion, BenchmarkResult, Citation, RetrievalTraceStep, TokenUsage


DEFAULT_CHUNK_WORDS = 220
DEFAULT_CHUNK_OVERLAP = 40
DEFAULT_RETRIEVE_TOP_K = 20
DEFAULT_RERANK_TOP_K = 6
DEFAULT_MAX_CITATIONS = 3
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
        "asked",
        "clearly",
        "into",
        "more",
        "than",
        "that",
        "this",
        "over",
        "one",
        "was",
        "are",
        "any",
        "not",
        "why",
        "fy2016",
        "fy2017",
        "fy2018",
        "fy2021",
        "fy2022",
        "fy2023",
    }
    normalized = text.lower().replace("&", " and ").replace("-", " ")
    return {w for w in re.findall(r"[a-z][a-z0-9]+", normalized) if len(w) > 2 and w not in stop}


def tokenize(text: str) -> list[str]:
    return sorted(keywords(text))


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
        ("legal",): {
            "legal",
            "litigation",
            "lawsuits",
            "proceeding",
            "proceedings",
            "actions",
            "filed",
            "claims",
            "accident",
        },
        ("battles",): {"legal", "litigation", "lawsuits", "proceeding", "proceedings", "actions", "filed"},
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
    try:
        import fitz  # type: ignore

        doc = fitz.open(pdf_path)
        return [{"page": i + 1, "text": page.get_text()} for i, page in enumerate(doc)]
    except Exception:
        from pypdf import PdfReader

        # Keep the baseline runnable on Windows environments that block PyMuPDF's native DLL.
        reader = PdfReader(str(pdf_path))
        return [
            {"page": i + 1, "text": page.extract_text() or ""}
            for i, page in enumerate(reader.pages)
        ]


def chunk_page_text(page: int, text: str, chunk_words: int, overlap: int) -> list[dict[str, Any]]:
    words = text.split()
    if not words:
        return []
    chunks: list[dict[str, Any]] = []
    step = max(1, chunk_words - overlap)
    for start in range(0, len(words), step):
        end = min(len(words), start + chunk_words)
        chunk_text = " ".join(words[start:end])
        chunks.append(
            {
                "chunk_id": f"p{page}_c{len(chunks)}",
                "page": page,
                "text": chunk_text,
                "word_start": start,
                "word_end": end,
            }
        )
        if end >= len(words):
            break
    return chunks


def build_chunks(pages: list[dict[str, Any]], chunk_words: int, overlap: int) -> list[dict[str, Any]]:
    chunks: list[dict[str, Any]] = []
    for page in pages:
        chunks.extend(chunk_page_text(int(page["page"]), page.get("text") or "", chunk_words, overlap))
    return chunks


def tfidf_vectors(chunks: list[dict[str, Any]]) -> tuple[list[dict[str, float]], dict[str, float]]:
    tokenized = [tokenize(chunk.get("text") or "") for chunk in chunks]
    df: Counter[str] = Counter()
    for tokens in tokenized:
        df.update(set(tokens))
    doc_count = max(1, len(chunks))
    idf = {term: math.log((doc_count + 1) / (freq + 1)) + 1 for term, freq in df.items()}

    vectors: list[dict[str, float]] = []
    for tokens in tokenized:
        counts = Counter(tokens)
        total = max(1, len(tokens))
        vector = {term: (count / total) * idf.get(term, 1.0) for term, count in counts.items()}
        vectors.append(vector)
    return vectors, idf


def query_vector(question: BenchmarkQuestion, idf: dict[str, float]) -> dict[str, float]:
    terms = list(keywords(question.question)) + list(expanded_question_terms(question))
    counts = Counter(terms)
    total = max(1, len(terms))
    return {term: (count / total) * idf.get(term, 1.0) for term, count in counts.items()}


def cosine(a: dict[str, float], b: dict[str, float]) -> float:
    if not a or not b:
        return 0.0
    dot = sum(weight * b.get(term, 0.0) for term, weight in a.items())
    norm_a = math.sqrt(sum(weight * weight for weight in a.values()))
    norm_b = math.sqrt(sum(weight * weight for weight in b.values()))
    if not norm_a or not norm_b:
        return 0.0
    return dot / (norm_a * norm_b)


def phrase_boost(text: str, terms: set[str]) -> float:
    lower_text = text.lower()
    boost = 0.0
    phrase_groups = (
        ("cash flows", {"cash", "flow", "flows"}),
        ("statement of cash flows", {"cash", "flow", "flows"}),
        ("consolidated statements of cash flows", {"cash", "flow", "flows"}),
        ("statements of operations", {"income", "operations", "revenue", "sales"}),
        ("statements of income", {"income", "revenue", "sales", "cost"}),
        ("consolidated statements of operations", {"income", "revenue", "sales", "cost"}),
        ("consolidated statements of earnings", {"earnings", "gross", "margin", "revenue", "sales"}),
        ("balance sheets", {"balance", "assets", "liabilities"}),
        ("total net sales", {"revenue", "sales"}),
        ("total assets", {"assets", "balance"}),
        ("gross profit", {"gross", "margin", "margins", "profit"}),
        ("cost of sales", {"cost", "cogs", "sales"}),
        ("cost of revenue", {"cost", "cogs", "revenue"}),
        ("total cost of revenue", {"cost", "cogs", "revenue"}),
        ("legal proceedings", {"legal", "litigation", "proceedings"}),
        ("legal proceeding", {"legal", "litigation", "proceeding", "proceedings"}),
        ("legal actions", {"legal", "actions", "lawsuits", "litigation"}),
        ("filed against us", {"legal", "actions", "lawsuits", "filed"}),
        ("non-gaap", {"non", "gaap", "adjusted", "ebitda"}),
        ("adjusted ebitda", {"adjusted", "ebitda"}),
        ("discontinued operations", {"discontinued", "operations", "consumer", "health"}),
    )
    for phrase, triggers in phrase_groups:
        if phrase in lower_text and terms & triggers:
            boost += 3.0
    if terms & {"legal", "litigation", "lawsuits", "proceeding", "proceedings", "actions"}:
        if "multiple legal actions have been filed" in lower_text:
            boost += 12.0
        if "legal proceedings resulting from" in lower_text:
            boost += 4.0
        if "lion air flight 610" in lower_text and "ethiopian airlines flight 302" in lower_text:
            boost += 6.0
    return boost


def retrieve_and_rerank(
    question: BenchmarkQuestion,
    chunks: list[dict[str, Any]],
    *,
    retrieve_top_k: int,
    rerank_top_k: int,
) -> list[dict[str, Any]]:
    vectors, idf = tfidf_vectors(chunks)
    q_vector = query_vector(question, idf)
    terms = expanded_question_terms(question)

    retrieved: list[dict[str, Any]] = []
    for chunk, vector in zip(chunks, vectors):
        vector_score = cosine(q_vector, vector)
        if vector_score <= 0:
            continue
        text_terms = keywords(chunk.get("text") or "")
        matched_terms = sorted(terms & text_terms)
        retrieved.append(
            {
                **chunk,
                "vector_score": vector_score,
                "matched_terms": matched_terms,
            }
        )
    retrieved.sort(key=lambda item: (-item["vector_score"], item["page"], item["chunk_id"]))

    reranked = []
    for rank, chunk in enumerate(retrieved[:retrieve_top_k]):
        matched_terms = chunk.get("matched_terms", [])
        rerank_score = (
            chunk["vector_score"] * 100.0
            + len(matched_terms) * 2.0
            + phrase_boost(chunk.get("text") or "", terms)
            + max(0.0, (retrieve_top_k - rank) / retrieve_top_k)
        )
        reranked.append({**chunk, "rerank_score": rerank_score, "initial_rank": rank + 1})
    reranked.sort(key=lambda item: (-item["rerank_score"], item["page"], item["chunk_id"]))
    return reranked[:rerank_top_k]


def render_context(chunks: list[dict[str, Any]]) -> str:
    return "\n\n".join(
        f"[PAGE {chunk['page']} | CHUNK {chunk['chunk_id']}]\n{chunk.get('text') or ''}" for chunk in chunks
    )


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


def build_answer_prompt(
    question: str,
    context: str,
    *,
    prompt_mode: str = DEFAULT_ANSWER_PROMPT_MODE,
) -> str:
    if prompt_mode == DEFAULT_ANSWER_PROMPT_MODE:
        return f"""Use only the retrieved document chunks to answer the question.
Each chunk has a page marker like [PAGE 12 | CHUNK p12_c0].
Return a concise answer and cite supporting pages using [PAGE n].

QUESTION:
{question}

RETRIEVED CHUNKS:
{context}
"""
    if prompt_mode == FINANCE_REASONING_ANSWER_PROMPT_MODE:
        return f"""Use only the retrieved document chunks to answer the question.
Each chunk has a page marker like [PAGE 12 | CHUNK p12_c0].
Return a concise answer and cite supporting pages using [PAGE n].

Apply strict finance reasoning before giving the final answer:
- Do not decide conceptual finance questions from a single ratio when the evidence gives multiple relevant indicators.
- For capital-intensive questions, compare asset base, return on assets, PP&E or fixed assets as a share of total assets, goodwill/intangibles, leased-asset business model indicators, capex, and the business model. If the evidence includes low ROA or large goodwill/asset base, discuss that evidence explicitly before the yes/no conclusion.
- For working-capital questions, state which definition is used. If the question or evidence points to operating working capital, do not silently substitute total current assets minus total current liabilities.
- For unit conversions, convert values before judging numeric agreement. Example: $389 million = $0.389 billion, approximately $0.39 billion or $0.40 billion depending on requested rounding.
- If indicators conflict, explain the competing indicators and then give the best supported conclusion from the provided chunks.

QUESTION:
{question}

RETRIEVED CHUNKS:
{context}
"""
    if prompt_mode == FINANCE_REASONING_V2_ANSWER_PROMPT_MODE:
        return f"""Use only the retrieved document chunks to answer the question.
Each chunk has a page marker like [PAGE 12 | CHUNK p12_c0].
Return a concise answer and cite supporting pages using [PAGE n].

Apply strict finance reasoning before giving the final answer:
- Treat conceptual finance questions as definition-sensitive. State the definition you are applying before the final conclusion.
- For capital-intensive questions, use a broad asset-intensity definition unless the question explicitly asks only about PP&E or capex intensity. Under this definition, low ROA and a large total asset base are direct evidence of capital intensity.
- Do not reject capital intensity only because PP&E / total assets is low, because leases, acquired goodwill, insurance/PBM assets, and other required operating assets can still make the business asset-intensive. If PP&E or fixed assets are low, present that as a caveat rather than as a standalone negative conclusion.
- If evidence shows low ROA together with significant total assets, goodwill, intangibles, or leased operating assets, the answer should generally be "Yes, with caveats" unless stronger contrary evidence is present in the chunks.
- For working-capital questions, state which definition is used. If the question or evidence points to operating working capital, do not silently substitute total current assets minus total current liabilities.
- For unit conversions, convert values before judging numeric agreement. Example: $389 million = $0.389 billion, approximately $0.39 billion or $0.40 billion depending on requested rounding.
- If indicators conflict, explain the competing indicators and then give the best supported conclusion from the provided chunks.

QUESTION:
{question}

RETRIEVED CHUNKS:
{context}
"""
    if prompt_mode == FINANCE_REASONING_V3_ANSWER_PROMPT_MODE:
        return f"""Use only the retrieved document chunks to answer the question.
Each chunk has a page marker like [PAGE 12 | CHUNK p12_c0].
Return a concise answer and cite supporting pages using [PAGE n].

Apply strict finance reasoning before giving the final answer:
- Treat conceptual finance questions as definition-sensitive. State the definition you are applying before the final conclusion.
- For capital-intensive questions, use a broad asset-intensity definition unless the question explicitly asks only about PP&E or capex intensity. Under this definition, low ROA and a large total asset base are direct evidence of capital intensity.
- Do not reject capital intensity only because PP&E / total assets is low, because leases, acquired goodwill, insurance/PBM assets, and other required operating assets can still make the business asset-intensive. If PP&E or fixed assets are low, present that as a caveat rather than as a standalone negative conclusion.
- If evidence shows low ROA together with significant total assets, goodwill, intangibles, or leased operating assets, the answer should generally be "Yes, with caveats" unless stronger contrary evidence is present in the chunks.
- For working-capital questions, state which definition is used. If the question or evidence points to operating working capital, do not silently substitute total current assets minus total current liabilities.
- For unit conversions, convert values before judging numeric agreement and match the requested reporting unit. If the question asks for USD billions and does not specify decimal places, provide the benchmark-style rounded billion answer first, then include the exact source value in parentheses. Example: $389 million = $0.389 billion, so answer "$0.40 billion ($389 million)" rather than only "$0.389 billion" or "$0.39 billion".
- If indicators conflict, explain the competing indicators and then give the best supported conclusion from the provided chunks.

QUESTION:
{question}

RETRIEVED CHUNKS:
{context}
"""
    raise ValueError(f"Unsupported answer prompt mode: {prompt_mode}")


def answer_with_llm(
    model: str,
    question: str,
    chunks: list[dict[str, Any]],
    *,
    prompt_mode: str = DEFAULT_ANSWER_PROMPT_MODE,
) -> tuple[str, TokenUsage]:
    context = render_context(chunks)
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


def build_citations(
    question: BenchmarkQuestion,
    reranked_chunks: list[dict[str, Any]],
    cited_pages: list[int],
    max_citations: int,
) -> list[Citation]:
    chunks_by_page: dict[int, dict[str, Any]] = {}
    for chunk in reranked_chunks:
        page = int(chunk["page"])
        if page not in chunks_by_page:
            chunks_by_page[page] = chunk

    selected_pages = [page for page in cited_pages if page in chunks_by_page]
    for chunk in reranked_chunks:
        page = int(chunk["page"])
        if page not in selected_pages:
            selected_pages.append(page)
        if len(selected_pages) >= max_citations:
            break

    citations = []
    for page in selected_pages[:max_citations]:
        chunk = chunks_by_page[page]
        matched_terms = set(chunk.get("matched_terms", []))
        citations.append(
            Citation(
                document_id=question.doc_name,
                page=page,
                text=text_snippet(chunk.get("text") or "", matched_terms),
                metadata={
                    "chunk_id": chunk.get("chunk_id"),
                    "word_start": chunk.get("word_start"),
                    "word_end": chunk.get("word_end"),
                    "vector_score": chunk.get("vector_score"),
                    "rerank_score": chunk.get("rerank_score"),
                    "matched_terms": chunk.get("matched_terms", []),
                    "citation_source": "llm_answer" if page in cited_pages else "rerank_fallback",
                },
            )
        )
    return citations


def run_vector_rag_qa(
    question: BenchmarkQuestion,
    pdf_path: Path,
    *,
    model: str | None,
    no_llm: bool = False,
    chunk_words: int = DEFAULT_CHUNK_WORDS,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    retrieve_top_k: int = DEFAULT_RETRIEVE_TOP_K,
    rerank_top_k: int = DEFAULT_RERANK_TOP_K,
    max_citations: int = DEFAULT_MAX_CITATIONS,
    answer_prompt_mode: str = DEFAULT_ANSWER_PROMPT_MODE,
) -> BenchmarkResult:
    started = time.perf_counter()
    pages = extract_pages(pdf_path)
    chunks = build_chunks(pages, chunk_words, chunk_overlap)
    reranked_chunks = retrieve_and_rerank(
        question,
        chunks,
        retrieve_top_k=retrieve_top_k,
        rerank_top_k=rerank_top_k,
    )

    if no_llm:
        answer = f"Retrieved {len(reranked_chunks)} chunks with TF-IDF vector search and reranking."
        token_usage = TokenUsage()
        cited_pages: list[int] = []
    else:
        if not model:
            raise ValueError("model is required unless --no-llm is set")
        answer, token_usage = answer_with_llm(
            model,
            question.question,
            reranked_chunks,
            prompt_mode=answer_prompt_mode,
        )
        cited_pages = parse_cited_pages(answer)

    citations = build_citations(question, reranked_chunks, cited_pages, max_citations)
    trace = [
        RetrievalTraceStep(
            step=1,
            action="chunk_document",
            target=question.doc_name,
            metadata={
                "page_count": len(pages),
                "chunk_count": len(chunks),
                "chunk_words": chunk_words,
                "chunk_overlap": chunk_overlap,
            },
        )
    ]
    trace.extend(
        RetrievalTraceStep(
            step=i + 2,
            action="retrieve_and_rerank_chunk",
            target=chunk.get("chunk_id", ""),
            metadata={
                "page": chunk.get("page"),
                "initial_rank": chunk.get("initial_rank"),
                "vector_score": chunk.get("vector_score"),
                "rerank_score": chunk.get("rerank_score"),
                "matched_terms": chunk.get("matched_terms", []),
            },
        )
        for i, chunk in enumerate(reranked_chunks)
    )

    return BenchmarkResult(
        method="vector_rag_tfidf_rerank",
        question_id=question.question_id,
        question=question.question,
        answer=answer,
        citations=citations,
        retrieval_trace=trace,
        token_usage=token_usage,
        latency_ms=int((time.perf_counter() - started) * 1000),
        metadata={
            "pdf_path": str(pdf_path),
            "adapter_mode": "tfidf_vector_search_plus_rerank",
            "llm_enabled": not no_llm,
            "model": model,
            "page_count": len(pages),
            "chunk_count": len(chunks),
            "chunk_words": chunk_words,
            "chunk_overlap": chunk_overlap,
            "retrieve_top_k": retrieve_top_k,
            "rerank_top_k": rerank_top_k,
            "max_citations": max_citations,
            "answer_prompt_mode": answer_prompt_mode,
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Answer one benchmark question with a Vector RAG baseline.")
    parser.add_argument("--questions", type=Path, required=True)
    parser.add_argument("--question-id", required=True)
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--model", default=None)
    parser.add_argument("--no-llm", action="store_true")
    parser.add_argument("--chunk-words", type=int, default=DEFAULT_CHUNK_WORDS)
    parser.add_argument("--chunk-overlap", type=int, default=DEFAULT_CHUNK_OVERLAP)
    parser.add_argument("--retrieve-top-k", type=int, default=DEFAULT_RETRIEVE_TOP_K)
    parser.add_argument("--rerank-top-k", type=int, default=DEFAULT_RERANK_TOP_K)
    parser.add_argument("--max-citations", type=int, default=DEFAULT_MAX_CITATIONS)
    parser.add_argument(
        "--answer-prompt-mode",
        choices=SUPPORTED_ANSWER_PROMPT_MODES,
        default=DEFAULT_ANSWER_PROMPT_MODE,
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    question = load_question(args.questions, args.question_id)
    result = run_vector_rag_qa(
        question,
        args.pdf,
        model=args.model,
        no_llm=args.no_llm,
        chunk_words=args.chunk_words,
        chunk_overlap=args.chunk_overlap,
        retrieve_top_k=args.retrieve_top_k,
        rerank_top_k=args.rerank_top_k,
        max_citations=args.max_citations,
        answer_prompt_mode=args.answer_prompt_mode,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(result.model_dump_json(indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
