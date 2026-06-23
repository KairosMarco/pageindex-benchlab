from __future__ import annotations

from pathlib import Path

from benchlab.schemas import BenchmarkQuestion, GoldEvidence
from scripts.build_bookrag_dataset import build_bookrag_records, stable_doc_uuid


def make_question(question_id: str, doc_name: str) -> BenchmarkQuestion:
    return BenchmarkQuestion(
        question_id=question_id,
        source_id=f"source_{question_id}",
        dataset="financebench",
        company="ExampleCo",
        doc_name=doc_name,
        doc_type="10k",
        doc_period=2024,
        question=f"What is the answer for {question_id}?",
        gold_answer="42",
        gold_evidence=[
            GoldEvidence(
                document_id=doc_name,
                page_zero_indexed=2,
                page_one_indexed=3,
                text="Evidence text",
            )
        ],
    )


def test_stable_doc_uuid_is_document_level() -> None:
    assert stable_doc_uuid("EXAMPLE_10K") == stable_doc_uuid("EXAMPLE_10K")
    assert stable_doc_uuid("EXAMPLE_10K") != stable_doc_uuid("OTHER_10K")


def test_build_bookrag_records_preserves_question_mapping(tmp_path: Path) -> None:
    pdf_dir = tmp_path / "pdfs"
    pdf_dir.mkdir()
    (pdf_dir / "EXAMPLE_10K.pdf").write_bytes(b"%PDF-1.4")
    questions = [
        make_question("q1", "EXAMPLE_10K"),
        make_question("q2", "EXAMPLE_10K"),
    ]

    records, mapping = build_bookrag_records(
        questions=questions,
        pdf_dir=pdf_dir,
        allow_missing_pdfs=False,
    )

    assert len(records) == 2
    assert records[0]["question"] == "What is the answer for q1?"
    assert records[0]["answer"] == "42"
    assert records[0]["doc_uuid"] == records[1]["doc_uuid"]
    assert records[0]["doc_path"].endswith("EXAMPLE_10K.pdf")
    assert mapping["record_count"] == 2
    assert mapping["document_count"] == 1
    assert mapping["questions"][0]["question_id"] == "q1"
    assert mapping["questions"][0]["gold_pages_one_indexed"] == [3]


def test_build_bookrag_records_reports_missing_pdfs(tmp_path: Path) -> None:
    records, mapping = build_bookrag_records(
        questions=[make_question("q1", "MISSING_10K")],
        pdf_dir=tmp_path,
        allow_missing_pdfs=False,
    )

    assert records == []
    assert mapping["missing_pdfs"]
