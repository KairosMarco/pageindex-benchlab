from __future__ import annotations

import argparse
import math
import time
from collections import Counter
from pathlib import Path
from typing import Any

from benchlab.schemas import BenchmarkQuestion, BenchmarkResult, RetrievalTraceStep, TokenUsage
from pipelines.vector_rag.adapter import (
    DEFAULT_ANSWER_PROMPT_MODE,
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_CHUNK_WORDS,
    DEFAULT_MAX_CITATIONS,
    DEFAULT_RERANK_TOP_K,
    DEFAULT_RETRIEVE_TOP_K,
    SUPPORTED_ANSWER_PROMPT_MODES,
    answer_with_llm,
    build_chunks,
    build_citations,
    cosine,
    expanded_question_terms,
    extract_pages,
    keywords,
    load_question,
    parse_cited_pages,
    phrase_boost,
    query_vector,
    tfidf_vectors,
    tokenize,
)


DEFAULT_FUSION_TOP_K = 30
DEFAULT_RRF_K = 60


def bm25_scores(question: BenchmarkQuestion, chunks: list[dict[str, Any]], *, k1: float = 1.5, b: float = 0.75) -> list[dict[str, Any]]:
    query_terms = list(expanded_question_terms(question))
    tokenized_chunks = [tokenize(chunk.get("text") or "") for chunk in chunks]
    doc_count = max(1, len(chunks))
    avg_len = sum(len(tokens) for tokens in tokenized_chunks) / doc_count if doc_count else 0.0

    df: Counter[str] = Counter()
    for tokens in tokenized_chunks:
        df.update(set(tokens))

    scored: list[dict[str, Any]] = []
    for chunk, tokens in zip(chunks, tokenized_chunks):
        counts = Counter(tokens)
        doc_len = max(1, len(tokens))
        score = 0.0
        for term in query_terms:
            if term not in counts:
                continue
            idf = math.log(1 + (doc_count - df[term] + 0.5) / (df[term] + 0.5))
            tf = counts[term]
            denominator = tf + k1 * (1 - b + b * doc_len / max(avg_len, 1.0))
            score += idf * (tf * (k1 + 1)) / denominator
        if score > 0:
            scored.append({**chunk, "bm25_score": score})
    scored.sort(key=lambda item: (-item["bm25_score"], item["page"], item["chunk_id"]))
    return scored


def vector_scores(question: BenchmarkQuestion, chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    vectors, idf = tfidf_vectors(chunks)
    q_vector = query_vector(question, idf)
    scored: list[dict[str, Any]] = []
    for chunk, vector in zip(chunks, vectors):
        score = cosine(q_vector, vector)
        if score > 0:
            scored.append({**chunk, "vector_score": score})
    scored.sort(key=lambda item: (-item["vector_score"], item["page"], item["chunk_id"]))
    return scored


def reciprocal_rank_fusion(
    bm25_ranked: list[dict[str, Any]],
    vector_ranked: list[dict[str, Any]],
    *,
    fusion_top_k: int,
    rrf_k: int,
) -> list[dict[str, Any]]:
    fused: dict[str, dict[str, Any]] = {}

    # RRF combines rank positions rather than raw scores, which keeps BM25 and vector scales comparable.
    for source, ranked in (("bm25", bm25_ranked), ("vector", vector_ranked)):
        for rank, chunk in enumerate(ranked[:fusion_top_k], start=1):
            chunk_id = chunk["chunk_id"]
            item = fused.setdefault(
                chunk_id,
                {
                    **chunk,
                    "rrf_score": 0.0,
                    "bm25_rank": None,
                    "vector_rank": None,
                    "bm25_score": chunk.get("bm25_score"),
                    "vector_score": chunk.get("vector_score"),
                },
            )
            item["rrf_score"] += 1.0 / (rrf_k + rank)
            item[f"{source}_rank"] = rank
            if source == "bm25":
                item["bm25_score"] = chunk.get("bm25_score")
            else:
                item["vector_score"] = chunk.get("vector_score")

    fused_items = list(fused.values())
    fused_items.sort(key=lambda item: (-item["rrf_score"], item["page"], item["chunk_id"]))
    return fused_items


def rerank_fused_chunks(
    question: BenchmarkQuestion,
    chunks: list[dict[str, Any]],
    *,
    rerank_top_k: int,
) -> list[dict[str, Any]]:
    terms = expanded_question_terms(question)
    reranked = []
    for rank, chunk in enumerate(chunks, start=1):
        text_terms = keywords(chunk.get("text") or "")
        matched_terms = sorted(terms & text_terms)
        rerank_score = (
            chunk.get("rrf_score", 0.0) * 1000.0
            + len(matched_terms) * 2.0
            + phrase_boost(chunk.get("text") or "", terms)
            + max(0.0, (len(chunks) - rank + 1) / max(len(chunks), 1))
        )
        reranked.append(
            {
                **chunk,
                "matched_terms": matched_terms,
                "rerank_score": rerank_score,
                "fusion_rank": rank,
            }
        )
    reranked.sort(key=lambda item: (-item["rerank_score"], item["page"], item["chunk_id"]))
    return reranked[:rerank_top_k]


def retrieve_fuse_and_rerank(
    question: BenchmarkQuestion,
    chunks: list[dict[str, Any]],
    *,
    retrieve_top_k: int,
    fusion_top_k: int,
    rerank_top_k: int,
    rrf_k: int,
) -> list[dict[str, Any]]:
    bm25_ranked = bm25_scores(question, chunks)[:retrieve_top_k]
    vector_ranked = vector_scores(question, chunks)[:retrieve_top_k]
    fused = reciprocal_rank_fusion(bm25_ranked, vector_ranked, fusion_top_k=fusion_top_k, rrf_k=rrf_k)
    return rerank_fused_chunks(question, fused, rerank_top_k=rerank_top_k)


def run_hybrid_rag_qa(
    question: BenchmarkQuestion,
    pdf_path: Path,
    *,
    model: str | None,
    no_llm: bool = False,
    chunk_words: int = DEFAULT_CHUNK_WORDS,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    retrieve_top_k: int = DEFAULT_RETRIEVE_TOP_K,
    fusion_top_k: int = DEFAULT_FUSION_TOP_K,
    rerank_top_k: int = DEFAULT_RERANK_TOP_K,
    rrf_k: int = DEFAULT_RRF_K,
    max_citations: int = DEFAULT_MAX_CITATIONS,
    answer_prompt_mode: str = DEFAULT_ANSWER_PROMPT_MODE,
) -> BenchmarkResult:
    started = time.perf_counter()
    pages = extract_pages(pdf_path)
    chunks = build_chunks(pages, chunk_words, chunk_overlap)
    reranked_chunks = retrieve_fuse_and_rerank(
        question,
        chunks,
        retrieve_top_k=retrieve_top_k,
        fusion_top_k=fusion_top_k,
        rerank_top_k=rerank_top_k,
        rrf_k=rrf_k,
    )

    if no_llm:
        answer = f"Retrieved {len(reranked_chunks)} chunks with BM25/vector hybrid fusion and reranking."
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
            action="hybrid_fuse_and_rerank_chunk",
            target=chunk.get("chunk_id", ""),
            metadata={
                "page": chunk.get("page"),
                "bm25_rank": chunk.get("bm25_rank"),
                "vector_rank": chunk.get("vector_rank"),
                "fusion_rank": chunk.get("fusion_rank"),
                "bm25_score": chunk.get("bm25_score"),
                "vector_score": chunk.get("vector_score"),
                "rrf_score": chunk.get("rrf_score"),
                "rerank_score": chunk.get("rerank_score"),
                "matched_terms": chunk.get("matched_terms", []),
            },
        )
        for i, chunk in enumerate(reranked_chunks)
    )

    return BenchmarkResult(
        method="hybrid_rag_bm25_tfidf_rrf",
        question_id=question.question_id,
        question=question.question,
        answer=answer,
        citations=citations,
        retrieval_trace=trace,
        token_usage=token_usage,
        latency_ms=int((time.perf_counter() - started) * 1000),
        metadata={
            "pdf_path": str(pdf_path),
            "adapter_mode": "bm25_tfidf_rrf_plus_rerank",
            "llm_enabled": not no_llm,
            "model": model,
            "page_count": len(pages),
            "chunk_count": len(chunks),
            "chunk_words": chunk_words,
            "chunk_overlap": chunk_overlap,
            "retrieve_top_k": retrieve_top_k,
            "fusion_top_k": fusion_top_k,
            "rerank_top_k": rerank_top_k,
            "rrf_k": rrf_k,
            "max_citations": max_citations,
            "answer_prompt_mode": answer_prompt_mode,
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Answer one benchmark question with a Hybrid RAG baseline.")
    parser.add_argument("--questions", type=Path, required=True)
    parser.add_argument("--question-id", required=True)
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--model", default=None)
    parser.add_argument("--no-llm", action="store_true")
    parser.add_argument("--chunk-words", type=int, default=DEFAULT_CHUNK_WORDS)
    parser.add_argument("--chunk-overlap", type=int, default=DEFAULT_CHUNK_OVERLAP)
    parser.add_argument("--retrieve-top-k", type=int, default=DEFAULT_RETRIEVE_TOP_K)
    parser.add_argument("--fusion-top-k", type=int, default=DEFAULT_FUSION_TOP_K)
    parser.add_argument("--rerank-top-k", type=int, default=DEFAULT_RERANK_TOP_K)
    parser.add_argument("--rrf-k", type=int, default=DEFAULT_RRF_K)
    parser.add_argument("--max-citations", type=int, default=DEFAULT_MAX_CITATIONS)
    parser.add_argument(
        "--answer-prompt-mode",
        choices=SUPPORTED_ANSWER_PROMPT_MODES,
        default=DEFAULT_ANSWER_PROMPT_MODE,
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    question = load_question(args.questions, args.question_id)
    result = run_hybrid_rag_qa(
        question,
        args.pdf,
        model=args.model,
        no_llm=args.no_llm,
        chunk_words=args.chunk_words,
        chunk_overlap=args.chunk_overlap,
        retrieve_top_k=args.retrieve_top_k,
        fusion_top_k=args.fusion_top_k,
        rerank_top_k=args.rerank_top_k,
        rrf_k=args.rrf_k,
        max_citations=args.max_citations,
        answer_prompt_mode=args.answer_prompt_mode,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(result.model_dump_json(indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
