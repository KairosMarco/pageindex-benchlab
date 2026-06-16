from __future__ import annotations

import argparse
import json
import statistics
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchlab.schemas import BenchmarkQuestion, BenchmarkResult  # noqa: E402


DEFAULT_QUESTIONS = ROOT / "datasets" / "financebench" / "mvp_questions.jsonl"
DEFAULT_REPORT_JSON = ROOT / "reports" / "stage1_detailed_evidence_report.json"
DEFAULT_OUTPUT = ROOT / "reports" / "stage1_validation_report.json"


@dataclass(frozen=True)
class MethodConfig:
    key: str
    label: str
    results_dir: Path
    evidence_eval: Path
    answer_eval: Path


DEFAULT_METHODS = [
    MethodConfig(
        key="pageindex",
        label="PageIndex",
        results_dir=ROOT / "reports" / "pageindex" / "qa_llm",
        evidence_eval=ROOT / "reports" / "pageindex" / "evidence_eval_llm.json",
        answer_eval=ROOT / "reports" / "pageindex" / "answer_eval_llm.json",
    ),
    MethodConfig(
        key="long_context",
        label="Long-context",
        results_dir=ROOT / "reports" / "long_context" / "qa_llm",
        evidence_eval=ROOT / "reports" / "long_context" / "evidence_eval_llm.json",
        answer_eval=ROOT / "reports" / "long_context" / "answer_eval_llm.json",
    ),
    MethodConfig(
        key="vector_rag",
        label="Vector RAG + reranker",
        results_dir=ROOT / "reports" / "vector_rag" / "qa_llm",
        evidence_eval=ROOT / "reports" / "vector_rag" / "evidence_eval_llm.json",
        answer_eval=ROOT / "reports" / "vector_rag" / "answer_eval_llm.json",
    ),
    MethodConfig(
        key="hybrid_rag",
        label="Hybrid RAG",
        results_dir=ROOT / "reports" / "hybrid_rag" / "qa_llm",
        evidence_eval=ROOT / "reports" / "hybrid_rag" / "evidence_eval_llm.json",
        answer_eval=ROOT / "reports" / "hybrid_rag" / "answer_eval_llm.json",
    ),
]


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_questions(path: Path) -> dict[str, BenchmarkQuestion]:
    questions: dict[str, BenchmarkQuestion] = {}
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                question = BenchmarkQuestion.model_validate_json(line)
                questions[question.question_id] = question
    return questions


def load_results(results_dir: Path) -> dict[str, BenchmarkResult]:
    return {
        path.stem: BenchmarkResult.model_validate_json(path.read_text(encoding="utf-8"))
        for path in sorted(results_dir.glob("*.json"))
    }


def index_rows(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["question_id"]: row for row in payload.get("per_question", [])}


def close_enough(left: float, right: float, tolerance: float = 1e-9) -> bool:
    return abs(left - right) <= tolerance


def assert_condition(checks: list[dict[str, Any]], name: str, condition: bool, details: dict[str, Any] | None = None) -> None:
    checks.append(
        {
            "name": name,
            "status": "pass" if condition else "fail",
            "details": details or {},
        }
    )


def validate_method(config: MethodConfig, expected_question_ids: set[str], checks: list[dict[str, Any]]) -> dict[str, Any]:
    results = load_results(config.results_dir)
    evidence = load_json(config.evidence_eval)
    answer = load_json(config.answer_eval)
    evidence_by_question = index_rows(evidence)
    answer_by_question = index_rows(answer)

    result_ids = set(results)
    evidence_ids = set(evidence_by_question)
    answer_ids = set(answer_by_question)
    assert_condition(
        checks,
        f"{config.key}: result count matches question count",
        result_ids == expected_question_ids,
        {"missing": sorted(expected_question_ids - result_ids), "extra": sorted(result_ids - expected_question_ids)},
    )
    assert_condition(
        checks,
        f"{config.key}: evidence eval covers all questions",
        evidence_ids == expected_question_ids,
        {"missing": sorted(expected_question_ids - evidence_ids), "extra": sorted(evidence_ids - expected_question_ids)},
    )
    assert_condition(
        checks,
        f"{config.key}: answer eval covers all questions",
        answer_ids == expected_question_ids,
        {"missing": sorted(expected_question_ids - answer_ids), "extra": sorted(answer_ids - expected_question_ids)},
    )

    recalls = [row["evidence_recall"] for row in evidence_by_question.values()]
    precisions = [row["citation_precision"] for row in evidence_by_question.values()]
    answer_scores = [row["score"] for row in answer_by_question.values()]
    total_tokens = [result.token_usage.total for result in results.values()]
    latencies = [result.latency_ms for result in results.values()]

    assert_condition(
        checks,
        f"{config.key}: no missing token usage",
        all(value is not None for value in total_tokens),
        {"missing_question_ids": sorted(qid for qid, result in results.items() if result.token_usage.total is None)},
    )
    assert_condition(
        checks,
        f"{config.key}: no missing latency",
        all(value is not None for value in latencies),
        {"missing_question_ids": sorted(qid for qid, result in results.items() if result.latency_ms is None)},
    )

    evidence_summary = evidence["summary"]
    answer_summary = answer["summary"]
    computed_recall = statistics.mean(recalls)
    computed_precision = statistics.mean(precisions)
    computed_accuracy = sum(1 for row in answer_by_question.values() if row["verdict"] == "correct") / len(answer_by_question)
    computed_answer_score = statistics.mean(answer_scores)

    assert_condition(
        checks,
        f"{config.key}: evidence recall summary matches per-question rows",
        close_enough(computed_recall, evidence_summary["average_evidence_recall"]),
        {"computed": computed_recall, "summary": evidence_summary["average_evidence_recall"]},
    )
    assert_condition(
        checks,
        f"{config.key}: citation precision summary matches per-question rows",
        close_enough(computed_precision, evidence_summary["average_citation_precision"]),
        {"computed": computed_precision, "summary": evidence_summary["average_citation_precision"]},
    )
    assert_condition(
        checks,
        f"{config.key}: answer accuracy summary matches per-question rows",
        close_enough(computed_accuracy, answer_summary["accuracy"]),
        {"computed": computed_accuracy, "summary": answer_summary["accuracy"]},
    )
    assert_condition(
        checks,
        f"{config.key}: answer score summary matches per-question rows",
        close_enough(computed_answer_score, answer_summary["average_answer_score"]),
        {"computed": computed_answer_score, "summary": answer_summary["average_answer_score"]},
    )

    return {
        "key": config.key,
        "label": config.label,
        "result_count": len(results),
        "evidence_eval": rel(config.evidence_eval),
        "answer_eval": rel(config.answer_eval),
        "computed_average_evidence_recall": computed_recall,
        "computed_average_citation_precision": computed_precision,
        "computed_answer_accuracy": computed_accuracy,
        "computed_average_answer_score": computed_answer_score,
    }


def validate_detailed_report(report_path: Path, expected_question_ids: set[str], checks: list[dict[str, Any]]) -> dict[str, Any]:
    report = load_json(report_path)
    records = report.get("records", [])
    expected_record_count = len(expected_question_ids) * len(DEFAULT_METHODS)
    assert_condition(
        checks,
        "detailed report record count matches questions x methods",
        len(records) == expected_record_count,
        {"expected": expected_record_count, "actual": len(records)},
    )

    seen_pairs = {(row["question_id"], row["method_key"]) for row in records}
    expected_pairs = {
        (question_id, method.key)
        for question_id in expected_question_ids
        for method in DEFAULT_METHODS
    }
    assert_condition(
        checks,
        "detailed report covers every question-method pair",
        seen_pairs == expected_pairs,
        {"missing": sorted(expected_pairs - seen_pairs), "extra": sorted(seen_pairs - expected_pairs)},
    )

    vector_boeing = [
        row
        for row in records
        if row["question_id"] == "fb_mvp_006" and row["method_key"] == "vector_rag"
    ]
    assert_condition(
        checks,
        "known Vector RAG Boeing failure is preserved",
        bool(vector_boeing)
        and vector_boeing[0]["evidence_recall"] == 1.0
        and vector_boeing[0]["answer_verdict"] == "incorrect",
        {"record": vector_boeing[0] if vector_boeing else None},
    )
    return {
        "record_count": len(records),
        "failure_or_risk_count": report.get("summary", {}).get("failure_or_risk_count"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Stage 1 benchmark artifacts.")
    parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS)
    parser.add_argument("--detailed-report-json", type=Path, default=DEFAULT_REPORT_JSON)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    checks: list[dict[str, Any]] = []
    questions = load_questions(args.questions)
    expected_question_ids = set(questions)
    method_summaries = [
        validate_method(config, expected_question_ids, checks)
        for config in DEFAULT_METHODS
    ]
    detailed_report_summary = validate_detailed_report(args.detailed_report_json, expected_question_ids, checks)

    failed = [check for check in checks if check["status"] != "pass"]
    payload = {
        "summary": {
            "status": "pass" if not failed else "fail",
            "question_count": len(questions),
            "method_count": len(DEFAULT_METHODS),
            "check_count": len(checks),
            "failed_check_count": len(failed),
        },
        "method_summaries": method_summaries,
        "detailed_report_summary": detailed_report_summary,
        "checks": checks,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Validation report: {args.output}")
    print(f"status={payload['summary']['status']} checks={len(checks)} failed={len(failed)}")
    if failed:
        for check in failed:
            print(f"FAILED: {check['name']}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
