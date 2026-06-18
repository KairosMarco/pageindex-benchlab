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


DEFAULT_OUTPUT_JSON = ROOT / "reports" / "pageindex" / "pageindex_prompt_variant_summary.json"
DEFAULT_OUTPUT_MD = ROOT / "reports" / "pageindex" / "pageindex_prompt_variant_summary.md"
QUESTION_FILE = ROOT / "datasets" / "financebench" / "expanded_questions_25.jsonl"
BASE_RESULTS_DIR = ROOT / "reports" / "pageindex" / "qa_llm_expanded_25"
BASE_EVIDENCE_EVAL = ROOT / "reports" / "pageindex" / "evidence_eval_qa_llm_expanded_25.json"
BASE_ANSWER_EVAL = ROOT / "reports" / "pageindex" / "answer_eval_qa_llm_expanded_25.json"
TARGET_QUESTION_IDS = ("fb_exp_019", "fb_exp_020")


RUNS = [
    {
        "key": "default",
        "label": "default prompt",
        "prompt_mode": "default",
        "result_scope": "full_run",
        "expected_count": 25,
        "results_dir": BASE_RESULTS_DIR,
        "evidence_eval": BASE_EVIDENCE_EVAL,
        "answer_eval": BASE_ANSWER_EVAL,
    },
    {
        "key": "finance_reasoning_v2_probe",
        "label": "finance reasoning v2 probe",
        "prompt_mode": "finance_reasoning_v2",
        "result_scope": "targeted_probe",
        "expected_count": 2,
        "results_dir": ROOT / "reports" / "pageindex" / "qa_llm_expanded_25_finance_reasoning_v2_probe",
        "evidence_eval": ROOT
        / "reports"
        / "pageindex"
        / "evidence_eval_qa_llm_expanded_25_finance_reasoning_v2_probe.json",
        "answer_eval": ROOT
        / "reports"
        / "pageindex"
        / "answer_eval_qa_llm_expanded_25_finance_reasoning_v2_probe.json",
    },
    {
        "key": "finance_reasoning_v3_probe",
        "label": "finance reasoning v3 probe",
        "prompt_mode": "finance_reasoning_v3",
        "result_scope": "targeted_probe",
        "expected_count": 2,
        "results_dir": ROOT / "reports" / "pageindex" / "qa_llm_expanded_25_finance_reasoning_v3_probe",
        "evidence_eval": ROOT
        / "reports"
        / "pageindex"
        / "evidence_eval_qa_llm_expanded_25_finance_reasoning_v3_probe.json",
        "answer_eval": ROOT
        / "reports"
        / "pageindex"
        / "answer_eval_qa_llm_expanded_25_finance_reasoning_v3_probe.json",
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


def fmt(value: Any, digits: int = 3) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def compact(value: Any, max_chars: int = 220) -> str:
    text = " ".join(str(value or "").split()).replace("|", "/")
    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    text = text.encode("ascii", "ignore").decode("ascii")
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3].rstrip() + "..."


def eval_summary(payload: dict[str, Any] | None, key: str) -> Any:
    if not isinstance(payload, dict):
        return None
    return (payload.get("summary") or {}).get(key)


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


def rows_by_question(payload: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    if not isinstance(payload, dict):
        return {}
    return {
        row["question_id"]: row
        for row in payload.get("per_question", [])
        if row.get("question_id") in TARGET_QUESTION_IDS
    }


def result_by_question(results: list[BenchmarkResult]) -> dict[str, BenchmarkResult]:
    return {result.question_id: result for result in results if result.question_id in TARGET_QUESTION_IDS}


def summarize_run(config: dict[str, Any]) -> dict[str, Any]:
    evidence_eval = load_json_if_exists(config["evidence_eval"])
    answer_eval = load_json_if_exists(config["answer_eval"])
    results = load_results(config["results_dir"])
    target_results = result_by_question(results)
    evidence_by_id = rows_by_question(evidence_eval)
    answer_by_id = rows_by_question(answer_eval)
    verdict_counts = eval_summary(answer_eval, "verdict_counts") or {}
    expected_count = int(config["expected_count"])
    complete = (
        len(results) >= expected_count
        and eval_summary(evidence_eval, "result_count") == expected_count
        and eval_summary(answer_eval, "result_count") == expected_count
    )

    target_outcomes = []
    for question_id in TARGET_QUESTION_IDS:
        result = target_results.get(question_id)
        evidence_row = evidence_by_id.get(question_id, {})
        answer_row = answer_by_id.get(question_id, {})
        target_outcomes.append(
            {
                "question_id": question_id,
                "verdict": answer_row.get("verdict"),
                "score": answer_row.get("score"),
                "evidence_recall": evidence_row.get("evidence_recall"),
                "citation_precision": evidence_row.get("citation_precision"),
                "selected_pages_one_indexed": result.metadata.get("selected_pages_one_indexed") if result else None,
                "gold_pages_one_indexed": evidence_row.get("gold_pages_one_indexed"),
                "predicted_answer": result.answer if result else None,
                "judge_rationale": answer_row.get("rationale"),
                "total_tokens": result.token_usage.total if result else None,
                "latency_ms": result.latency_ms if result else None,
                "answer_prompt_mode": (result.metadata.get("answer_prompt_mode") or config["prompt_mode"])
                if result
                else config["prompt_mode"],
                "result_path": rel(config["results_dir"] / f"{question_id}.json"),
            }
        )

    return {
        "key": config["key"],
        "label": config["label"],
        "prompt_mode": config["prompt_mode"],
        "result_scope": config["result_scope"],
        "complete": complete,
        "result_count": len(results),
        "expected_count": expected_count,
        "average_evidence_recall": eval_summary(evidence_eval, "average_evidence_recall"),
        "average_citation_precision": eval_summary(evidence_eval, "average_citation_precision"),
        "answer_accuracy": eval_summary(answer_eval, "accuracy"),
        "average_answer_score": eval_summary(answer_eval, "average_answer_score"),
        "verdict_counts": verdict_counts,
        "results_dir": rel(config["results_dir"]),
        "evidence_eval": rel(config["evidence_eval"]),
        "answer_eval": rel(config["answer_eval"]),
        "target_outcomes": target_outcomes,
        **result_metrics(results),
    }


def build_payload() -> dict[str, Any]:
    question_rows = load_jsonl(QUESTION_FILE)
    questions_by_id = {row["question_id"]: row for row in question_rows}
    runs = [summarize_run(config) for config in RUNS]
    return {
        "summary": {
            "date": date.today().isoformat(),
            "method": "pageindex_tree_qa_llm",
            "question_file": rel(QUESTION_FILE),
            "question_count": len(question_rows),
            "target_question_ids": list(TARGET_QUESTION_IDS),
            "run_count": len(runs),
        },
        "target_questions": [
            {
                "question_id": question_id,
                "doc_name": questions_by_id[question_id]["doc_name"],
                "question": questions_by_id[question_id]["question"],
                "gold_answer": questions_by_id[question_id]["gold_answer"],
            }
            for question_id in TARGET_QUESTION_IDS
        ],
        "runs": runs,
    }


def render_summary_table(runs: list[dict[str, Any]]) -> list[str]:
    lines = [
        "| Run | Scope | Complete | Results | Evidence recall | Citation precision | Answer accuracy | Correct | Partial | Incorrect | Avg tokens | Avg latency ms |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for run in runs:
        counts = run.get("verdict_counts") or {}
        lines.append(
            "| {label} | {scope} | {complete} | {count} | {recall} | {precision} | {accuracy} | {correct} | {partial} | {incorrect} | {tokens} | {latency} |".format(
                label=run["label"],
                scope=run["result_scope"],
                complete="yes" if run["complete"] else "no",
                count=run["result_count"],
                recall=fmt(run["average_evidence_recall"]),
                precision=fmt(run["average_citation_precision"]),
                accuracy=fmt(run["answer_accuracy"]),
                correct=counts.get("correct", 0),
                partial=counts.get("partial", 0),
                incorrect=counts.get("incorrect", 0),
                tokens=fmt(run["average_total_tokens"]),
                latency=fmt(run["average_latency_ms"]),
            )
        )
    return lines


def render_target_table(runs: list[dict[str, Any]]) -> list[str]:
    lines = [
        "| Run | Question | Verdict | Evidence recall | Citation precision | Selected pages | Tokens | Prompt mode |",
        "|---|---|---|---:|---:|---|---:|---|",
    ]
    for run in runs:
        for row in run["target_outcomes"]:
            lines.append(
                "| {label} | `{qid}` | {verdict} | {recall} | {precision} | {pages} | {tokens} | `{prompt}` |".format(
                    label=run["label"],
                    qid=row["question_id"],
                    verdict=row.get("verdict") or "n/a",
                    recall=fmt(row.get("evidence_recall")),
                    precision=fmt(row.get("citation_precision")),
                    pages=", ".join(str(page) for page in (row.get("selected_pages_one_indexed") or [])),
                    tokens=fmt(row.get("total_tokens"), digits=0),
                    prompt=row.get("answer_prompt_mode") or run["prompt_mode"],
                )
            )
    return lines


def render_answer_table(runs: list[dict[str, Any]]) -> list[str]:
    lines = [
        "| Run | Question | Predicted answer | Judge rationale |",
        "|---|---|---|---|",
    ]
    for run in runs:
        for row in run["target_outcomes"]:
            lines.append(
                "| {label} | `{qid}` | {answer} | {rationale} |".format(
                    label=run["label"],
                    qid=row["question_id"],
                    answer=compact(row.get("predicted_answer"), max_chars=280),
                    rationale=compact(row.get("judge_rationale"), max_chars=280),
                )
            )
    return lines


def render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# PageIndex Prompt Variant Summary",
        "",
        f"Date: {summary['date']}",
        "",
        "## Scope",
        "",
        "This report compares targeted PageIndex answer-prompt probes for the two remaining expanded answer issues. The default row is the existing 25-question baseline; the finance rows are two-question probes only.",
        "",
        f"- Question file: `{summary['question_file']}`",
        f"- Method: `{summary['method']}`",
        f"- Target questions: `{', '.join(summary['target_question_ids'])}`",
        "- Model: `deepseek/deepseek-v4-pro`",
        "",
        "## Run Summary",
        "",
    ]
    lines.extend(render_summary_table(payload["runs"]))
    lines.extend(["", "## Target Outcomes", ""])
    lines.extend(render_target_table(payload["runs"]))
    lines.extend(["", "## Answer Evidence", ""])
    lines.extend(render_answer_table(payload["runs"]))
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- The PageIndex retrieval stage was already successful for both target questions; the probes isolate answer-generation behavior.",
            "- `fb_exp_019` is primarily a rounding or judge-policy case: the source value is `$389 million`, while the benchmark gold answer is `$0.40` billion.",
            "- `fb_exp_020` is a finance concept-definition case: the gold answer treats low ROA and a broad goodwill-heavy asset base as capital-intensity evidence, while the default answer used a narrow fixed-asset ratio interpretation.",
            "- Treat these rows as prompt-ablation evidence only. They do not replace the default 25-question cross-method baseline unless a full 25-question PageIndex prompt-variant run is executed.",
            "",
            "## Artifacts",
            "",
        ]
    )
    for run in payload["runs"]:
        lines.extend(
            [
                f"### {run['label']}",
                "",
                f"- Results: `{run['results_dir']}`",
                f"- Evidence eval: `{run['evidence_eval']}`",
                f"- Answer eval: `{run['answer_eval']}`",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize PageIndex answer-prompt variant probes.")
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    args = parser.parse_args()

    payload = build_payload()
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text(render_markdown(payload), encoding="utf-8")
    print(f"PageIndex prompt variant summary JSON: {args.output_json}")
    print(f"PageIndex prompt variant summary report: {args.output_md}")


if __name__ == "__main__":
    main()
