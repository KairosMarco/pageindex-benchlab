from __future__ import annotations

import argparse
import json
import sys
import uuid
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from benchlab.schemas import BenchmarkQuestion  # noqa: E402

DEFAULT_QUESTIONS = ROOT / "datasets" / "financebench" / "expanded_questions_25.jsonl"
DEFAULT_PDF_DIR = ROOT / "datasets" / "raw" / "financebench" / "pdfs"
DEFAULT_OUTPUT = ROOT / "datasets" / "bookrag" / "financebench_expanded_25.json"
DEFAULT_MAPPING = ROOT / "datasets" / "bookrag" / "financebench_expanded_25_mapping.json"


def read_questions(path: Path) -> list[BenchmarkQuestion]:
    questions: list[BenchmarkQuestion] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            questions.append(BenchmarkQuestion.model_validate_json(line))
        except Exception as exc:
            raise ValueError(f"Invalid question JSONL at {path}:{line_number}: {exc}") from exc
    return questions


def stable_doc_uuid(document_id: str) -> str:
    """Create a stable document-level UUID for BookRAG dataset records."""

    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"pageindex-benchlab/financebench/{document_id}"))


def pdf_path_for_question(question: BenchmarkQuestion, pdf_dir: Path) -> Path:
    return pdf_dir / f"{question.doc_name}.pdf"


def build_bookrag_records(
    questions: list[BenchmarkQuestion],
    pdf_dir: Path,
    allow_missing_pdfs: bool,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    records: list[dict[str, Any]] = []
    question_mappings: list[dict[str, Any]] = []
    document_mappings: dict[str, dict[str, Any]] = {}
    missing_pdfs: list[str] = []

    for question in questions:
        pdf_path = pdf_path_for_question(question, pdf_dir)
        if not pdf_path.exists():
            missing_pdfs.append(str(pdf_path))
            if not allow_missing_pdfs:
                continue

        doc_uuid = stable_doc_uuid(question.doc_name)
        records.append(
            {
                "question": question.question,
                "answer": question.gold_answer,
                "doc_uuid": doc_uuid,
                "doc_path": str(pdf_path.resolve()),
            }
        )
        question_mappings.append(
            {
                "question_id": question.question_id,
                "source_id": question.source_id,
                "doc_uuid": doc_uuid,
                "doc_name": question.doc_name,
                "doc_path": str(pdf_path.resolve()),
                "gold_answer": question.gold_answer,
                "gold_pages_one_indexed": [item.page_one_indexed for item in question.gold_evidence],
                "gold_pages_zero_indexed": [item.page_zero_indexed for item in question.gold_evidence],
                "question_type": question.question_type,
                "question_reasoning": question.question_reasoning,
            }
        )
        document_mappings.setdefault(
            doc_uuid,
            {
                "doc_uuid": doc_uuid,
                "doc_name": question.doc_name,
                "company": question.company,
                "doc_type": question.doc_type,
                "doc_period": question.doc_period,
                "doc_path": str(pdf_path.resolve()),
                "question_ids": [],
            },
        )
        document_mappings[doc_uuid]["question_ids"].append(question.question_id)

    mapping = {
        "source_questions": "",
        "pdf_dir": str(pdf_dir.resolve()),
        "record_count": len(records),
        "question_count": len(questions),
        "document_count": len(document_mappings),
        "missing_pdfs": missing_pdfs,
        "documents": sorted(document_mappings.values(), key=lambda item: item["doc_name"]),
        "questions": question_mappings,
    }
    return records, mapping


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert BenchLab FinanceBench JSONL to BookRAG dataset JSON.")
    parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS)
    parser.add_argument("--pdf-dir", type=Path, default=DEFAULT_PDF_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--mapping", type=Path, default=DEFAULT_MAPPING)
    parser.add_argument(
        "--allow-missing-pdfs",
        action="store_true",
        help="Write records even when source PDFs are missing. Useful for planning-only manifests.",
    )
    args = parser.parse_args()

    questions = read_questions(args.questions)
    records, mapping = build_bookrag_records(
        questions=questions,
        pdf_dir=args.pdf_dir,
        allow_missing_pdfs=args.allow_missing_pdfs,
    )
    mapping["source_questions"] = str(args.questions.resolve())

    if mapping["missing_pdfs"] and not args.allow_missing_pdfs:
        missing = "\n".join(mapping["missing_pdfs"])
        raise FileNotFoundError(
            "Missing source PDFs. Run scripts\\download_mvp_pdfs.py for the selected question set "
            f"or use --allow-missing-pdfs for a planning manifest.\n{missing}"
        )

    write_json(args.output, records)
    write_json(args.mapping, mapping)

    print(f"BookRAG dataset: {args.output}")
    print(f"BookRAG mapping: {args.mapping}")
    print(f"records={len(records)} documents={mapping['document_count']} missing_pdfs={len(mapping['missing_pdfs'])}")


if __name__ == "__main__":
    main()
