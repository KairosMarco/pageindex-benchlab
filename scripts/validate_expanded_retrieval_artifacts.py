from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_QUESTIONS = ROOT / "datasets" / "financebench" / "expanded_questions_25.jsonl"
DEFAULT_PDF_MANIFEST = ROOT / "reports" / "expanded_25_pdf_manifest.json"
DEFAULT_BASELINE_REPORT = ROOT / "reports" / "llamaindex_expanded_retrieval.json"
DEFAULT_CONCEPT_REPORT = ROOT / "reports" / "llamaindex_expanded_retrieval_concept_v2.json"
DEFAULT_OUTPUT = ROOT / "reports" / "expanded_retrieval_validation_report.json"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def assert_condition(checks: list[dict[str, Any]], name: str, condition: bool, details: dict[str, Any] | None = None) -> None:
    checks.append(
        {
            "name": name,
            "status": "pass" if condition else "fail",
            "details": details or {},
        }
    )


def check_question_file(path: Path, checks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    questions = load_jsonl(path)
    question_ids = [row["question_id"] for row in questions]
    source_ids = [row["source_id"] for row in questions]
    doc_names = [row["doc_name"] for row in questions]
    assert_condition(checks, "expanded question count is 25", len(questions) == 25, {"actual": len(questions)})
    assert_condition(checks, "expanded question ids are unique", len(question_ids) == len(set(question_ids)))
    assert_condition(checks, "expanded source ids are unique", len(source_ids) == len(set(source_ids)))
    assert_condition(checks, "expanded question set includes original MVP ids", all(f"fb_mvp_{i:03d}" in question_ids for i in range(1, 13)))
    assert_condition(checks, "expanded question set has 24 unique docs", len(set(doc_names)) == 24, {"actual": len(set(doc_names))})
    return questions


def check_pdf_manifest(path: Path, questions: list[dict[str, Any]], checks: list[dict[str, Any]]) -> None:
    manifest = load_json(path)
    needed_docs = {row["doc_name"] for row in questions}
    manifest_docs = {row["doc_name"] for row in manifest}
    failed = [row for row in manifest if row.get("status") == "failed"]
    missing_hash = [row["doc_name"] for row in manifest if row.get("status") != "failed" and not row.get("sha256")]
    assert_condition(checks, "pdf manifest covers all expanded docs", manifest_docs == needed_docs, {"missing": sorted(needed_docs - manifest_docs), "extra": sorted(manifest_docs - needed_docs)})
    assert_condition(checks, "pdf manifest has no failed downloads", not failed, {"failed": failed})
    assert_condition(checks, "pdf manifest records hashes", not missing_hash, {"missing_hash": missing_hash})


def method_rows(report: dict[str, Any]) -> list[dict[str, Any]]:
    return report.get("methods", [])


def check_report_shape(report: dict[str, Any], expected_suffix: str | None, checks: list[dict[str, Any]], label: str) -> None:
    rows = method_rows(report)
    expected_pairs = {(method, rerank) for method in ("vector", "hybrid") for rerank in (3, 6, 12)}
    actual_pairs = {(row["method"], row["rerank_top_k"]) for row in rows}
    assert_condition(checks, f"{label}: has all method/rerank rows", actual_pairs == expected_pairs, {"missing": sorted(expected_pairs - actual_pairs), "extra": sorted(actual_pairs - expected_pairs)})
    assert_condition(checks, f"{label}: variant suffix matches", report["summary"].get("variant_suffix") == expected_suffix, {"actual": report["summary"].get("variant_suffix")})
    assert_condition(checks, f"{label}: every row covers 25 questions", all(row["question_count"] == 25 and row["result_count"] == 25 for row in rows))
    assert_condition(checks, f"{label}: no manifest failures", all(row["manifest_failure_count"] == 0 for row in rows))


def check_baseline_report(path: Path, checks: list[dict[str, Any]]) -> None:
    report = load_json(path)
    check_report_shape(report, None, checks, "baseline expanded retrieval")
    rows = method_rows(report)
    low_recall_rows = [row for row in rows if row["average_evidence_recall"] < 1.0]
    failures = report.get("failures", [])
    assert_condition(checks, "baseline expanded retrieval records recall failures", bool(low_recall_rows), {"low_recall_rows": low_recall_rows})
    assert_condition(checks, "baseline expanded retrieval records per-question failures", bool(failures), {"failure_count": len(failures)})


def check_concept_report(path: Path, checks: list[dict[str, Any]]) -> None:
    report = load_json(path)
    check_report_shape(report, "concept_v2", checks, "concept_v2 expanded retrieval")
    rows = method_rows(report)
    assert_condition(checks, "concept_v2 reaches full evidence recall", all(row["average_evidence_recall"] == 1.0 for row in rows))
    assert_condition(checks, "concept_v2 has no per-question failures", not report.get("failures"), {"failure_count": len(report.get("failures", []))})
    for method in ("vector", "hybrid"):
        method_rows_sorted = sorted([row for row in rows if row["method"] == method], key=lambda row: row["rerank_top_k"])
        r3 = next(row for row in method_rows_sorted if row["rerank_top_k"] == 3)
        larger = [row for row in method_rows_sorted if row["rerank_top_k"] in (6, 12)]
        assert_condition(
            checks,
            f"concept_v2 {method}: r3 has smallest context",
            all(r3["average_context_words"] < row["average_context_words"] for row in larger),
            {"r3": r3["average_context_words"], "larger": {row["rerank_top_k"]: row["average_context_words"] for row in larger}},
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate expanded FinanceBench retrieval artifacts.")
    parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS)
    parser.add_argument("--pdf-manifest", type=Path, default=DEFAULT_PDF_MANIFEST)
    parser.add_argument("--baseline-report", type=Path, default=DEFAULT_BASELINE_REPORT)
    parser.add_argument("--concept-report", type=Path, default=DEFAULT_CONCEPT_REPORT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    checks: list[dict[str, Any]] = []
    questions = check_question_file(args.questions, checks)
    check_pdf_manifest(args.pdf_manifest, questions, checks)
    check_baseline_report(args.baseline_report, checks)
    check_concept_report(args.concept_report, checks)

    failed = [check for check in checks if check["status"] != "pass"]
    payload = {
        "summary": {
            "status": "pass" if not failed else "fail",
            "check_count": len(checks),
            "failed_check_count": len(failed),
            "question_file": rel(args.questions),
            "pdf_manifest": rel(args.pdf_manifest),
            "baseline_report": rel(args.baseline_report),
            "concept_report": rel(args.concept_report),
        },
        "checks": checks,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Expanded retrieval validation report: {args.output}")
    print(f"status={payload['summary']['status']} checks={len(checks)} failed={len(failed)}")
    if failed:
        for check in failed:
            print(f"FAILED: {check['name']}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
