from __future__ import annotations

import argparse
import time
from functools import lru_cache
from pathlib import Path
from typing import Any

from sentence_transformers import CrossEncoder

from llama_index.core import Settings, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import TextNode
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.retrievers.bm25 import BM25Retriever

from benchlab.schemas import BenchmarkQuestion, BenchmarkResult, RetrievalTraceStep, TokenUsage
from pipelines.finance_rerank import financial_line_item_boost
from pipelines.llamaindex_vector_rag.adapter import DEFAULT_EMBED_MODEL
from pipelines.vector_rag.adapter import (
    DEFAULT_MAX_CITATIONS as VECTOR_DEFAULT_MAX_CITATIONS,
    answer_with_llm,
    build_citations,
    expanded_question_terms,
    extract_pages,
    keywords,
    load_question,
    parse_cited_pages,
    phrase_boost,
)


DEFAULT_CHUNK_SIZE = 900
DEFAULT_CHUNK_OVERLAP = 160
DEFAULT_VECTOR_TOP_K = 120
DEFAULT_BM25_TOP_K = 120
DEFAULT_FUSION_TOP_K = 120
DEFAULT_RERANK_TOP_K = 12
DEFAULT_RRF_K = 60
DEFAULT_MAX_CITATIONS = VECTOR_DEFAULT_MAX_CITATIONS
DEFAULT_CROSS_ENCODER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
DEFAULT_CROSS_ENCODER_CANDIDATES = 60


def context_size(chunks: list[dict[str, Any]]) -> dict[str, int]:
    """Measure the exact retrieved context passed to answer generation."""

    texts = [chunk.get("text") or "" for chunk in chunks]
    return {
        "answer_context_chunk_count": len(texts),
        "answer_context_chars": sum(len(text) for text in texts),
        "answer_context_words": sum(len(text.split()) for text in texts),
    }


def configure_llamaindex(embed_model_name: str, *, chunk_size: int, chunk_overlap: int) -> HuggingFaceEmbedding:
    embed_model = HuggingFaceEmbedding(model_name=embed_model_name)
    Settings.embed_model = embed_model
    Settings.llm = None
    Settings.node_parser = SentenceSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return embed_model


def build_nodes(pages: list[dict[str, Any]], *, chunk_size: int, chunk_overlap: int, document_id: str) -> list[TextNode]:
    splitter = SentenceSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    nodes: list[TextNode] = []
    for page in pages:
        text = page.get("text") or ""
        if not text.strip():
            continue
        page_nodes = splitter.get_nodes_from_documents(
            [
                TextNode(
                    text=text,
                    metadata={
                        "document_id": document_id,
                        "page": int(page["page"]),
                    },
                )
            ]
        )
        for node_index, node in enumerate(page_nodes):
            node.metadata["document_id"] = document_id
            node.metadata["page"] = int(page["page"])
            node.metadata["page_node_index"] = node_index
            nodes.append(node)
    return nodes


def node_to_chunk(node: TextNode, score: float | None, *, source: str, rank: int) -> dict[str, Any]:
    metadata = dict(node.metadata or {})
    return {
        "chunk_id": node.node_id,
        "page": int(metadata.get("page") or 0),
        "text": node.get_content(metadata_mode="none"),
        "word_start": None,
        "word_end": None,
        f"{source}_score": score,
        f"{source}_rank": rank,
        "matched_terms": [],
    }


def reciprocal_rank_fusion(
    bm25_ranked: list[dict[str, Any]],
    vector_ranked: list[dict[str, Any]],
    *,
    fusion_top_k: int,
    rrf_k: int,
) -> list[dict[str, Any]]:
    fused: dict[str, dict[str, Any]] = {}
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
                    "bm25_score": None,
                    "vector_score": None,
                },
            )
            item["rrf_score"] += 1.0 / (rrf_k + rank)
            item[f"{source}_rank"] = rank
            item[f"{source}_score"] = chunk.get(f"{source}_score")
    fused_items = list(fused.values())
    fused_items.sort(key=lambda item: (-item["rrf_score"], item["page"], item["chunk_id"]))
    return fused_items


@lru_cache(maxsize=2)
def load_cross_encoder(model_name: str) -> CrossEncoder:
    return CrossEncoder(model_name)


def rerank_fused_chunks(
    question: BenchmarkQuestion,
    chunks: list[dict[str, Any]],
    *,
    rerank_top_k: int,
    finance_rerank: bool = True,
    cross_encoder_model: str | None = None,
    cross_encoder_candidates: int = DEFAULT_CROSS_ENCODER_CANDIDATES,
) -> list[dict[str, Any]]:
    terms = expanded_question_terms(question)
    reranked = []
    for rank, chunk in enumerate(chunks, start=1):
        text_terms = keywords(chunk.get("text") or "")
        matched_terms = sorted(terms & text_terms)
        if finance_rerank:
            finance_boost, finance_reasons = financial_line_item_boost(question, chunk.get("text") or "")
        else:
            finance_boost, finance_reasons = 0.0, []
        rerank_score = (
            chunk.get("rrf_score", 0.0) * 1000.0
            + len(matched_terms) * 2.0
            + phrase_boost(chunk.get("text") or "", terms)
            + finance_boost
            + max(0.0, (len(chunks) - rank + 1) / max(len(chunks), 1))
        )
        reranked.append(
            {
                **chunk,
                "matched_terms": matched_terms,
                "finance_boost": finance_boost,
                "finance_boost_reasons": finance_reasons,
                "rerank_score": rerank_score,
                "fusion_rank": rank,
            }
        )
    reranked.sort(key=lambda item: (-item["rerank_score"], item["page"], item["chunk_id"]))

    if cross_encoder_model:
        candidates = reranked[:cross_encoder_candidates]
        model = load_cross_encoder(cross_encoder_model)
        pairs = [(question.question, chunk.get("text") or "") for chunk in candidates]
        cross_scores = model.predict(pairs)
        cross_reranked = [
            {
                **chunk,
                "cross_encoder_model": cross_encoder_model,
                "cross_encoder_score": float(score),
                "pre_cross_encoder_rank": rank,
            }
            for rank, (chunk, score) in enumerate(zip(candidates, cross_scores), start=1)
        ]
        # Cross-encoder scores are query-passage relevance logits, so they become the final ordering signal.
        cross_reranked.sort(key=lambda item: (-item["cross_encoder_score"], item["page"], item["chunk_id"]))
        return cross_reranked[:rerank_top_k]

    return reranked[:rerank_top_k]


def retrieve_fuse_and_rerank(
    question: BenchmarkQuestion,
    pages: list[dict[str, Any]],
    *,
    embed_model_name: str,
    chunk_size: int,
    chunk_overlap: int,
    vector_top_k: int,
    bm25_top_k: int,
    fusion_top_k: int,
    rerank_top_k: int,
    rrf_k: int,
    finance_rerank: bool = True,
    cross_encoder_model: str | None = None,
    cross_encoder_candidates: int = DEFAULT_CROSS_ENCODER_CANDIDATES,
) -> tuple[list[dict[str, Any]], int]:
    configure_llamaindex(embed_model_name, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    nodes = build_nodes(pages, chunk_size=chunk_size, chunk_overlap=chunk_overlap, document_id=question.doc_name)

    vector_index = VectorStoreIndex(nodes)
    vector_nodes = vector_index.as_retriever(similarity_top_k=vector_top_k).retrieve(question.question)
    bm25_nodes = BM25Retriever.from_defaults(nodes=nodes, similarity_top_k=bm25_top_k).retrieve(question.question)

    vector_ranked = [
        node_to_chunk(item.node, item.score, source="vector", rank=rank)
        for rank, item in enumerate(vector_nodes, start=1)
    ]
    bm25_ranked = [
        node_to_chunk(item.node, item.score, source="bm25", rank=rank)
        for rank, item in enumerate(bm25_nodes, start=1)
    ]
    fused = reciprocal_rank_fusion(
        bm25_ranked,
        vector_ranked,
        fusion_top_k=fusion_top_k,
        rrf_k=rrf_k,
    )
    return rerank_fused_chunks(
        question,
        fused,
        rerank_top_k=rerank_top_k,
        finance_rerank=finance_rerank,
        cross_encoder_model=cross_encoder_model,
        cross_encoder_candidates=cross_encoder_candidates,
    ), len(nodes)


def run_llamaindex_hybrid_rag_qa(
    question: BenchmarkQuestion,
    pdf_path: Path,
    *,
    model: str | None,
    no_llm: bool = False,
    embed_model_name: str = DEFAULT_EMBED_MODEL,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    vector_top_k: int = DEFAULT_VECTOR_TOP_K,
    bm25_top_k: int = DEFAULT_BM25_TOP_K,
    fusion_top_k: int = DEFAULT_FUSION_TOP_K,
    rerank_top_k: int = DEFAULT_RERANK_TOP_K,
    rrf_k: int = DEFAULT_RRF_K,
    max_citations: int = DEFAULT_MAX_CITATIONS,
    finance_rerank: bool = True,
    cross_encoder_model: str | None = None,
    cross_encoder_candidates: int = DEFAULT_CROSS_ENCODER_CANDIDATES,
) -> BenchmarkResult:
    started = time.perf_counter()
    pages = extract_pages(pdf_path)
    reranked_chunks, node_count = retrieve_fuse_and_rerank(
        question,
        pages,
        embed_model_name=embed_model_name,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        vector_top_k=vector_top_k,
        bm25_top_k=bm25_top_k,
        fusion_top_k=fusion_top_k,
        rerank_top_k=rerank_top_k,
        rrf_k=rrf_k,
        finance_rerank=finance_rerank,
        cross_encoder_model=cross_encoder_model,
        cross_encoder_candidates=cross_encoder_candidates,
    )
    context_metrics = context_size(reranked_chunks)

    if no_llm:
        answer = f"Retrieved {len(reranked_chunks)} chunks with LlamaIndex BM25/vector hybrid fusion."
        token_usage = TokenUsage()
        cited_pages: list[int] = []
    else:
        if not model:
            raise ValueError("model is required unless --no-llm is set")
        answer, token_usage = answer_with_llm(model, question.question, reranked_chunks)
        cited_pages = parse_cited_pages(answer)

    citations = build_citations(question, reranked_chunks, cited_pages, max_citations)
    trace = [
        RetrievalTraceStep(
            step=1,
            action="llamaindex_build_hybrid_index",
            target=question.doc_name,
            metadata={
                "page_count": len(pages),
                "node_count": node_count,
                "embedding_model": embed_model_name,
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap,
                "vector_top_k": vector_top_k,
                "bm25_top_k": bm25_top_k,
                "fusion_top_k": fusion_top_k,
                "rerank_top_k": rerank_top_k,
                "rrf_k": rrf_k,
                "finance_rerank": finance_rerank,
                "cross_encoder_model": cross_encoder_model,
                "cross_encoder_candidates": cross_encoder_candidates,
                **context_metrics,
            },
        )
    ]
    trace.extend(
        RetrievalTraceStep(
            step=i + 2,
            action="llamaindex_hybrid_fuse_and_rerank_node",
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
                "finance_boost": chunk.get("finance_boost"),
                "finance_boost_reasons": chunk.get("finance_boost_reasons", []),
                "cross_encoder_score": chunk.get("cross_encoder_score"),
                "pre_cross_encoder_rank": chunk.get("pre_cross_encoder_rank"),
                "matched_terms": chunk.get("matched_terms", []),
            },
        )
        for i, chunk in enumerate(reranked_chunks)
    )

    return BenchmarkResult(
        method="llamaindex_hybrid_rag",
        question_id=question.question_id,
        question=question.question,
        answer=answer,
        citations=citations,
        retrieval_trace=trace,
        token_usage=token_usage,
        latency_ms=int((time.perf_counter() - started) * 1000),
        metadata={
            "pdf_path": str(pdf_path),
            "adapter_mode": "llamaindex_bm25_vector_rrf_plus_rerank",
            "llm_enabled": not no_llm,
            "model": model,
            "embedding_model": embed_model_name,
            "page_count": len(pages),
            "node_count": node_count,
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
            "vector_top_k": vector_top_k,
            "bm25_top_k": bm25_top_k,
            "fusion_top_k": fusion_top_k,
            "rerank_top_k": rerank_top_k,
            "rrf_k": rrf_k,
            "max_citations": max_citations,
            "finance_rerank": finance_rerank,
            "cross_encoder_model": cross_encoder_model,
            "cross_encoder_candidates": cross_encoder_candidates,
            **context_metrics,
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Answer one question with a LlamaIndex Hybrid RAG baseline.")
    parser.add_argument("--questions", type=Path, required=True)
    parser.add_argument("--question-id", required=True)
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--model", default=None)
    parser.add_argument("--no-llm", action="store_true")
    parser.add_argument("--embed-model", default=DEFAULT_EMBED_MODEL)
    parser.add_argument("--chunk-size", type=int, default=DEFAULT_CHUNK_SIZE)
    parser.add_argument("--chunk-overlap", type=int, default=DEFAULT_CHUNK_OVERLAP)
    parser.add_argument("--vector-top-k", type=int, default=DEFAULT_VECTOR_TOP_K)
    parser.add_argument("--bm25-top-k", type=int, default=DEFAULT_BM25_TOP_K)
    parser.add_argument("--fusion-top-k", type=int, default=DEFAULT_FUSION_TOP_K)
    parser.add_argument("--rerank-top-k", type=int, default=DEFAULT_RERANK_TOP_K)
    parser.add_argument("--rrf-k", type=int, default=DEFAULT_RRF_K)
    parser.add_argument("--max-citations", type=int, default=DEFAULT_MAX_CITATIONS)
    parser.add_argument("--disable-finance-rerank", action="store_true")
    parser.add_argument("--cross-encoder-model", default=None)
    parser.add_argument("--cross-encoder-candidates", type=int, default=DEFAULT_CROSS_ENCODER_CANDIDATES)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    question = load_question(args.questions, args.question_id)
    result = run_llamaindex_hybrid_rag_qa(
        question,
        args.pdf,
        model=args.model,
        no_llm=args.no_llm,
        embed_model_name=args.embed_model,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        vector_top_k=args.vector_top_k,
        bm25_top_k=args.bm25_top_k,
        fusion_top_k=args.fusion_top_k,
        rerank_top_k=args.rerank_top_k,
        rrf_k=args.rrf_k,
        max_citations=args.max_citations,
        finance_rerank=not args.disable_finance_rerank,
        cross_encoder_model=args.cross_encoder_model,
        cross_encoder_candidates=args.cross_encoder_candidates,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(result.model_dump_json(indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
