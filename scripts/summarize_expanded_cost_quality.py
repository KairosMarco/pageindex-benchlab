from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_JSON = ROOT / "reports" / "expanded_cost_quality_summary.json"
DEFAULT_OUTPUT_MD = ROOT / "reports" / "expanded_cost_quality_summary.md"


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def rounded(value: float | None, digits: int = 3) -> float | None:
    return round(value, digits) if value is not None else None


def format_value(value: Any, digits: int = 3) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def issue_ids(rows: list[dict[str, Any]]) -> list[str]:
    return sorted({row["question_id"] for row in rows if row.get("question_id")})


def load_llamaindex_rows(path: Path) -> list[dict[str, Any]]:
    payload = load_json(path)
    rows = []
    for method in payload.get("methods", []):
        rows.append(
            {
                "key": method["method"],
                "label": method["label"],
                "source_report": rel(path),
                "question_count": method["result_count"],
                "mechanical_gate_passed": method["mechanical_gate_passed"],
                "generation_failure_count": method["generation_failure_count"],
                "evaluation_failure_count": method["evaluation_failure_count"],
                "average_evidence_recall": method["average_evidence_recall"],
                "average_citation_precision": method["average_citation_precision"],
                "answer_accuracy": method["answer_accuracy"],
                "average_answer_score": method["average_answer_score"],
                "answer_verdict_counts": method["answer_verdict_counts"],
                "average_total_tokens": method["average_total_tokens"],
                "median_total_tokens": method["median_total_tokens"],
                "total_tokens": method["total_tokens"],
                "average_latency_ms": method["average_latency_ms"],
                "median_latency_ms": method["median_latency_ms"],
                "average_context_words": method.get("average_context_words"),
                "answer_issue_ids": issue_ids(method.get("answer_issue_rows", [])),
                "evidence_issue_ids": issue_ids(method.get("evidence_issue_rows", [])),
            }
        )
    return rows


def load_long_context_row(path: Path) -> dict[str, Any]:
    payload = load_json(path)
    summary = payload["summary"]
    return {
        "key": "long_context",
        "label": summary["label"],
        "source_report": rel(path),
        "question_count": summary["result_count"],
        "mechanical_gate_passed": summary["mechanical_gate_passed"],
        "generation_failure_count": summary["generation_failure_count"],
        "evaluation_failure_count": summary["evaluation_failure_count"],
        "average_evidence_recall": summary["average_evidence_recall"],
        "average_citation_precision": summary["average_citation_precision"],
        "answer_accuracy": summary["answer_accuracy"],
        "average_answer_score": summary["average_answer_score"],
        "answer_verdict_counts": summary["answer_verdict_counts"],
        "average_total_tokens": summary["average_total_tokens"],
        "median_total_tokens": summary["median_total_tokens"],
        "total_tokens": summary["total_tokens"],
        "average_latency_ms": summary["average_latency_ms"],
        "median_latency_ms": summary["median_latency_ms"],
        "average_context_chars": summary["average_context_chars"],
        "average_context_pages": summary["average_context_pages"],
        "answer_issue_ids": issue_ids(payload.get("answer_issue_rows", [])),
        "evidence_issue_ids": issue_ids(payload.get("evidence_issue_rows", [])),
    }


def add_relative_costs(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    token_values = [row.get("average_total_tokens") for row in rows if row.get("average_total_tokens")]
    latency_values = [row.get("average_latency_ms") for row in rows if row.get("average_latency_ms")]
    min_tokens = min(token_values) if token_values else None
    min_latency = min(latency_values) if latency_values else None
    enriched = []
    for row in rows:
        row = dict(row)
        row["token_multiplier_vs_lowest"] = rounded(
            (row["average_total_tokens"] / min_tokens) if min_tokens and row.get("average_total_tokens") else None
        )
        row["latency_multiplier_vs_lowest"] = rounded(
            (row["average_latency_ms"] / min_latency) if min_latency and row.get("average_latency_ms") else None
        )
        enriched.append(row)
    return enriched


def shared_issue_sets(rows: list[dict[str, Any]]) -> dict[str, Any]:
    answer_issue_sets = {row["key"]: set(row["answer_issue_ids"]) for row in rows}
    evidence_issue_sets = {row["key"]: set(row["evidence_issue_ids"]) for row in rows}
    all_answer = sorted(set().union(*answer_issue_sets.values())) if answer_issue_sets else []
    all_evidence = sorted(set().union(*evidence_issue_sets.values())) if evidence_issue_sets else []
    common_answer = sorted(set.intersection(*answer_issue_sets.values())) if answer_issue_sets else []
    common_evidence = sorted(set.intersection(*evidence_issue_sets.values())) if evidence_issue_sets else []
    return {
        "all_answer_issue_ids": all_answer,
        "all_evidence_issue_ids": all_evidence,
        "common_answer_issue_ids": common_answer,
        "common_evidence_issue_ids": common_evidence,
        "per_method_answer_issue_ids": {key: sorted(value) for key, value in answer_issue_sets.items()},
        "per_method_evidence_issue_ids": {key: sorted(value) for key, value in evidence_issue_sets.items()},
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Expanded Cost and Quality Summary",
        "",
        f"Date: {payload['summary']['date']}",
        "",
        "## Scope",
        "",
        "This report compares committed expanded 25-question LLM artifacts. It does not run new model calls.",
        "",
        "## Summary Table",
        "",
        "| Method | Questions | Evidence recall | Citation precision | Answer accuracy | Avg tokens | Token x | Avg latency ms | Latency x | Answer issues | Evidence issues |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in payload["methods"]:
        lines.append(
            "| {label} | {questions} | {recall} | {precision} | {accuracy} | {tokens} | {token_x} | {latency} | {latency_x} | {answer_issues} | {evidence_issues} |".format(
                label=row["label"],
                questions=row["question_count"],
                recall=format_value(row["average_evidence_recall"]),
                precision=format_value(row["average_citation_precision"]),
                accuracy=format_value(row["answer_accuracy"]),
                tokens=format_value(row["average_total_tokens"]),
                token_x=format_value(row["token_multiplier_vs_lowest"]),
                latency=format_value(row["average_latency_ms"]),
                latency_x=format_value(row["latency_multiplier_vs_lowest"]),
                answer_issues=", ".join(row["answer_issue_ids"]) or "none",
                evidence_issues=", ".join(row["evidence_issue_ids"]) or "none",
            )
        )

    issue_summary = payload["issue_summary"]
    lines.extend(
        [
            "",
            "## Issue Overlap",
            "",
            f"- Answer issue union: `{', '.join(issue_summary['all_answer_issue_ids']) or 'none'}`",
            f"- Answer issue intersection: `{', '.join(issue_summary['common_answer_issue_ids']) or 'none'}`",
            f"- Evidence issue union: `{', '.join(issue_summary['all_evidence_issue_ids']) or 'none'}`",
            f"- Evidence issue intersection: `{', '.join(issue_summary['common_evidence_issue_ids']) or 'none'}`",
            "",
            "## Interpretation",
            "",
            "- LlamaIndex Vector and Long-context both reached `0.920` answer accuracy on the expanded subset.",
            "- LlamaIndex Vector used the fewest average tokens and preserved `1.000` evidence recall.",
            "- Long-context used about `36x` more average tokens than the lowest-token candidate while producing lower citation evidence recall.",
            "- `fb_exp_020` is the shared answer failure across all compared methods and should be treated as a high-value reasoning prompt or benchmark-analysis case.",
            "- These results still do not establish broad PageIndex superiority; PageIndex expanded QA has not yet been run on this 25-question subset.",
            "",
            "## Source Reports",
            "",
        ]
    )
    for row in payload["methods"]:
        lines.append(f"- {row['label']}: `{row['source_report']}`")
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize expanded LLM cost and quality across methods.")
    parser.add_argument(
        "--llamaindex-json",
        type=Path,
        default=ROOT / "reports" / "llamaindex_expanded_llm_diagnostics.json",
    )
    parser.add_argument(
        "--long-context-json",
        type=Path,
        default=ROOT / "reports" / "long_context_expanded_llm_diagnostics.json",
    )
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    args = parser.parse_args()

    rows = load_llamaindex_rows(args.llamaindex_json)
    rows.append(load_long_context_row(args.long_context_json))
    rows = add_relative_costs(rows)
    payload = {
        "summary": {
            "date": date.today().isoformat(),
            "method_count": len(rows),
            "question_count": rows[0]["question_count"] if rows else 0,
        },
        "methods": rows,
        "issue_summary": shared_issue_sets(rows),
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text(render_markdown(payload), encoding="utf-8")
    print(f"Expanded cost/quality JSON: {args.output_json}")
    print(f"Expanded cost/quality report: {args.output_md}")


if __name__ == "__main__":
    main()
