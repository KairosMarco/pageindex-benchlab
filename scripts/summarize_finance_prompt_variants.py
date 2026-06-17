from __future__ import annotations

import argparse
import json
import statistics
import sys
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchlab.schemas import BenchmarkResult  # noqa: E402


DEFAULT_OUTPUT_JSON = ROOT / "reports" / "finance_prompt_variant_summary.json"
DEFAULT_OUTPUT_MD = ROOT / "reports" / "finance_prompt_variant_summary.md"
QUESTION_FILE = ROOT / "datasets" / "financebench" / "expanded_questions_25.jsonl"


VARIANTS = [
    {
        "key": "default",
        "label": "default prompt",
        "diagnostics": ROOT / "reports" / "llamaindex_expanded_llm_diagnostics.json",
        "results_dir": ROOT / "reports" / "llamaindex_vector_rag" / "qa_llm_expanded_25_concept_v2_r3",
        "evidence_eval": ROOT
        / "reports"
        / "llamaindex_vector_rag"
        / "evidence_eval_qa_llm_expanded_25_concept_v2_r3.json",
        "answer_eval": ROOT
        / "reports"
        / "llamaindex_vector_rag"
        / "answer_eval_qa_llm_expanded_25_concept_v2_r3.json",
    },
    {
        "key": "finance_reasoning_v2",
        "label": "finance reasoning v2",
        "diagnostics": ROOT / "reports" / "llamaindex_expanded_llm_diagnostics_finance_reasoning_v2.json",
        "results_dir": ROOT
        / "reports"
        / "llamaindex_vector_rag"
        / "qa_llm_expanded_25_concept_v2_r3_finance_reasoning_v2",
        "evidence_eval": ROOT
        / "reports"
        / "llamaindex_vector_rag"
        / "evidence_eval_qa_llm_expanded_25_concept_v2_r3_finance_reasoning_v2.json",
        "answer_eval": ROOT
        / "reports"
        / "llamaindex_vector_rag"
        / "answer_eval_qa_llm_expanded_25_concept_v2_r3_finance_reasoning_v2.json",
    },
    {
        "key": "finance_reasoning_v3",
        "label": "finance reasoning v3",
        "diagnostics": ROOT / "reports" / "llamaindex_expanded_llm_diagnostics_finance_reasoning_v3.json",
        "results_dir": ROOT
        / "reports"
        / "llamaindex_vector_rag"
        / "qa_llm_expanded_25_concept_v2_r3_finance_reasoning_v3",
        "evidence_eval": ROOT
        / "reports"
        / "llamaindex_vector_rag"
        / "evidence_eval_qa_llm_expanded_25_concept_v2_r3_finance_reasoning_v3.json",
        "answer_eval": ROOT
        / "reports"
        / "llamaindex_vector_rag"
        / "answer_eval_qa_llm_expanded_25_concept_v2_r3_finance_reasoning_v3.json",
    },
]

PROBES = [
    {
        "key": "finance_reasoning_v1_probe",
        "label": "v1 hard-case probe",
        "results_dir": ROOT
        / "reports"
        / "llamaindex_vector_rag"
        / "qa_llm_expanded_25_concept_v2_r3_finance_reasoning_v1_probe",
        "evidence_eval": ROOT
        / "reports"
        / "llamaindex_vector_rag"
        / "evidence_eval_qa_llm_expanded_25_concept_v2_r3_finance_reasoning_v1_probe.json",
        "answer_eval": ROOT
        / "reports"
        / "llamaindex_vector_rag"
        / "answer_eval_qa_llm_expanded_25_concept_v2_r3_finance_reasoning_v1_probe.json",
    },
    {
        "key": "finance_reasoning_v2_probe",
        "label": "v2 hard-case probe",
        "results_dir": ROOT
        / "reports"
        / "llamaindex_vector_rag"
        / "qa_llm_expanded_25_concept_v2_r3_finance_reasoning_v2_probe",
        "evidence_eval": ROOT
        / "reports"
        / "llamaindex_vector_rag"
        / "evidence_eval_qa_llm_expanded_25_concept_v2_r3_finance_reasoning_v2_probe.json",
        "answer_eval": ROOT
        / "reports"
        / "llamaindex_vector_rag"
        / "answer_eval_qa_llm_expanded_25_concept_v2_r3_finance_reasoning_v2_probe.json",
    },
    {
        "key": "finance_reasoning_v3_probe",
        "label": "v3 rounding plus hard-case probe",
        "results_dir": ROOT
        / "reports"
        / "llamaindex_vector_rag"
        / "qa_llm_expanded_25_concept_v2_r3_finance_reasoning_v3_probe",
        "evidence_eval": ROOT
        / "reports"
        / "llamaindex_vector_rag"
        / "evidence_eval_qa_llm_expanded_25_concept_v2_r3_finance_reasoning_v3_probe.json",
        "answer_eval": ROOT
        / "reports"
        / "llamaindex_vector_rag"
        / "answer_eval_qa_llm_expanded_25_concept_v2_r3_finance_reasoning_v3_probe.json",
    },
]


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_json_if_exists(path: Path) -> Any | None:
    return load_json(path) if path.exists() else None


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def load_results(results_dir: Path) -> list[BenchmarkResult]:
    if not results_dir.exists():
        return []
    return [
        BenchmarkResult.model_validate_json(path.read_text(encoding="utf-8"))
        for path in sorted(results_dir.glob("*.json"))
    ]


def mean(values: list[float]) -> float | None:
    return statistics.mean(values) if values else None


def rounded(value: float | None, digits: int = 3) -> float | None:
    return round(value, digits) if value is not None else None


def metric_from_eval(payload: dict[str, Any] | None, summary_key: str) -> Any:
    if not isinstance(payload, dict):
        return None
    return (payload.get("summary") or {}).get(summary_key)


def result_metrics(results: list[BenchmarkResult]) -> dict[str, Any]:
    total_tokens = [result.token_usage.total for result in results if result.token_usage.total is not None]
    latencies = [result.latency_ms for result in results if result.latency_ms is not None]
    return {
        "average_total_tokens": rounded(mean([float(value) for value in total_tokens])),
        "total_tokens": sum(total_tokens) if total_tokens else None,
        "average_latency_ms": rounded(mean([float(value) for value in latencies])),
        "token_usage_count": len(total_tokens),
        "latency_count": len(latencies),
    }


def issue_rows(answer_eval: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not isinstance(answer_eval, dict):
        return []
    return [
        row
        for row in answer_eval.get("per_question", [])
        if row.get("verdict") and row.get("verdict") != "correct"
    ]


def selected_question_rows(answer_eval: dict[str, Any] | None, question_ids: set[str]) -> dict[str, dict[str, Any]]:
    if not isinstance(answer_eval, dict):
        return {}
    return {
        row["question_id"]: row
        for row in answer_eval.get("per_question", [])
        if row.get("question_id") in question_ids
    }


def summarize_run(config: dict[str, Any], *, question_count: int | None = None) -> dict[str, Any]:
    evidence_eval = load_json_if_exists(config["evidence_eval"])
    answer_eval = load_json_if_exists(config["answer_eval"])
    results = load_results(config["results_dir"])
    verdict_counts = metric_from_eval(answer_eval, "verdict_counts") or {}
    expected_count = question_count if question_count is not None else len(results)
    complete = (
        len(results) == expected_count
        and metric_from_eval(evidence_eval, "result_count") == expected_count
        and metric_from_eval(answer_eval, "result_count") == expected_count
    )
    return {
        "key": config["key"],
        "label": config["label"],
        "complete": complete,
        "result_count": len(results),
        "expected_count": expected_count,
        "average_evidence_recall": metric_from_eval(evidence_eval, "average_evidence_recall"),
        "average_citation_precision": metric_from_eval(evidence_eval, "average_citation_precision"),
        "answer_accuracy": metric_from_eval(answer_eval, "accuracy"),
        "average_answer_score": metric_from_eval(answer_eval, "average_answer_score"),
        "verdict_counts": verdict_counts,
        "incorrect_count": verdict_counts.get("incorrect", 0),
        "partial_count": verdict_counts.get("partial", 0),
        "issue_rows": issue_rows(answer_eval),
        "results_dir": rel(config["results_dir"]),
        "evidence_eval": rel(config["evidence_eval"]),
        "answer_eval": rel(config["answer_eval"]),
        "diagnostics": rel(config["diagnostics"]) if "diagnostics" in config else None,
        **result_metrics(results),
    }


def fmt(value: Any, digits: int = 3) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def render_issue_table(variants: list[dict[str, Any]]) -> list[str]:
    lines = [
        "| Variant | Question | Verdict | Rationale |",
        "|---|---|---|---|",
    ]
    for variant in variants:
        for issue in variant["issue_rows"]:
            rationale = str(issue.get("rationale") or "").replace("\n", " ")
            if len(rationale) > 180:
                rationale = rationale[:177].rstrip() + "..."
            lines.append(
                f"| {variant['label']} | `{issue.get('question_id')}` | {issue.get('verdict')} | {rationale} |"
            )
    if len(lines) == 2:
        lines.append("| n/a | n/a | n/a | No non-correct answer verdicts. |")
    return lines


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Finance Prompt Variant Summary",
        "",
        f"Date: {payload['summary']['date']}",
        "",
        "## Scope",
        "",
        "This report compares answer-prompt variants for the LlamaIndex Vector RAG expanded FinanceBench run.",
        "",
        f"- Question file: `{payload['summary']['question_file']}`",
        f"- Full-run question count: `{payload['summary']['question_count']}`",
        "- Retrieval setup: `concept_v2`, `rerank_top_k=3`, `chunk_size=900`, `chunk_overlap=160`",
        "- Model: `deepseek/deepseek-v4-pro`",
        "",
        "## Full-run Summary",
        "",
        "| Variant | Complete | Results | Evidence recall | Citation precision | Answer accuracy | Correct | Partial | Incorrect | Avg tokens | Avg latency ms |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for variant in payload["variants"]:
        counts = variant.get("verdict_counts") or {}
        lines.append(
            "| {label} | {complete} | {count} | {recall} | {precision} | {accuracy} | {correct} | {partial} | {incorrect} | {tokens} | {latency} |".format(
                label=variant["label"],
                complete="yes" if variant["complete"] else "no",
                count=variant["result_count"],
                recall=fmt(variant["average_evidence_recall"]),
                precision=fmt(variant["average_citation_precision"]),
                accuracy=fmt(variant["answer_accuracy"]),
                correct=counts.get("correct", 0),
                partial=counts.get("partial", 0),
                incorrect=counts.get("incorrect", 0),
                tokens=fmt(variant["average_total_tokens"]),
                latency=fmt(variant["average_latency_ms"]),
            )
        )

    lines.extend(["", "## Probe Summary", ""])
    lines.extend(
        [
            "| Probe | Results | Evidence recall | Citation precision | Answer accuracy | Correct | Partial | Incorrect |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for probe in payload["probes"]:
        counts = probe.get("verdict_counts") or {}
        lines.append(
            "| {label} | {count} | {recall} | {precision} | {accuracy} | {correct} | {partial} | {incorrect} |".format(
                label=probe["label"],
                count=probe["result_count"],
                recall=fmt(probe["average_evidence_recall"]),
                precision=fmt(probe["average_citation_precision"]),
                accuracy=fmt(probe["answer_accuracy"]),
                correct=counts.get("correct", 0),
                partial=counts.get("partial", 0),
                incorrect=counts.get("incorrect", 0),
            )
        )

    lines.extend(["", "## Key Question Outcomes", ""])
    lines.extend(
        [
            "| Variant | `fb_exp_017` working capital | `fb_exp_019` rounding | `fb_exp_020` capital intensity | `fb_mvp_006` legal scope |",
            "|---|---|---|---|---|",
        ]
    )
    for variant in payload["variants"]:
        outcomes = variant.get("selected_question_outcomes", {})
        lines.append(
            "| {label} | {q17} | {q19} | {q20} | {q6} |".format(
                label=variant["label"],
                q17=outcomes.get("fb_exp_017", "n/a"),
                q19=outcomes.get("fb_exp_019", "n/a"),
                q20=outcomes.get("fb_exp_020", "n/a"),
                q6=outcomes.get("fb_mvp_006", "n/a"),
            )
        )

    lines.extend(["", "## Non-correct Full-run Cases", ""])
    lines.extend(render_issue_table(payload["variants"]))

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- The default prompt remains the most stable committed baseline for cross-method comparison because it is short and less prescriptive.",
            "- `finance_reasoning_v2` improved LlamaIndex Vector correct-only answer accuracy from `0.920` to `0.960`, fixing the capital-intensity failure, but it introduced a rounding-format failure on `fb_exp_019`.",
            "- `finance_reasoning_v3` fixed both targeted probe questions (`fb_exp_019` and `fb_exp_020`) but the full run still had two partial answers, showing that stronger prompts can trade one failure mode for another.",
            "- This supports a conservative next step: treat prompt engineering as an answer-generation ablation, not as a replacement for broader retrieval and evaluation improvements.",
            "",
            "## Artifacts",
            "",
        ]
    )
    for variant in payload["variants"]:
        lines.extend(
            [
                f"### {variant['label']}",
                "",
                f"- Diagnostics: `{variant['diagnostics']}`",
                f"- Results: `{variant['results_dir']}`",
                f"- Evidence eval: `{variant['evidence_eval']}`",
                f"- Answer eval: `{variant['answer_eval']}`",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def build_payload() -> dict[str, Any]:
    question_rows = load_jsonl(QUESTION_FILE)
    question_ids = {"fb_exp_017", "fb_exp_019", "fb_exp_020", "fb_mvp_006"}
    variants = [summarize_run(config, question_count=len(question_rows)) for config in VARIANTS]
    for variant, config in zip(variants, VARIANTS):
        answer_eval = load_json_if_exists(config["answer_eval"])
        selected = selected_question_rows(answer_eval, question_ids)
        variant["selected_question_outcomes"] = {
            question_id: selected.get(question_id, {}).get("verdict", "missing")
            for question_id in sorted(question_ids)
        }
    return {
        "summary": {
            "date": date.today().isoformat(),
            "question_file": rel(QUESTION_FILE),
            "question_count": len(question_rows),
            "variant_count": len(variants),
            "probe_count": len(PROBES),
        },
        "variants": variants,
        "probes": [summarize_run(config) for config in PROBES],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize finance answer-prompt variant diagnostics.")
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    args = parser.parse_args()

    payload = build_payload()
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text(render_markdown(payload), encoding="utf-8")
    print(f"Finance prompt variant summary JSON: {args.output_json}")
    print(f"Finance prompt variant summary report: {args.output_md}")


if __name__ == "__main__":
    main()
