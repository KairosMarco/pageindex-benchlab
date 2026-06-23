from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchlab.schemas import BenchmarkQuestion  # noqa: E402
from pipelines.structured_rag.adapter import (  # noqa: E402
    DEFAULT_ENTITY_TOP_K,
    DEFAULT_MAX_CITATIONS,
    DEFAULT_NODE_OVERLAP,
    DEFAULT_NODE_WORDS,
    DEFAULT_RETRIEVE_TOP_K,
    run_structured_rag_qa,
)


DEFAULT_QUESTIONS = ROOT / "datasets" / "financebench" / "mvp_questions.jsonl"
DEFAULT_PDF_DIR = ROOT / "datasets" / "raw" / "financebench" / "pdfs"
DEFAULT_OUTPUT_DIR = ROOT / "reports" / "structured_rag" / "qa_smoke"
DEFAULT_MANIFEST = ROOT / "reports" / "structured_rag" / "qa_smoke_manifest.json"


def load_questions(path: Path) -> list[BenchmarkQuestion]:
    with path.open(encoding="utf-8") as handle:
        return [BenchmarkQuestion.model_validate_json(line) for line in handle if line.strip()]


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def compact_result_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    compacted = dict(metadata)
    if "pdf_path" in compacted:
        compacted["pdf_path"] = rel(Path(compacted["pdf_path"]))
    return compacted


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the structured tree-graph RAG baseline.")
    parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS)
    parser.add_argument("--pdf-dir", type=Path, default=DEFAULT_PDF_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--question-id", action="append", help="Run only the given question id. Can be repeated.")
    parser.add_argument("--node-words", type=int, default=DEFAULT_NODE_WORDS)
    parser.add_argument("--node-overlap", type=int, default=DEFAULT_NODE_OVERLAP)
    parser.add_argument("--retrieve-top-k", type=int, default=DEFAULT_RETRIEVE_TOP_K)
    parser.add_argument("--entity-top-k", type=int, default=DEFAULT_ENTITY_TOP_K)
    parser.add_argument("--max-citations", type=int, default=DEFAULT_MAX_CITATIONS)
    parser.add_argument("--force", action="store_true", help="Re-run questions even if the output JSON already exists.")
    parser.add_argument("--continue-on-error", action="store_true")
    args = parser.parse_args()

    questions = load_questions(args.questions)
    if args.question_id:
        requested = set(args.question_id)
        questions = [question for question in questions if question.question_id in requested]
        missing = sorted(requested - {question.question_id for question in questions})
        if missing:
            raise SystemExit(f"Requested question_id not found: {missing}")

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
            result = run_structured_rag_qa(
                question,
                pdf_path,
                max_citations=args.max_citations,
                node_words=args.node_words,
                node_overlap=args.node_overlap,
                retrieve_top_k=args.retrieve_top_k,
                entity_top_k=args.entity_top_k,
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
                    "node_count": result.metadata.get("node_count"),
                    "entity_count": result.metadata.get("entity_count"),
                    "edge_count": result.metadata.get("edge_count"),
                    "node_words": args.node_words,
                    "node_overlap": args.node_overlap,
                    "retrieve_top_k": args.retrieve_top_k,
                    "entity_top_k": args.entity_top_k,
                    "max_citations": args.max_citations,
                    "latency_ms": int((time.perf_counter() - started) * 1000),
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
    print(f"Structured RAG outputs: {args.output_dir}")
    print(f"Structured RAG manifest: {args.manifest}")
    print(f"generated={generated} exists={exists} failed={failed}")


if __name__ == "__main__":
    main()
