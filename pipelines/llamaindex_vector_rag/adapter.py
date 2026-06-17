from __future__ import annotations

import argparse
import time
from pathlib import Path
from typing import Any

from llama_index.core import Document, Settings, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from benchlab.schemas import BenchmarkQuestion, BenchmarkResult, RetrievalTraceStep, TokenUsage
from pipelines.finance_rerank import financial_line_item_boost
from pipelines.vector_rag.adapter import (
    DEFAULT_ANSWER_PROMPT_MODE,
    DEFAULT_MAX_CITATIONS as VECTOR_DEFAULT_MAX_CITATIONS,
    SUPPORTED_ANSWER_PROMPT_MODES,
    answer_with_llm,
    build_citations,
    extract_pages,
    expanded_question_terms,
    keywords,
    load_question,
    parse_cited_pages,
    phrase_boost,
)


DEFAULT_EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_CHUNK_SIZE = 900
DEFAULT_CHUNK_OVERLAP = 160
DEFAULT_RETRIEVE_TOP_K = 120
DEFAULT_RERANK_TOP_K = 12
DEFAULT_MAX_CITATIONS = VECTOR_DEFAULT_MAX_CITATIONS


def context_size(chunks: list[dict[str, Any]]) -> dict[str, int]:
    """Measure the exact retrieved context passed to answer generation."""

    texts = [chunk.get("text") or "" for chunk in chunks]
    return {
        "answer_context_chunk_count": len(texts),
        "answer_context_chars": sum(len(text) for text in texts),
        "answer_context_words": sum(len(text.split()) for text in texts),
    }


def build_documents(pages: list[dict[str, Any]], document_id: str) -> list[Document]:
    return [
        Document(
            text=page.get("text") or "",
            metadata={
                "document_id": document_id,
                "page": int(page["page"]),
            },
        )
        for page in pages
        if (page.get("text") or "").strip()
    ]


def configure_llamaindex(embed_model_name: str, *, chunk_size: int, chunk_overlap: int) -> HuggingFaceEmbedding:
    embed_model = HuggingFaceEmbedding(model_name=embed_model_name)
    Settings.embed_model = embed_model
    # Disable LlamaIndex's default LLM so retrieval-only indexing never calls an external provider.
    Settings.llm = None
    Settings.node_parser = SentenceSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return embed_model


def retrieve_nodes(
    question: BenchmarkQuestion,
    pages: list[dict[str, Any]],
    *,
    embed_model_name: str,
    chunk_size: int,
    chunk_overlap: int,
    retrieve_top_k: int,
) -> list[dict[str, Any]]:
    configure_llamaindex(embed_model_name, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    documents = build_documents(pages, question.doc_name)
    index = VectorStoreIndex.from_documents(documents)
    retriever = index.as_retriever(similarity_top_k=retrieve_top_k)
    nodes = retriever.retrieve(question.question)

    retrieved: list[dict[str, Any]] = []
    for rank, node_with_score in enumerate(nodes, start=1):
        node = node_with_score.node
        metadata = dict(node.metadata or {})
        retrieved.append(
            {
                "chunk_id": node.node_id,
                "page": int(metadata.get("page") or 0),
                "text": node.get_content(metadata_mode="none"),
                "word_start": None,
                "word_end": None,
                "vector_score": node_with_score.score,
                "retrieval_rank": rank,
                "matched_terms": [],
            }
        )
    return retrieved


def rerank_nodes(
    question: BenchmarkQuestion,
    retrieved_chunks: list[dict[str, Any]],
    *,
    rerank_top_k: int,
    finance_rerank: bool = True,
) -> list[dict[str, Any]]:
    terms = expanded_question_terms(question)
    reranked = []
    for rank, chunk in enumerate(retrieved_chunks, start=1):
        text_terms = keywords(chunk.get("text") or "")
        matched_terms = sorted(terms & text_terms)
        vector_score = chunk.get("vector_score") or 0.0
        if finance_rerank:
            finance_boost, finance_reasons = financial_line_item_boost(question, chunk.get("text") or "")
        else:
            finance_boost, finance_reasons = 0.0, []
        rerank_score = (
            vector_score * 100.0
            + len(matched_terms) * 2.0
            + phrase_boost(chunk.get("text") or "", terms)
            + finance_boost
            + max(0.0, (len(retrieved_chunks) - rank + 1) / max(len(retrieved_chunks), 1))
        )
        reranked.append(
            {
                **chunk,
                "matched_terms": matched_terms,
                "finance_boost": finance_boost,
                "finance_boost_reasons": finance_reasons,
                "rerank_score": rerank_score,
                "initial_rank": rank,
            }
        )
    reranked.sort(key=lambda item: (-item["rerank_score"], item["page"], item["chunk_id"]))
    return reranked[:rerank_top_k]


def run_llamaindex_vector_rag_qa(
    question: BenchmarkQuestion,
    pdf_path: Path,
    *,
    model: str | None,
    no_llm: bool = False,
    embed_model_name: str = DEFAULT_EMBED_MODEL,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    retrieve_top_k: int = DEFAULT_RETRIEVE_TOP_K,
    rerank_top_k: int = DEFAULT_RERANK_TOP_K,
    max_citations: int = DEFAULT_MAX_CITATIONS,
    finance_rerank: bool = True,
    answer_prompt_mode: str = DEFAULT_ANSWER_PROMPT_MODE,
) -> BenchmarkResult:
    started = time.perf_counter()
    pages = extract_pages(pdf_path)
    retrieved_chunks = retrieve_nodes(
        question,
        pages,
        embed_model_name=embed_model_name,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        retrieve_top_k=retrieve_top_k,
    )
    reranked_chunks = rerank_nodes(
        question,
        retrieved_chunks,
        rerank_top_k=rerank_top_k,
        finance_rerank=finance_rerank,
    )
    context_metrics = context_size(reranked_chunks)

    if no_llm:
        answer = f"Retrieved {len(reranked_chunks)} chunks with LlamaIndex vector retrieval and lightweight reranking."
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
            action="llamaindex_build_vector_index",
            target=question.doc_name,
            metadata={
                "page_count": len(pages),
                "embedding_model": embed_model_name,
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap,
                "retrieve_top_k": retrieve_top_k,
            "rerank_top_k": rerank_top_k,
            "finance_rerank": finance_rerank,
            "answer_prompt_mode": answer_prompt_mode,
            **context_metrics,
        },
        )
    ]
    trace.extend(
        RetrievalTraceStep(
            step=i + 2,
            action="llamaindex_retrieve_node",
            target=chunk.get("chunk_id", ""),
            metadata={
                "page": chunk.get("page"),
                "retrieval_rank": chunk.get("retrieval_rank"),
                "initial_rank": chunk.get("initial_rank"),
                "vector_score": chunk.get("vector_score"),
                "rerank_score": chunk.get("rerank_score"),
                "finance_boost": chunk.get("finance_boost"),
                "finance_boost_reasons": chunk.get("finance_boost_reasons", []),
                "matched_terms": chunk.get("matched_terms", []),
            },
        )
        for i, chunk in enumerate(reranked_chunks)
    )

    return BenchmarkResult(
        method="llamaindex_vector_rag",
        question_id=question.question_id,
        question=question.question,
        answer=answer,
        citations=citations,
        retrieval_trace=trace,
        token_usage=token_usage,
        latency_ms=int((time.perf_counter() - started) * 1000),
        metadata={
            "pdf_path": str(pdf_path),
            "adapter_mode": "llamaindex_vector_retrieval",
            "llm_enabled": not no_llm,
            "model": model,
            "embedding_model": embed_model_name,
            "page_count": len(pages),
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
            "retrieve_top_k": retrieve_top_k,
            "rerank_top_k": rerank_top_k,
            "max_citations": max_citations,
            "finance_rerank": finance_rerank,
            "answer_prompt_mode": answer_prompt_mode,
            **context_metrics,
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Answer one benchmark question with a LlamaIndex Vector RAG baseline.")
    parser.add_argument("--questions", type=Path, required=True)
    parser.add_argument("--question-id", required=True)
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--model", default=None)
    parser.add_argument("--no-llm", action="store_true")
    parser.add_argument("--embed-model", default=DEFAULT_EMBED_MODEL)
    parser.add_argument("--chunk-size", type=int, default=DEFAULT_CHUNK_SIZE)
    parser.add_argument("--chunk-overlap", type=int, default=DEFAULT_CHUNK_OVERLAP)
    parser.add_argument("--retrieve-top-k", type=int, default=DEFAULT_RETRIEVE_TOP_K)
    parser.add_argument("--rerank-top-k", type=int, default=DEFAULT_RERANK_TOP_K)
    parser.add_argument("--max-citations", type=int, default=DEFAULT_MAX_CITATIONS)
    parser.add_argument("--disable-finance-rerank", action="store_true")
    parser.add_argument(
        "--answer-prompt-mode",
        choices=SUPPORTED_ANSWER_PROMPT_MODES,
        default=DEFAULT_ANSWER_PROMPT_MODE,
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    question = load_question(args.questions, args.question_id)
    result = run_llamaindex_vector_rag_qa(
        question,
        args.pdf,
        model=args.model,
        no_llm=args.no_llm,
        embed_model_name=args.embed_model,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        retrieve_top_k=args.retrieve_top_k,
        rerank_top_k=args.rerank_top_k,
        max_citations=args.max_citations,
        finance_rerank=not args.disable_finance_rerank,
        answer_prompt_mode=args.answer_prompt_mode,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(result.model_dump_json(indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
