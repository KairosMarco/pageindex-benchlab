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

from benchlab.schemas import BenchmarkResult  # noqa: E402


DEFAULT_OUTPUT_JSON = ROOT / "reports" / "stage1_metrics_summary.json"
DEFAULT_OUTPUT_MD = ROOT / "reports" / "stage1_metrics_summary.md"


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


def safe_mean(values: list[float]) -> float | None:
    return statistics.mean(values) if values else None


def safe_median(values: list[float]) -> float | None:
    return statistics.median(values) if values else None


def safe_sum(values: list[int]) -> int | None:
    return sum(values) if values else None


def round_or_none(value: float | None, digits: int = 3) -> float | None:
    return round(value, digits) if value is not None else None


def load_results(results_dir: Path) -> list[BenchmarkResult]:
    return [
        BenchmarkResult.model_validate_json(path.read_text(encoding="utf-8"))
        for path in sorted(results_dir.glob("*.json"))
    ]


def summarize_tokens(results: list[BenchmarkResult]) -> dict[str, Any]:
    input_tokens = [result.token_usage.input for result in results if result.token_usage.input is not None]
    output_tokens = [result.token_usage.output for result in results if result.token_usage.output is not None]
    total_tokens = [result.token_usage.total for result in results if result.token_usage.total is not None]
    latencies = [result.latency_ms for result in results if result.latency_ms is not None]

    # Keep total and per-question aggregates separate so cost and UX comparisons can use the right number.
    return {
        "total_input_tokens": safe_sum(input_tokens),
        "total_output_tokens": safe_sum(output_tokens),
        "total_tokens": safe_sum(total_tokens),
        "average_input_tokens": round_or_none(safe_mean([float(v) for v in input_tokens])),
        "average_output_tokens": round_or_none(safe_mean([float(v) for v in output_tokens])),
        "average_total_tokens": round_or_none(safe_mean([float(v) for v in total_tokens])),
        "median_total_tokens": round_or_none(safe_median([float(v) for v in total_tokens])),
        "average_latency_ms": round_or_none(safe_mean([float(v) for v in latencies])),
        "median_latency_ms": round_or_none(safe_median([float(v) for v in latencies])),
        "total_latency_ms": safe_sum(latencies),
        "missing_token_usage_count": sum(1 for result in results if result.token_usage.total is None),
        "missing_latency_count": sum(1 for result in results if result.latency_ms is None),
    }


def summarize_method(config: MethodConfig) -> dict[str, Any]:
    results = load_results(config.results_dir)
    evidence = load_json(config.evidence_eval)
    answer = load_json(config.answer_eval)
    token_latency = summarize_tokens(results)
    return {
        "key": config.key,
        "label": config.label,
        "result_count": len(results),
        "results_dir": rel(config.results_dir),
        "evidence_eval": rel(config.evidence_eval),
        "answer_eval": rel(config.answer_eval),
        "average_evidence_recall": evidence["summary"]["average_evidence_recall"],
        "average_citation_precision": evidence["summary"]["average_citation_precision"],
        "answer_accuracy": answer["summary"]["accuracy"],
        "average_answer_score": answer["summary"]["average_answer_score"],
        "answer_verdict_counts": answer["summary"]["verdict_counts"],
        **token_latency,
    }


def format_number(value: Any, digits: int = 3) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def render_markdown(methods: list[dict[str, Any]]) -> str:
    lines = [
        "# Stage 1 Metrics Summary",
        "",
        "Date: 2026-06-16",
        "",
        "## Scope",
        "",
        "This report aggregates evidence quality, answer accuracy, token usage, and latency for the current FinanceBench MVP LLM runs.",
        "",
        "All rows use 12 MVP questions unless otherwise noted.",
        "",
        "## Summary Table",
        "",
        "| Method | Questions | Evidence recall | Citation precision | Answer accuracy | Avg input tokens | Avg total tokens | Total tokens | Avg latency ms |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for method in methods:
        lines.append(
            "| {label} | {result_count} | {recall} | {precision} | {accuracy} | {avg_input} | {avg_total} | {total_tokens} | {avg_latency} |".format(
                label=method["label"],
                result_count=method["result_count"],
                recall=format_number(method["average_evidence_recall"]),
                precision=format_number(method["average_citation_precision"]),
                accuracy=format_number(method["answer_accuracy"]),
                avg_input=format_number(method["average_input_tokens"]),
                avg_total=format_number(method["average_total_tokens"]),
                total_tokens=format_number(method["total_tokens"], digits=0),
                avg_latency=format_number(method["average_latency_ms"]),
            )
        )

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- PageIndex, Vector RAG, and Hybrid RAG hit every gold evidence page in this 12-question MVP subset.",
            "- Long-context used far more input tokens because it sends full document text to the model.",
            "- Vector RAG matched PageIndex on page-level evidence but had one LLM-judge answer miss on `fb_mvp_006`.",
            "- Hybrid RAG matched PageIndex on page-level evidence and LLM-judge answer accuracy in this MVP subset.",
            "- This report does not estimate monetary cost because provider pricing can vary by account and date.",
            "",
            "## Artifact Paths",
            "",
        ]
    )
    for method in methods:
        lines.extend(
            [
                f"### {method['label']}",
                "",
                f"- Results: `{method['results_dir']}`",
                f"- Evidence eval: `{method['evidence_eval']}`",
                f"- Answer eval: `{method['answer_eval']}`",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize Stage 1 benchmark metrics.")
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    args = parser.parse_args()

    methods = [summarize_method(config) for config in DEFAULT_METHODS]
    payload = {
        "summary": {
            "method_count": len(methods),
            "question_count": methods[0]["result_count"] if methods else 0,
        },
        "methods": methods,
    }

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text(render_markdown(methods), encoding="utf-8")
    print(f"Metrics JSON: {args.output_json}")
    print(f"Metrics report: {args.output_md}")


if __name__ == "__main__":
    main()
