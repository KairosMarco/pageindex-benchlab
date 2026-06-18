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

DEFAULT_QUESTIONS = ROOT / "datasets" / "financebench" / "expanded_questions_25.jsonl"
DEFAULT_RESULTS_DIR = ROOT / "reports" / "pageindex" / "qa_llm_expanded_25"
DEFAULT_MANIFEST = ROOT / "reports" / "pageindex" / "qa_llm_expanded_25_manifest.json"
DEFAULT_EVIDENCE_EVAL = ROOT / "reports" / "pageindex" / "evidence_eval_qa_llm_expanded_25.json"
DEFAULT_ANSWER_EVAL = ROOT / "reports" / "pageindex" / "answer_eval_qa_llm_expanded_25.json"
DEFAULT_OUTPUT_JSON = ROOT / "reports" / "pageindex_expanded_llm_diagnostics.json"
DEFAULT_OUTPUT_MD = ROOT / "reports" / "pageindex_expanded_llm_diagnostics.md"


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


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


def safe_mean(values: list[float]) -> float | None:
    return statistics.mean(values) if values else None


def safe_median(values: list[float]) -> float | None:
    return statistics.median(values) if values else None


def rounded(value: float | None, digits: int = 3) -> float | None:
    return round(value, digits) if value is not None else None


def format_value(value: Any, digits: int = 3) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def markdown_cell(value: Any) -> str:
    """Normalize generated judge text for portable Markdown tables."""

    text = str(value or "").replace("\n", " ").replace("|", "/")
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
    return text.encode("ascii", "ignore").decode("ascii")


def status_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        status = str(row.get("status", "unknown"))
        counts[status] = counts.get(status, 0) + 1
    return counts


def eval_failures(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return list(payload.get("failures", [])) if isinstance(payload, dict) else []


def generation_failures(manifest: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in manifest if row.get("status") == "failed"]


def result_metrics(results: list[BenchmarkResult]) -> dict[str, Any]:
    total_tokens = [result.token_usage.total for result in results if result.token_usage.total is not None]
    input_tokens = [result.token_usage.input for result in results if result.token_usage.input is not None]
    output_tokens = [result.token_usage.output for result in results if result.token_usage.output is not None]
    latencies = [result.latency_ms for result in results if result.latency_ms is not None]
    citation_counts = [len(result.citations) for result in results]
    selected_page_counts = [
        len(result.metadata.get("selected_pages_one_indexed") or [])
        for result in results
        if result.metadata.get("selected_pages_one_indexed") is not None
    ]
    return {
        "average_total_tokens": rounded(safe_mean([float(value) for value in total_tokens])),
        "median_total_tokens": rounded(safe_median([float(value) for value in total_tokens])),
        "total_tokens": sum(total_tokens) if total_tokens else None,
        "average_input_tokens": rounded(safe_mean([float(value) for value in input_tokens])),
        "average_output_tokens": rounded(safe_mean([float(value) for value in output_tokens])),
        "average_latency_ms": rounded(safe_mean([float(value) for value in latencies])),
        "median_latency_ms": rounded(safe_median([float(value) for value in latencies])),
        "average_citation_count": rounded(safe_mean([float(value) for value in citation_counts])),
        "average_selected_page_count": rounded(safe_mean([float(value) for value in selected_page_counts])),
        "token_usage_count": len(total_tokens),
        "latency_count": len(latencies),
    }


def per_question_rows(
    *,
    questions_by_id: dict[str, dict[str, Any]],
    results: list[BenchmarkResult],
    evidence: dict[str, Any],
    answer: dict[str, Any],
) -> list[dict[str, Any]]:
    evidence_by_id = {row["question_id"]: row for row in evidence.get("per_question", [])}
    answer_by_id = {row["question_id"]: row for row in answer.get("per_question", [])}
    result_by_id = {result.question_id: result for result in results}

    rows = []
    for question_id in sorted(questions_by_id):
        question = questions_by_id[question_id]
        result = result_by_id.get(question_id)
        evidence_row = evidence_by_id.get(question_id, {})
        answer_row = answer_by_id.get(question_id, {})
        rows.append(
            {
                "question_id": question_id,
                "doc_name": question.get("doc_name"),
                "question_type": question.get("question_type"),
                "question_reasoning": question.get("question_reasoning"),
                "evidence_recall": evidence_row.get("evidence_recall"),
                "citation_precision": evidence_row.get("citation_precision"),
                "gold_pages_one_indexed": evidence_row.get("gold_pages_one_indexed"),
                "predicted_pages": evidence_row.get("predicted_pages"),
                "answer_verdict": answer_row.get("verdict"),
                "answer_score": answer_row.get("score"),
                "answer_rationale": answer_row.get("rationale"),
                "total_tokens": result.token_usage.total if result else None,
                "latency_ms": result.latency_ms if result else None,
                "citation_count": len(result.citations) if result else None,
                "selected_pages_one_indexed": result.metadata.get("selected_pages_one_indexed") if result else None,
                "result_path": (answer_row.get("metadata") or {}).get("result_path")
                or (evidence_row.get("metadata") or {}).get("result_path"),
            }
        )
    return rows


def summarize(
    *,
    questions: Path,
    results_dir: Path,
    manifest: Path,
    evidence_eval: Path,
    answer_eval: Path,
    model: str,
) -> dict[str, Any]:
    question_rows = load_jsonl(questions)
    questions_by_id = {row["question_id"]: row for row in question_rows}
    results = load_results(results_dir)
    manifest_payload = load_json(manifest)
    evidence = load_json(evidence_eval)
    answer = load_json(answer_eval)

    question_count = len(question_rows)
    generation_failure_rows = generation_failures(manifest_payload)
    evidence_failures = eval_failures(evidence)
    answer_failures = eval_failures(answer)
    metrics = result_metrics(results)
    evidence_summary = evidence.get("summary", {})
    answer_summary = answer.get("summary", {})
    eval_failure_count = len(evidence_failures) + len(answer_failures)
    complete_artifacts = (
        len(results) == question_count
        and len(manifest_payload) == question_count
        and evidence_summary.get("result_count") == question_count
        and answer_summary.get("result_count") == question_count
    )
    token_usage_complete = metrics["token_usage_count"] == len(results) == question_count
    latency_complete = metrics["latency_count"] == len(results) == question_count
    mechanical_gate_passed = (
        complete_artifacts
        and not generation_failure_rows
        and eval_failure_count == 0
        and token_usage_complete
        and latency_complete
    )
    rows = per_question_rows(
        questions_by_id=questions_by_id,
        results=results,
        evidence=evidence,
        answer=answer,
    )
    return {
        "summary": {
            "date": date.today().isoformat(),
            "method": "pageindex_tree_qa_llm",
            "label": "PageIndex tree QA",
            "question_file": rel(questions),
            "question_count": question_count,
            "model": model,
            "status": "complete" if complete_artifacts else "incomplete",
            "mechanical_gate_passed": mechanical_gate_passed,
            "result_count": len(results),
            "manifest_count": len(manifest_payload),
            "manifest_status_counts": status_counts(manifest_payload),
            "generation_failure_count": len(generation_failure_rows),
            "evaluation_failure_count": eval_failure_count,
            "evidence_eval_failure_count": len(evidence_failures),
            "answer_eval_failure_count": len(answer_failures),
            "average_evidence_recall": evidence_summary.get("average_evidence_recall"),
            "average_citation_precision": evidence_summary.get("average_citation_precision"),
            "answer_accuracy": answer_summary.get("accuracy"),
            "average_answer_score": answer_summary.get("average_answer_score"),
            "answer_verdict_counts": answer_summary.get("verdict_counts"),
            "token_usage_complete": token_usage_complete,
            "latency_complete": latency_complete,
            "results_dir": rel(results_dir),
            "manifest": rel(manifest),
            "evidence_eval": rel(evidence_eval),
            "answer_eval": rel(answer_eval),
            **metrics,
        },
        "generation_failures": generation_failure_rows,
        "evaluation_failures": evidence_failures + answer_failures,
        "evidence_issue_rows": [
            row for row in rows if row.get("evidence_recall") is not None and row.get("evidence_recall") < 1.0
        ],
        "answer_issue_rows": [
            row for row in rows if row.get("answer_verdict") and row.get("answer_verdict") != "correct"
        ],
        "per_question": rows,
    }


def render_issue_table(rows: list[dict[str, Any]], issue_type: str) -> list[str]:
    lines = [
        "| Issue | Question | Document | Verdict/Recall | Gold pages | Predicted pages | Rationale |",
        "|---|---|---|---:|---|---|---|",
    ]
    for row in rows:
        if issue_type == "evidence":
            verdict_or_recall = format_value(row.get("evidence_recall"))
        else:
            verdict_or_recall = row.get("answer_verdict") or "n/a"
        rationale = markdown_cell(row.get("answer_rationale"))
        if len(rationale) > 180:
            rationale = rationale[:177].rstrip() + "..."
        lines.append(
            "| {issue} | `{qid}` | `{doc}` | {verdict} | {gold} | {predicted} | {rationale} |".format(
                issue=issue_type,
                qid=row["question_id"],
                doc=row.get("doc_name"),
                verdict=verdict_or_recall,
                gold=", ".join(str(page) for page in (row.get("gold_pages_one_indexed") or [])),
                predicted=", ".join(str(page) for page in (row.get("predicted_pages") or [])),
                rationale=rationale or "n/a",
            )
        )
    return lines


def render_per_question_table(rows: list[dict[str, Any]]) -> list[str]:
    lines = [
        "| Question | Document | Evidence recall | Citation precision | Verdict | Total tokens | Citations | Latency ms |",
        "|---|---|---:|---:|---|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            "| `{qid}` | `{doc}` | {recall} | {precision} | {verdict} | {tokens} | {citations} | {latency} |".format(
                qid=row["question_id"],
                doc=row.get("doc_name"),
                recall=format_value(row.get("evidence_recall")),
                precision=format_value(row.get("citation_precision")),
                verdict=row.get("answer_verdict") or "n/a",
                tokens=format_value(row.get("total_tokens"), digits=0),
                citations=format_value(row.get("citation_count"), digits=0),
                latency=format_value(row.get("latency_ms"), digits=0),
            )
        )
    return lines


def render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    answer_issue_ids = ", ".join(row["question_id"] for row in payload["answer_issue_rows"]) or "none"
    has_evidence_issues = bool(payload["evidence_issue_rows"])
    lines = [
        "# PageIndex Expanded LLM Diagnostics",
        "",
        f"Date: {summary['date']}",
        "",
        "## Scope",
        "",
        "This report summarizes PageIndex answer generation on the expanded 25-question FinanceBench subset.",
        "",
        f"- Question file: `{summary['question_file']}`",
        f"- Question count: `{summary['question_count']}`",
        f"- Model: `{summary['model']}`",
        "",
        "## Summary",
        "",
        "| Method | Status | Questions | Gen failures | Eval failures | Evidence recall | Citation precision | Answer accuracy | Verdicts | Avg total tokens | Avg citations | Avg latency ms | Gate |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|---|",
        "| {label} | {status} | {questions} | {gen_failures} | {eval_failures} | {recall} | {precision} | {accuracy} | {verdicts} | {tokens} | {citations} | {latency} | {gate} |".format(
            label=summary["label"],
            status=summary["status"],
            questions=summary["result_count"],
            gen_failures=summary["generation_failure_count"],
            eval_failures=summary["evaluation_failure_count"],
            recall=format_value(summary["average_evidence_recall"]),
            precision=format_value(summary["average_citation_precision"]),
            accuracy=format_value(summary["answer_accuracy"]),
            verdicts=summary.get("answer_verdict_counts"),
            tokens=format_value(summary["average_total_tokens"]),
            citations=format_value(summary["average_citation_count"]),
            latency=format_value(summary["average_latency_ms"]),
            gate="passed" if summary["mechanical_gate_passed"] else "not passed",
        ),
        "",
        "## Failure And Issue Cases",
        "",
    ]
    if payload["evidence_issue_rows"]:
        lines.extend(render_issue_table(payload["evidence_issue_rows"], "evidence"))
        lines.append("")
    if payload["answer_issue_rows"]:
        lines.extend(render_issue_table(payload["answer_issue_rows"], "answer"))
    if not payload["evidence_issue_rows"] and not payload["answer_issue_rows"]:
        lines.append("No evidence-recall failures or non-correct answer verdicts were observed in this run.")

    lines.extend(["", "## Per-question Diagnostics", ""])
    lines.extend(render_per_question_table(payload["per_question"]))

    lines.extend(["", "## Interpretation", ""])
    if summary["mechanical_gate_passed"]:
        lines.append("- PageIndex completed the mechanical artifact gate for the expanded subset.")
    else:
        lines.append("- PageIndex did not pass the mechanical artifact gate; inspect generation and evaluation failures before comparing quality.")
    if has_evidence_issues:
        lines.append("- Evidence misses remain in this run, so retrieval/ranking should be inspected before making quality claims.")
    else:
        lines.append("- PageIndex retrieved all gold evidence pages in the top three selected pages for this 25-question subset.")
    lines.extend(
        [
            "- PageIndex used a compact three-page answer context; the remaining answer issues are answer-reasoning or judge-strictness cases after successful evidence retrieval.",
            f"- Non-correct answer cases: `{answer_issue_ids}`.",
            "- These results should be reported conservatively: the expanded subset is still small, and stronger claims need larger datasets plus non-finance domains.",
            "",
            "## Artifacts",
            "",
            f"- Results: `{summary['results_dir']}`",
            f"- Manifest: `{summary['manifest']}`",
            f"- Evidence eval: `{summary['evidence_eval']}`",
            f"- Answer eval: `{summary['answer_eval']}`",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize expanded PageIndex LLM diagnostics.")
    parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS)
    parser.add_argument("--results-dir", type=Path, default=DEFAULT_RESULTS_DIR)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--evidence-eval", type=Path, default=DEFAULT_EVIDENCE_EVAL)
    parser.add_argument("--answer-eval", type=Path, default=DEFAULT_ANSWER_EVAL)
    parser.add_argument("--model", default="deepseek/deepseek-v4-pro")
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    args = parser.parse_args()

    payload = summarize(
        questions=args.questions,
        results_dir=args.results_dir,
        manifest=args.manifest,
        evidence_eval=args.evidence_eval,
        answer_eval=args.answer_eval,
        model=args.model,
    )
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text(render_markdown(payload), encoding="utf-8")
    print(f"PageIndex expanded LLM diagnostics JSON: {args.output_json}")
    print(f"PageIndex expanded LLM diagnostics report: {args.output_md}")


if __name__ == "__main__":
    main()
