from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DIAGNOSTICS = ROOT / "reports" / "pageindex_expanded_llm_diagnostics.json"
DEFAULT_OUTPUT = ROOT / "reports" / "expanded_pageindex_llm_validation_report.json"


@dataclass
class Check:
    name: str
    passed: bool
    details: dict[str, Any] = field(default_factory=dict)


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def add_check(checks: list[Check], name: str, passed: bool, **details: Any) -> None:
    checks.append(Check(name=name, passed=passed, details=details))


def validate(diagnostics_path: Path, expected_question_count: int) -> dict[str, Any]:
    checks: list[Check] = []
    add_check(checks, "diagnostics file exists", diagnostics_path.exists(), path=rel(diagnostics_path))
    if not diagnostics_path.exists():
        return {
            "status": "fail",
            "diagnostics": rel(diagnostics_path),
            "expected_question_count": expected_question_count,
            "check_count": len(checks),
            "failed_check_count": sum(1 for check in checks if not check.passed),
            "checks": [check.__dict__ for check in checks],
        }

    diagnostics = load_json(diagnostics_path)
    summary = diagnostics.get("summary", {})
    add_check(
        checks,
        "method is PageIndex",
        summary.get("method") == "pageindex_tree_qa_llm",
        actual=summary.get("method"),
    )
    add_check(
        checks,
        "summary question count",
        summary.get("question_count") == expected_question_count,
        expected=expected_question_count,
        actual=summary.get("question_count"),
    )
    add_check(
        checks,
        "result count",
        summary.get("result_count") == expected_question_count,
        expected=expected_question_count,
        actual=summary.get("result_count"),
    )
    add_check(
        checks,
        "manifest count",
        summary.get("manifest_count") == expected_question_count,
        expected=expected_question_count,
        actual=summary.get("manifest_count"),
    )
    add_check(
        checks,
        "generation failures",
        summary.get("generation_failure_count") == 0,
        actual=summary.get("generation_failure_count"),
    )
    add_check(
        checks,
        "evaluation failures",
        summary.get("evaluation_failure_count") == 0,
        actual=summary.get("evaluation_failure_count"),
    )
    add_check(
        checks,
        "evidence recall present",
        isinstance(summary.get("average_evidence_recall"), (int, float)),
        actual=summary.get("average_evidence_recall"),
    )
    add_check(
        checks,
        "citation precision present",
        isinstance(summary.get("average_citation_precision"), (int, float)),
        actual=summary.get("average_citation_precision"),
    )
    add_check(
        checks,
        "answer accuracy present",
        isinstance(summary.get("answer_accuracy"), (int, float)),
        actual=summary.get("answer_accuracy"),
    )
    verdict_counts = summary.get("answer_verdict_counts") or {}
    add_check(
        checks,
        "answer verdict count",
        sum(verdict_counts.values()) == expected_question_count,
        expected=expected_question_count,
        actual=sum(verdict_counts.values()),
        verdict_counts=verdict_counts,
    )
    add_check(
        checks,
        "token usage complete",
        bool(summary.get("token_usage_complete")),
        token_usage_count=summary.get("token_usage_count"),
        expected=expected_question_count,
    )
    add_check(
        checks,
        "latency complete",
        bool(summary.get("latency_complete")),
        latency_count=summary.get("latency_count"),
        expected=expected_question_count,
    )
    add_check(
        checks,
        "selected page count present",
        isinstance(summary.get("average_selected_page_count"), (int, float))
        and summary.get("average_selected_page_count") > 0,
        actual=summary.get("average_selected_page_count"),
    )
    add_check(
        checks,
        "mechanical gate",
        bool(summary.get("mechanical_gate_passed")),
        status=summary.get("status"),
    )
    add_check(
        checks,
        "per-question rows",
        len(diagnostics.get("per_question") or []) == expected_question_count,
        expected=expected_question_count,
        actual=len(diagnostics.get("per_question") or []),
    )
    for artifact_key in ("results_dir", "manifest", "evidence_eval", "answer_eval"):
        artifact = ROOT / str(summary.get(artifact_key, ""))
        add_check(
            checks,
            f"artifact exists {artifact_key}",
            artifact.exists(),
            path=rel(artifact),
        )

    failed = [check for check in checks if not check.passed]
    return {
        "status": "pass" if not failed else "fail",
        "diagnostics": rel(diagnostics_path),
        "expected_question_count": expected_question_count,
        "check_count": len(checks),
        "failed_check_count": len(failed),
        "checks": [check.__dict__ for check in checks],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate expanded PageIndex LLM diagnostics artifacts.")
    parser.add_argument("--diagnostics-json", type=Path, default=DEFAULT_DIAGNOSTICS)
    parser.add_argument("--expected-question-count", type=int, default=25)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    payload = validate(args.diagnostics_json, args.expected_question_count)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        "Expanded PageIndex LLM validation: status={status} checks={check_count} failed={failed_check_count}".format(
            **payload
        )
    )
    print(f"Validation report: {args.output}")
    if payload["status"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
