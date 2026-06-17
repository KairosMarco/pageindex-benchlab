from __future__ import annotations

import argparse
import json
import os
import statistics
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

load_dotenv(ROOT / ".env")

from benchlab.schemas import BenchmarkResult  # noqa: E402


DEFAULT_MODEL = "deepseek/deepseek-v4-pro"
DEFAULT_QUESTIONS = ROOT / "datasets" / "financebench" / "expanded_questions_25.jsonl"
DEFAULT_PDF_DIR = ROOT / "datasets" / "raw" / "financebench" / "pdfs"
DEFAULT_RESULTS_DIR = ROOT / "reports" / "long_context" / "qa_llm_expanded_25"
DEFAULT_MANIFEST = ROOT / "reports" / "long_context" / "qa_llm_expanded_25_manifest.json"
DEFAULT_EVIDENCE_EVAL = ROOT / "reports" / "long_context" / "evidence_eval_qa_llm_expanded_25.json"
DEFAULT_ANSWER_EVAL = ROOT / "reports" / "long_context" / "answer_eval_qa_llm_expanded_25.json"
DEFAULT_OUTPUT_JSON = ROOT / "reports" / "long_context_expanded_llm_diagnostics.json"
DEFAULT_OUTPUT_MD = ROOT / "reports" / "long_context_expanded_llm_diagnostics.md"


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def has_model_key() -> bool:
    return any(
        os.getenv(name)
        for name in (
            "DASHSCOPE_API_KEY",
            "DEEPSEEK_API_KEY",
            "OPENAI_API_KEY",
            "ANTHROPIC_API_KEY",
            "GEMINI_API_KEY",
            "OPENROUTER_API_KEY",
        )
    )


def load_json_if_exists(path: Path) -> Any | None:
    if not path.exists():
        return None
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


def command_label(command: list[str]) -> str:
    display = [Path(command[0]).name if index == 0 else item for index, item in enumerate(command)]
    return subprocess.list2cmdline(display)


def run_command(command: list[str], *, dry_run: bool) -> None:
    print(f"+ {command_label(command)}")
    if not dry_run:
        subprocess.run(command, cwd=ROOT, check=True)


def run_long_context(
    *,
    questions: Path,
    pdf_dir: Path,
    model: str,
    answer_mode: str,
    results_dir: Path,
    manifest: Path,
    evidence_eval: Path,
    answer_eval: Path,
    max_citations: int,
    max_document_chars: int | None,
    force: bool,
    continue_on_error: bool,
    dry_run: bool,
) -> None:
    run_args = [
        sys.executable,
        str(ROOT / "scripts" / "run_long_context_mvp.py"),
        "--questions",
        str(questions),
        "--pdf-dir",
        str(pdf_dir),
        "--model",
        model,
        "--max-citations",
        str(max_citations),
        "--output-dir",
        str(results_dir),
        "--manifest",
        str(manifest),
    ]
    if max_document_chars is not None:
        run_args.extend(["--max-document-chars", str(max_document_chars)])
    if force:
        run_args.append("--force")
    if continue_on_error:
        run_args.append("--continue-on-error")
    run_command(run_args, dry_run=dry_run)

    evidence_args = [
        sys.executable,
        str(ROOT / "scripts" / "evaluate_evidence_mvp.py"),
        "--questions",
        str(questions),
        "--results-dir",
        str(results_dir),
        "--output",
        str(evidence_eval),
    ]
    if continue_on_error:
        evidence_args.append("--continue-on-error")
    run_command(evidence_args, dry_run=dry_run)

    answer_args = [
        sys.executable,
        str(ROOT / "scripts" / "evaluate_answers_mvp.py"),
        "--questions",
        str(questions),
        "--results-dir",
        str(results_dir),
        "--output",
        str(answer_eval),
        "--mode",
        answer_mode,
    ]
    if answer_mode == "llm":
        answer_args.extend(["--model", model])
    if continue_on_error:
        answer_args.append("--continue-on-error")
    run_command(answer_args, dry_run=dry_run)


def eval_failures(payload: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not isinstance(payload, dict):
        return []
    return list(payload.get("failures", []))


def generation_failures(manifest: Any | None) -> list[dict[str, Any]]:
    if not isinstance(manifest, list):
        return []
    return [row for row in manifest if row.get("status") == "failed"]


def result_metrics(results: list[BenchmarkResult]) -> dict[str, Any]:
    total_tokens = [result.token_usage.total for result in results if result.token_usage.total is not None]
    input_tokens = [result.token_usage.input for result in results if result.token_usage.input is not None]
    output_tokens = [result.token_usage.output for result in results if result.token_usage.output is not None]
    latencies = [result.latency_ms for result in results if result.latency_ms is not None]
    context_chars = [
        result.metadata.get("context_chars")
        for result in results
        if result.metadata.get("context_chars") is not None
    ]
    context_pages = [
        result.metadata.get("context_page_count")
        for result in results
        if result.metadata.get("context_page_count") is not None
    ]
    return {
        "average_total_tokens": rounded(safe_mean([float(value) for value in total_tokens])),
        "median_total_tokens": rounded(safe_median([float(value) for value in total_tokens])),
        "total_tokens": sum(total_tokens) if total_tokens else None,
        "average_input_tokens": rounded(safe_mean([float(value) for value in input_tokens])),
        "average_output_tokens": rounded(safe_mean([float(value) for value in output_tokens])),
        "average_latency_ms": rounded(safe_mean([float(value) for value in latencies])),
        "median_latency_ms": rounded(safe_median([float(value) for value in latencies])),
        "average_context_chars": rounded(safe_mean([float(value) for value in context_chars])),
        "average_context_pages": rounded(safe_mean([float(value) for value in context_pages])),
        "token_usage_count": len(total_tokens),
        "latency_count": len(latencies),
    }


def per_question_rows(
    *,
    questions_by_id: dict[str, dict[str, Any]],
    results: list[BenchmarkResult],
    evidence: dict[str, Any] | None,
    answer: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    evidence_by_id = {
        row["question_id"]: row for row in (evidence or {}).get("per_question", []) if "question_id" in row
    }
    answer_by_id = {row["question_id"]: row for row in (answer or {}).get("per_question", []) if "question_id" in row}
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
                "context_chars": result.metadata.get("context_chars") if result else None,
                "context_page_count": result.metadata.get("context_page_count") if result else None,
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
    answer_mode: str,
    max_document_chars: int | None,
) -> dict[str, Any]:
    question_rows = load_jsonl(questions)
    questions_by_id = {row["question_id"]: row for row in question_rows}
    results = load_results(results_dir)
    manifest_payload = load_json_if_exists(manifest)
    evidence = load_json_if_exists(evidence_eval)
    answer = load_json_if_exists(answer_eval)
    manifest_count = len(manifest_payload) if isinstance(manifest_payload, list) else 0
    generation_failure_rows = generation_failures(manifest_payload)
    evidence_failures = eval_failures(evidence)
    answer_failures = eval_failures(answer)
    metrics = result_metrics(results)
    question_count = len(question_rows)
    token_usage_complete = metrics["token_usage_count"] == len(results) == question_count
    latency_complete = metrics["latency_count"] == len(results) == question_count
    evidence_summary = evidence.get("summary", {}) if isinstance(evidence, dict) else {}
    answer_summary = answer.get("summary", {}) if isinstance(answer, dict) else {}
    eval_failure_count = len(evidence_failures) + len(answer_failures)
    complete_artifacts = (
        len(results) == question_count
        and manifest_count == question_count
        and evidence_summary.get("result_count") == question_count
        and answer_summary.get("result_count") == question_count
    )
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
        evidence=evidence if isinstance(evidence, dict) else None,
        answer=answer if isinstance(answer, dict) else None,
    )
    return {
        "summary": {
            "date": date.today().isoformat(),
            "method": "long_context_llm",
            "label": "Long-context LLM",
            "question_file": rel(questions),
            "question_count": question_count,
            "model": model,
            "answer_mode": answer_mode,
            "max_document_chars": max_document_chars,
            "status": "complete" if complete_artifacts else "incomplete",
            "mechanical_gate_passed": mechanical_gate_passed,
            "result_count": len(results),
            "manifest_count": manifest_count,
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


def comparison_rows() -> list[dict[str, Any]]:
    llamaindex_path = ROOT / "reports" / "llamaindex_expanded_llm_diagnostics.json"
    payload = load_json_if_exists(llamaindex_path)
    if not isinstance(payload, dict):
        return []
    rows = []
    for method in payload.get("methods", []):
        rows.append(
            {
                "label": method.get("label"),
                "questions": method.get("result_count"),
                "evidence_recall": method.get("average_evidence_recall"),
                "citation_precision": method.get("average_citation_precision"),
                "answer_accuracy": method.get("answer_accuracy"),
                "average_total_tokens": method.get("average_total_tokens"),
                "average_latency_ms": method.get("average_latency_ms"),
            }
        )
    return rows


def render_issue_table(rows: list[dict[str, Any]], issue_type: str) -> list[str]:
    lines = [
        "| Issue | Question | Verdict/Recall | Gold pages | Predicted pages | Rationale |",
        "|---|---|---:|---|---|---|",
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
            "| {issue} | `{qid}` | {verdict} | {gold} | {predicted} | {rationale} |".format(
                issue=issue_type,
                qid=row["question_id"],
                verdict=verdict_or_recall,
                gold=", ".join(str(page) for page in (row.get("gold_pages_one_indexed") or [])),
                predicted=", ".join(str(page) for page in (row.get("predicted_pages") or [])),
                rationale=rationale or "n/a",
            )
        )
    return lines


def render_per_question_table(rows: list[dict[str, Any]]) -> list[str]:
    lines = [
        "| Question | Evidence recall | Citation precision | Verdict | Total tokens | Context chars | Context pages | Latency ms |",
        "|---|---:|---:|---|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            "| `{qid}` | {recall} | {precision} | {verdict} | {tokens} | {chars} | {pages} | {latency} |".format(
                qid=row["question_id"],
                recall=format_value(row.get("evidence_recall")),
                precision=format_value(row.get("citation_precision")),
                verdict=row.get("answer_verdict") or "n/a",
                tokens=format_value(row.get("total_tokens"), digits=0),
                chars=format_value(row.get("context_chars"), digits=0),
                pages=format_value(row.get("context_page_count"), digits=0),
                latency=format_value(row.get("latency_ms"), digits=0),
            )
        )
    return lines


def render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Long-context Expanded LLM Diagnostics",
        "",
        f"Date: {summary['date']}",
        "",
        "## Scope",
        "",
        "This report runs the full-document Long-context LLM baseline on the expanded FinanceBench subset.",
        "",
        f"- Question file: `{summary['question_file']}`",
        f"- Question count: `{summary['question_count']}`",
        f"- Model: `{summary['model']}`",
        f"- Max document chars: `{summary['max_document_chars']}`",
        "",
        "## Summary",
        "",
        "| Method | Status | Questions | Gen failures | Eval failures | Evidence recall | Citation precision | Answer accuracy | Avg total tokens | Avg context chars | Avg context pages | Avg latency ms | Gate |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        "| {label} | {status} | {questions} | {gen_failures} | {eval_failures} | {recall} | {precision} | {accuracy} | {tokens} | {chars} | {pages} | {latency} | {gate} |".format(
            label=summary["label"],
            status=summary["status"],
            questions=summary["result_count"],
            gen_failures=summary["generation_failure_count"],
            eval_failures=summary["evaluation_failure_count"],
            recall=format_value(summary["average_evidence_recall"]),
            precision=format_value(summary["average_citation_precision"]),
            accuracy=format_value(summary["answer_accuracy"]),
            tokens=format_value(summary["average_total_tokens"]),
            chars=format_value(summary["average_context_chars"]),
            pages=format_value(summary["average_context_pages"]),
            latency=format_value(summary["average_latency_ms"]),
            gate="passed" if summary["mechanical_gate_passed"] else "not passed",
        ),
    ]

    comparison = comparison_rows()
    if comparison:
        lines.extend(
            [
                "",
                "## LlamaIndex Comparison Context",
                "",
                "These rows are copied from the committed expanded LlamaIndex diagnostics for quick comparison on the same 25-question subset.",
                "",
                "| Method | Questions | Evidence recall | Citation precision | Answer accuracy | Avg total tokens | Avg latency ms |",
                "|---|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for row in comparison:
            lines.append(
                "| {label} | {questions} | {recall} | {precision} | {accuracy} | {tokens} | {latency} |".format(
                    label=row["label"],
                    questions=row["questions"],
                    recall=format_value(row["evidence_recall"]),
                    precision=format_value(row["citation_precision"]),
                    accuracy=format_value(row["answer_accuracy"]),
                    tokens=format_value(row["average_total_tokens"]),
                    latency=format_value(row["average_latency_ms"]),
                )
            )

    issue_rows = payload["evidence_issue_rows"] + payload["answer_issue_rows"]
    lines.extend(["", "## Failure And Issue Cases", ""])
    if issue_rows:
        if payload["evidence_issue_rows"]:
            lines.extend(render_issue_table(payload["evidence_issue_rows"], "evidence"))
            lines.append("")
        if payload["answer_issue_rows"]:
            lines.extend(render_issue_table(payload["answer_issue_rows"], "answer"))
    else:
        lines.append("No evidence-recall failures or non-correct answer verdicts were observed in this run.")

    lines.extend(["", "## Per-question Diagnostics", ""])
    lines.extend(render_per_question_table(payload["per_question"]))

    lines.extend(["", "## Interpretation", ""])
    if summary["mechanical_gate_passed"]:
        lines.append("- The Long-context baseline completed the mechanical artifact gate for the expanded subset.")
    else:
        lines.append("- The Long-context baseline did not pass the mechanical artifact gate; inspect generation and evaluation failures before comparing quality.")
    lines.extend(
        [
            "- Compare answer accuracy against token and latency cost. This baseline sends full document context, so it should be treated as a strong but expensive reference point.",
            "- Evidence recall depends on the model's cited pages and the lexical fallback citations, not on a retrieval prefilter.",
            "- Any answer issue rows above are answer-generation or judge-strictness findings, not retrieval-only failures.",
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


def write_summary(
    *,
    questions: Path,
    results_dir: Path,
    manifest: Path,
    evidence_eval: Path,
    answer_eval: Path,
    model: str,
    answer_mode: str,
    max_document_chars: int | None,
    output_json: Path,
    output_md: Path,
) -> None:
    payload = summarize(
        questions=questions,
        results_dir=results_dir,
        manifest=manifest,
        evidence_eval=evidence_eval,
        answer_eval=answer_eval,
        model=model,
        answer_mode=answer_mode,
        max_document_chars=max_document_chars,
    )
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(render_markdown(payload), encoding="utf-8")
    print(f"Long-context expanded diagnostics JSON: {output_json}")
    print(f"Long-context expanded diagnostics report: {output_md}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run expanded Long-context LLM diagnostics.")
    parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS)
    parser.add_argument("--pdf-dir", type=Path, default=DEFAULT_PDF_DIR)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--answer-mode", choices=("heuristic", "llm"), default="llm")
    parser.add_argument("--results-dir", type=Path, default=DEFAULT_RESULTS_DIR)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--evidence-eval", type=Path, default=DEFAULT_EVIDENCE_EVAL)
    parser.add_argument("--answer-eval", type=Path, default=DEFAULT_ANSWER_EVAL)
    parser.add_argument("--max-citations", type=int, default=3)
    parser.add_argument("--max-document-chars", type=int, default=None)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--continue-on-error", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--summary-only", action="store_true")
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    args = parser.parse_args()

    if not args.summary_only:
        if not args.dry_run and not has_model_key():
            raise SystemExit(
                "No model API key found in the current shell. Set a provider env var such as "
                "DEEPSEEK_API_KEY or DASHSCOPE_API_KEY before running expanded Long-context diagnostics."
            )
        run_long_context(
            questions=args.questions,
            pdf_dir=args.pdf_dir,
            model=args.model,
            answer_mode=args.answer_mode,
            results_dir=args.results_dir,
            manifest=args.manifest,
            evidence_eval=args.evidence_eval,
            answer_eval=args.answer_eval,
            max_citations=args.max_citations,
            max_document_chars=args.max_document_chars,
            force=args.force,
            continue_on_error=args.continue_on_error,
            dry_run=args.dry_run,
        )

    if not args.dry_run:
        write_summary(
            questions=args.questions,
            results_dir=args.results_dir,
            manifest=args.manifest,
            evidence_eval=args.evidence_eval,
            answer_eval=args.answer_eval,
            model=args.model,
            answer_mode=args.answer_mode,
            max_document_chars=args.max_document_chars,
            output_json=args.output_json,
            output_md=args.output_md,
        )


if __name__ == "__main__":
    main()
