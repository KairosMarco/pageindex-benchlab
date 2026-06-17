from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DIAGNOSTICS = ROOT / "reports" / "llamaindex_expanded_llm_diagnostics.json"
DEFAULT_OUTPUT = ROOT / "reports" / "expanded_llm_validation_report.json"


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


def close_to_one(value: Any) -> bool:
    return isinstance(value, (int, float)) and value >= 0.999


def add_check(checks: list[Check], name: str, passed: bool, **details: Any) -> None:
    checks.append(Check(name=name, passed=passed, details=details))


def validate_method(checks: list[Check], method: dict[str, Any], expected_question_count: int) -> None:
    label = method.get("label", method.get("method", "unknown"))
    add_check(
        checks,
        f"{label}: result count",
        method.get("result_count") == expected_question_count,
        expected=expected_question_count,
        actual=method.get("result_count"),
    )
    add_check(
        checks,
        f"{label}: manifest count",
        method.get("manifest_count") == expected_question_count,
        expected=expected_question_count,
        actual=method.get("manifest_count"),
    )
    add_check(
        checks,
        f"{label}: generation failures",
        method.get("generation_failure_count") == 0,
        actual=method.get("generation_failure_count"),
    )
    add_check(
        checks,
        f"{label}: evaluation failures",
        method.get("evaluation_failure_count") == 0,
        actual=method.get("evaluation_failure_count"),
    )
    add_check(
        checks,
        f"{label}: evidence recall",
        close_to_one(method.get("average_evidence_recall")),
        actual=method.get("average_evidence_recall"),
    )
    add_check(
        checks,
        f"{label}: citation precision present",
        isinstance(method.get("average_citation_precision"), (int, float)),
        actual=method.get("average_citation_precision"),
    )
    add_check(
        checks,
        f"{label}: answer accuracy present",
        isinstance(method.get("answer_accuracy"), (int, float)),
        actual=method.get("answer_accuracy"),
    )
    verdict_counts = method.get("answer_verdict_counts") or {}
    add_check(
        checks,
        f"{label}: answer verdict count",
        sum(verdict_counts.values()) == expected_question_count,
        expected=expected_question_count,
        actual=sum(verdict_counts.values()),
        verdict_counts=verdict_counts,
    )
    add_check(
        checks,
        f"{label}: token usage complete",
        bool(method.get("token_usage_complete")),
        token_usage_count=method.get("token_usage_count"),
        expected=expected_question_count,
    )
    add_check(
        checks,
        f"{label}: latency complete",
        bool(method.get("latency_complete")),
        latency_count=method.get("latency_count"),
        expected=expected_question_count,
    )
    add_check(
        checks,
        f"{label}: mechanical gate",
        bool(method.get("mechanical_gate_passed")),
        status=method.get("status"),
    )
    add_check(
        checks,
        f"{label}: per-question rows",
        len(method.get("per_question") or []) == expected_question_count,
        expected=expected_question_count,
        actual=len(method.get("per_question") or []),
    )
    for artifact_key in ("results_dir", "manifest", "evidence_eval", "answer_eval"):
        artifact = ROOT / str(method.get(artifact_key, ""))
        add_check(
            checks,
            f"{label}: artifact exists {artifact_key}",
            artifact.exists(),
            path=rel(artifact),
        )


def validate(diagnostics_path: Path, expected_question_count: int) -> dict[str, Any]:
    checks: list[Check] = []
    add_check(checks, "diagnostics file exists", diagnostics_path.exists(), path=rel(diagnostics_path))
    if not diagnostics_path.exists():
        return {
            "status": "fail",
            "check_count": len(checks),
            "failed_check_count": sum(1 for check in checks if not check.passed),
            "checks": [check.__dict__ for check in checks],
        }

    diagnostics = load_json(diagnostics_path)
    methods = diagnostics.get("methods", [])
    summary = diagnostics.get("summary", {})
    add_check(
        checks,
        "summary question count",
        summary.get("question_count") == expected_question_count,
        expected=expected_question_count,
        actual=summary.get("question_count"),
    )
    add_check(checks, "method count", len(methods) >= 1, actual=len(methods))
    add_check(
        checks,
        "summary mechanical gate",
        bool(summary.get("mechanical_gate_passed")),
        actual=summary.get("mechanical_gate_passed"),
    )
    methods_present = sorted(method.get("method") for method in methods if method.get("method"))
    required_methods = ["hybrid", "vector"]
    add_check(
        checks,
        "required methods present",
        all(method in methods_present for method in required_methods),
        required=required_methods,
        actual=methods_present,
    )

    for method in methods:
        validate_method(checks, method, expected_question_count)

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
    parser = argparse.ArgumentParser(description="Validate expanded LlamaIndex LLM diagnostics artifacts.")
    parser.add_argument("--diagnostics-json", type=Path, default=DEFAULT_DIAGNOSTICS)
    parser.add_argument("--expected-question-count", type=int, default=25)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    payload = validate(args.diagnostics_json, args.expected_question_count)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        "Expanded LLM validation: status={status} checks={check_count} failed={failed_check_count}".format(
            **payload
        )
    )
    print(f"Validation report: {args.output}")
    if payload["status"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
