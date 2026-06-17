from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchlab.schemas import BenchmarkQuestion  # noqa: E402
from pipelines.llamaindex_vector_rag.adapter import (  # noqa: E402
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_EMBED_MODEL,
    DEFAULT_MAX_CITATIONS,
    DEFAULT_RERANK_TOP_K,
    DEFAULT_RETRIEVE_TOP_K,
    run_llamaindex_vector_rag_qa,
)
from pipelines.vector_rag.adapter import (  # noqa: E402
    DEFAULT_ANSWER_PROMPT_MODE,
    SUPPORTED_ANSWER_PROMPT_MODES,
)


DEFAULT_QUESTIONS = ROOT / "datasets" / "financebench" / "mvp_questions.jsonl"
DEFAULT_PDF_DIR = ROOT / "datasets" / "raw" / "financebench" / "pdfs"
DEFAULT_OUTPUT_DIR = ROOT / "reports" / "llamaindex_vector_rag" / "qa_smoke"
DEFAULT_MANIFEST = ROOT / "reports" / "llamaindex_vector_rag" / "qa_smoke_manifest.json"


def load_questions(path: Path) -> list[BenchmarkQuestion]:
    with path.open(encoding="utf-8") as f:
        return [BenchmarkQuestion.model_validate_json(line) for line in f if line.strip()]


def has_model_key() -> bool:
    return any(
        os.getenv(name)
        for name in (
            "DASHSCOPE_API_KEY",
            "DEEPSEEK_API_KEY",
            "OPENAI_API_KEY",
            "ANTHROPIC_API_KEY",
            "GEMINI_API_KEY",
            "OPENROUTER_API_KEY",
        )
    )


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def compact_result_metadata(result_metadata: dict[str, Any]) -> dict[str, Any]:
    metadata = dict(result_metadata)
    if "pdf_path" in metadata:
        metadata["pdf_path"] = rel(Path(metadata["pdf_path"]))
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the LlamaIndex Vector RAG baseline for FinanceBench MVP questions.")
    parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS)
    parser.add_argument("--pdf-dir", type=Path, default=DEFAULT_PDF_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--question-id", action="append", help="Run only the given question id. Can be repeated.")
    parser.add_argument("--model", default=None, help="LiteLLM model name used for answer generation.")
    parser.add_argument("--no-llm", action="store_true", help="Only run LlamaIndex vector retrieval.")
    parser.add_argument("--embed-model", default=DEFAULT_EMBED_MODEL)
    parser.add_argument("--chunk-size", type=int, default=DEFAULT_CHUNK_SIZE)
    parser.add_argument("--chunk-overlap", type=int, default=DEFAULT_CHUNK_OVERLAP)
    parser.add_argument("--retrieve-top-k", type=int, default=DEFAULT_RETRIEVE_TOP_K)
    parser.add_argument("--rerank-top-k", type=int, default=DEFAULT_RERANK_TOP_K)
    parser.add_argument("--max-citations", type=int, default=DEFAULT_MAX_CITATIONS)
    parser.add_argument(
        "--disable-finance-rerank",
        action="store_true",
        help="Disable the label-free finance line-item boost and run the generic reranker only.",
    )
    parser.add_argument(
        "--answer-prompt-mode",
        choices=SUPPORTED_ANSWER_PROMPT_MODES,
        default=DEFAULT_ANSWER_PROMPT_MODE,
        help="Answer-generation prompt template. Default preserves the historical baseline prompt.",
    )
    parser.add_argument("--force", action="store_true", help="Re-run questions even if the output JSON already exists.")
    parser.add_argument("--continue-on-error", action="store_true")
    args = parser.parse_args()

    questions = load_questions(args.questions)
    if args.question_id:
        requested = set(args.question_id)
        questions = [q for q in questions if q.question_id in requested]
        missing = sorted(requested - {q.question_id for q in questions})
        if missing:
            raise SystemExit(f"Requested question_id not found in MVP questions: {missing}")

    if not args.no_llm and not args.model:
        raise SystemExit("--model is required unless --no-llm is set.")
    if not args.no_llm and not has_model_key():
        raise SystemExit("No model API key found in the current shell.")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest: list[dict[str, Any]] = []

    for question in questions:
        output_path = args.output_dir / f"{question.question_id}.json"
        pdf_path = args.pdf_dir / f"{question.doc_name}.pdf"

        if output_path.exists() and not args.force:
            manifest.append(
                {
                    "question_id": question.question_id,
                    "doc_name": question.doc_name,
                    "status": "exists",
                    "output_path": rel(output_path),
                    "size_bytes": output_path.stat().st_size,
                }
            )
            continue

        started = time.perf_counter()
        try:
            if not pdf_path.exists():
                raise FileNotFoundError(f"Missing PDF: {pdf_path}")
            result = run_llamaindex_vector_rag_qa(
                question,
                pdf_path,
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
            result.metadata = compact_result_metadata(result.metadata)
            output_path.write_text(result.model_dump_json(indent=2) + "\n", encoding="utf-8")
            manifest.append(
                {
                    "question_id": question.question_id,
                    "doc_name": question.doc_name,
                    "status": "generated",
                    "output_path": rel(output_path),
                    "pdf_path": rel(pdf_path),
                    "citation_count": len(result.citations),
                    "selected_pages_one_indexed": [citation.page for citation in result.citations],
                    "embedding_model": args.embed_model,
                    "chunk_size": args.chunk_size,
                    "chunk_overlap": args.chunk_overlap,
                    "retrieve_top_k": args.retrieve_top_k,
                    "rerank_top_k": args.rerank_top_k,
                    "max_citations": args.max_citations,
                    "finance_rerank": not args.disable_finance_rerank,
                    "answer_prompt_mode": args.answer_prompt_mode,
                    "answer_context_chunk_count": result.metadata.get("answer_context_chunk_count"),
                    "answer_context_chars": result.metadata.get("answer_context_chars"),
                    "answer_context_words": result.metadata.get("answer_context_words"),
                    "latency_ms": int((time.perf_counter() - started) * 1000),
                    "llm_enabled": not args.no_llm,
                    "model": args.model,
                }
            )
        except Exception as exc:
            manifest.append(
                {
                    "question_id": question.question_id,
                    "doc_name": question.doc_name,
                    "status": "failed",
                    "latency_ms": int((time.perf_counter() - started) * 1000),
                    "error": str(exc),
                }
            )
            if not args.continue_on_error:
                args.manifest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
                raise

    args.manifest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    generated = sum(1 for row in manifest if row["status"] == "generated")
    exists = sum(1 for row in manifest if row["status"] == "exists")
    failed = sum(1 for row in manifest if row["status"] == "failed")
    print(f"LlamaIndex Vector RAG outputs: {args.output_dir}")
    print(f"LlamaIndex Vector RAG manifest: {args.manifest}")
    print(f"generated={generated} exists={exists} failed={failed}")


if __name__ == "__main__":
    main()
