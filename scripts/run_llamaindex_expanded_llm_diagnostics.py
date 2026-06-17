from __future__ import annotations

import argparse
import json
import os
import statistics
import subprocess
import sys
from dataclasses import dataclass
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
DEFAULT_OUTPUT_JSON = ROOT / "reports" / "llamaindex_expanded_llm_diagnostics.json"
DEFAULT_OUTPUT_MD = ROOT / "reports" / "llamaindex_expanded_llm_diagnostics.md"


@dataclass(frozen=True)
class MethodConfig:
    key: str
    method: str
    label: str
    runner: Path
    base_report_dir: Path


METHODS = {
    "vector": MethodConfig(
        key="llamaindex_vector_rag_expanded_llm",
        method="vector",
        label="LlamaIndex Vector RAG + finance concept_v2 rerank",
        runner=ROOT / "scripts" / "run_llamaindex_vector_rag_mvp.py",
        base_report_dir=ROOT / "reports" / "llamaindex_vector_rag",
    ),
    "hybrid": MethodConfig(
        key="llamaindex_hybrid_rag_expanded_llm",
        method="hybrid",
        label="LlamaIndex Hybrid RAG + finance concept_v2 rerank",
        runner=ROOT / "scripts" / "run_llamaindex_hybrid_rag_mvp.py",
        base_report_dir=ROOT / "reports" / "llamaindex_hybrid_rag",
    ),
}


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


def question_label(questions: Path) -> str:
    stem = questions.stem
    if stem.startswith("expanded_questions_"):
        return stem.replace("expanded_questions_", "expanded_", 1)
    return stem


def artifact_stem(questions: Path, variant_suffix: str, rerank_top_k: int) -> str:
    return f"qa_llm_{question_label(questions)}_{variant_suffix}_r{rerank_top_k}"


def artifact_paths(
    config: MethodConfig,
    *,
    questions: Path,
    variant_suffix: str,
    rerank_top_k: int,
) -> dict[str, Path]:
    stem = artifact_stem(questions, variant_suffix, rerank_top_k)
    return {
        "results_dir": config.base_report_dir / stem,
        "manifest": config.base_report_dir / f"{stem}_manifest.json",
        "evidence_eval": config.base_report_dir / f"evidence_eval_{stem}.json",
        "answer_eval": config.base_report_dir / f"answer_eval_{stem}.json",
    }


def command_label(command: list[str]) -> str:
    display = [Path(command[0]).name if index == 0 else item for index, item in enumerate(command)]
    return subprocess.list2cmdline(display)


def run_command(command: list[str], *, dry_run: bool) -> None:
    print(f"+ {command_label(command)}")
    if not dry_run:
        subprocess.run(command, cwd=ROOT, check=True)


def run_method(
    config: MethodConfig,
    *,
    questions: Path,
    pdf_dir: Path,
    model: str,
    answer_mode: str,
    variant_suffix: str,
    rerank_top_k: int,
    chunk_size: int,
    chunk_overlap: int,
    force: bool,
    continue_on_error: bool,
    dry_run: bool,
) -> dict[str, Path]:
    paths = artifact_paths(
        config,
        questions=questions,
        variant_suffix=variant_suffix,
        rerank_top_k=rerank_top_k,
    )

    # The existing runner names are MVP-oriented, but both accept an explicit question file.
    run_args = [
        sys.executable,
        str(config.runner),
        "--questions",
        str(questions),
        "--pdf-dir",
        str(pdf_dir),
        "--model",
        model,
        "--rerank-top-k",
        str(rerank_top_k),
        "--chunk-size",
        str(chunk_size),
        "--chunk-overlap",
        str(chunk_overlap),
        "--output-dir",
        str(paths["results_dir"]),
        "--manifest",
        str(paths["manifest"]),
    ]
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
        str(paths["results_dir"]),
        "--output",
        str(paths["evidence_eval"]),
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
        str(paths["results_dir"]),
        "--output",
        str(paths["answer_eval"]),
        "--mode",
        answer_mode,
    ]
    if answer_mode == "llm":
        answer_args.extend(["--model", model])
    if continue_on_error:
        answer_args.append("--continue-on-error")
    run_command(answer_args, dry_run=dry_run)

    return paths


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
    context_words = [
        result.metadata.get("answer_context_words")
        for result in results
        if result.metadata.get("answer_context_words") is not None
    ]
    context_chunks = [
        result.metadata.get("answer_context_chunk_count")
        for result in results
        if result.metadata.get("answer_context_chunk_count") is not None
    ]
    context_chars = [
        result.metadata.get("answer_context_chars")
        for result in results
        if result.metadata.get("answer_context_chars") is not None
    ]
    return {
        "average_total_tokens": rounded(safe_mean([float(value) for value in total_tokens])),
        "median_total_tokens": rounded(safe_median([float(value) for value in total_tokens])),
        "total_tokens": sum(total_tokens) if total_tokens else None,
        "average_input_tokens": rounded(safe_mean([float(value) for value in input_tokens])),
        "average_output_tokens": rounded(safe_mean([float(value) for value in output_tokens])),
        "average_latency_ms": rounded(safe_mean([float(value) for value in latencies])),
        "median_latency_ms": rounded(safe_median([float(value) for value in latencies])),
        "average_context_words": rounded(safe_mean([float(value) for value in context_words])),
        "average_context_chunks": rounded(safe_mean([float(value) for value in context_chunks])),
        "average_context_chars": rounded(safe_mean([float(value) for value in context_chars])),
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
                "answer_context_words": result.metadata.get("answer_context_words") if result else None,
                "answer_context_chunks": result.metadata.get("answer_context_chunk_count") if result else None,
                "result_path": (answer_row.get("metadata") or {}).get("result_path")
                or (evidence_row.get("metadata") or {}).get("result_path"),
            }
        )
    return rows


def summarize_method(
    config: MethodConfig,
    *,
    questions: Path,
    variant_suffix: str,
    rerank_top_k: int,
    chunk_size: int,
    chunk_overlap: int,
    paths: dict[str, Path],
) -> dict[str, Any]:
    question_rows = load_jsonl(questions)
    questions_by_id = {row["question_id"]: row for row in question_rows}
    results = load_results(paths["results_dir"])
    manifest = load_json_if_exists(paths["manifest"])
    evidence = load_json_if_exists(paths["evidence_eval"])
    answer = load_json_if_exists(paths["answer_eval"])

    manifest_count = len(manifest) if isinstance(manifest, list) else 0
    generation_failure_rows = generation_failures(manifest)
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
    answer_issue_rows = [
        row for row in rows if row.get("answer_verdict") and row.get("answer_verdict") != "correct"
    ]
    evidence_issue_rows = [
        row for row in rows if row.get("evidence_recall") is not None and row.get("evidence_recall") < 1.0
    ]

    return {
        "key": config.key,
        "method": config.method,
        "label": config.label,
        "status": "complete" if complete_artifacts else "incomplete",
        "mechanical_gate_passed": mechanical_gate_passed,
        "question_file": rel(questions),
        "question_count": question_count,
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
        "rerank_top_k": rerank_top_k,
        "chunk_size": chunk_size,
        "chunk_overlap": chunk_overlap,
        "variant_suffix": variant_suffix,
        "token_usage_complete": token_usage_complete,
        "latency_complete": latency_complete,
        "results_dir": rel(paths["results_dir"]),
        "manifest": rel(paths["manifest"]),
        "evidence_eval": rel(paths["evidence_eval"]),
        "answer_eval": rel(paths["answer_eval"]),
        "generation_failures": generation_failure_rows,
        "evaluation_failures": evidence_failures + answer_failures,
        "answer_issue_rows": answer_issue_rows,
        "evidence_issue_rows": evidence_issue_rows,
        "per_question": rows,
        **metrics,
    }


def issue_rows(methods: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for method in methods:
        for row in method["evidence_issue_rows"]:
            rows.append({"method": method["method"], "label": method["label"], "issue_type": "evidence", **row})
        for row in method["answer_issue_rows"]:
            rows.append({"method": method["method"], "label": method["label"], "issue_type": "answer", **row})
    return rows


def render_issue_table(rows: list[dict[str, Any]]) -> list[str]:
    lines = [
        "| Method | Issue | Question | Verdict/Recall | Gold pages | Predicted pages | Rationale |",
        "|---|---|---|---:|---|---|---|",
    ]
    for row in rows:
        verdict_or_recall = row.get("answer_verdict") or format_value(row.get("evidence_recall"))
        rationale = str(row.get("answer_rationale") or "").replace("\n", " ")
        if len(rationale) > 180:
            rationale = rationale[:177].rstrip() + "..."
        lines.append(
            "| {label} | {issue} | `{qid}` | {verdict} | {gold} | {predicted} | {rationale} |".format(
                label=row["label"],
                issue=row["issue_type"],
                qid=row["question_id"],
                verdict=verdict_or_recall,
                gold=", ".join(str(page) for page in (row.get("gold_pages_one_indexed") or [])),
                predicted=", ".join(str(page) for page in (row.get("predicted_pages") or [])),
                rationale=rationale or "n/a",
            )
        )
    return lines


def render_per_question_table(methods: list[dict[str, Any]]) -> list[str]:
    lines = [
        "| Method | Question | Evidence recall | Citation precision | Verdict | Total tokens | Context words | Latency ms |",
        "|---|---|---:|---:|---|---:|---:|---:|",
    ]
    for method in methods:
        for row in method["per_question"]:
            lines.append(
                "| {label} | `{qid}` | {recall} | {precision} | {verdict} | {tokens} | {words} | {latency} |".format(
                    label=method["label"],
                    qid=row["question_id"],
                    recall=format_value(row.get("evidence_recall")),
                    precision=format_value(row.get("citation_precision")),
                    verdict=row.get("answer_verdict") or "n/a",
                    tokens=format_value(row.get("total_tokens"), digits=0),
                    words=format_value(row.get("answer_context_words"), digits=0),
                    latency=format_value(row.get("latency_ms"), digits=0),
                )
            )
    return lines


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# LlamaIndex Expanded LLM Diagnostics",
        "",
        f"Date: {payload['summary']['date']}",
        "",
        "## Scope",
        "",
        "This report runs answer generation and answer judging for the lowest-context expanded LlamaIndex candidates that passed the retrieval-only precheck.",
        "",
        f"- Question file: `{payload['summary']['question_file']}`",
        f"- Question count: `{payload['summary']['question_count']}`",
        f"- Model: `{payload['summary']['model']}`",
        f"- Reranker variant label: `{payload['summary']['variant_suffix']}`",
        f"- Chunking: `chunk_size={payload['summary']['chunk_size']}`, `chunk_overlap={payload['summary']['chunk_overlap']}`",
        f"- Rerank top-k: `{payload['summary']['rerank_top_k']}`",
        "",
        "The reranker uses only question text and candidate chunk text. Gold evidence pages are used only by the evaluator after generation.",
        "",
        "## Summary",
        "",
        "| Method | Status | Questions | Gen failures | Eval failures | Evidence recall | Citation precision | Answer accuracy | Avg total tokens | Avg context words | Avg latency ms | Gate |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for method in payload["methods"]:
        lines.append(
            "| {label} | {status} | {questions} | {gen_failures} | {eval_failures} | {recall} | {precision} | {accuracy} | {tokens} | {words} | {latency} | {gate} |".format(
                label=method["label"],
                status=method["status"],
                questions=method["result_count"],
                gen_failures=method["generation_failure_count"],
                eval_failures=method["evaluation_failure_count"],
                recall=format_value(method["average_evidence_recall"]),
                precision=format_value(method["average_citation_precision"]),
                accuracy=format_value(method["answer_accuracy"]),
                tokens=format_value(method["average_total_tokens"]),
                words=format_value(method["average_context_words"]),
                latency=format_value(method["average_latency_ms"]),
                gate="passed" if method["mechanical_gate_passed"] else "not passed",
            )
        )

    issues = issue_rows(payload["methods"])
    lines.extend(["", "## Failure And Issue Cases", ""])
    if issues:
        lines.extend(render_issue_table(issues))
    else:
        lines.append("No evidence-recall failures or non-correct answer verdicts were observed in this run.")

    lines.extend(
        [
            "",
            "## Per-question Diagnostics",
            "",
        ]
    )
    lines.extend(render_per_question_table(payload["methods"]))

    all_gate_passed = all(method["mechanical_gate_passed"] for method in payload["methods"])
    all_recall_full = all(method.get("average_evidence_recall") == 1.0 for method in payload["methods"])
    all_accuracy_full = all(method.get("answer_accuracy") == 1.0 for method in payload["methods"])
    lines.extend(["", "## Interpretation", ""])
    if all_gate_passed and all_recall_full and all_accuracy_full:
        lines.extend(
            [
                "- On this 25-question expanded FinanceBench subset, both tested LlamaIndex candidates completed answer generation and evaluation with zero mechanical failures.",
                "- Both candidates preserved `1.000` page-level evidence recall and received `1.000` LLM-judge answer accuracy under the same model protocol.",
                "- This strengthens the LlamaIndex baseline for the current FinanceBench subset; it still does not prove broad superiority for PageIndex, LlamaIndex, or any RAG family outside this evaluated slice.",
            ]
        )
    else:
        lines.extend(
            [
                "- This run should be treated as diagnostic evidence, not a final benchmark conclusion.",
                "- Any issue rows above should be reviewed before promoting these candidates into the main comparison table.",
                "- The larger subset is doing its job if it exposes answer, citation, or retrieval weaknesses that the 12-question MVP did not show.",
            ]
        )

    lines.extend(["", "## Artifacts", ""])
    for method in payload["methods"]:
        lines.extend(
            [
                f"### {method['label']}",
                "",
                f"- Results: `{method['results_dir']}`",
                f"- Manifest: `{method['manifest']}`",
                f"- Evidence eval: `{method['evidence_eval']}`",
                f"- Answer eval: `{method['answer_eval']}`",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def selected_methods(values: list[str] | None) -> list[str]:
    return values or ["vector", "hybrid"]


def write_summary(
    *,
    configs: list[MethodConfig],
    questions: Path,
    model: str,
    answer_mode: str,
    variant_suffix: str,
    rerank_top_k: int,
    chunk_size: int,
    chunk_overlap: int,
    output_json: Path,
    output_md: Path,
) -> None:
    question_rows = load_jsonl(questions)
    methods = [
        summarize_method(
            config,
            questions=questions,
            variant_suffix=variant_suffix,
            rerank_top_k=rerank_top_k,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            paths=artifact_paths(
                config,
                questions=questions,
                variant_suffix=variant_suffix,
                rerank_top_k=rerank_top_k,
            ),
        )
        for config in configs
    ]
    payload = {
        "summary": {
            "date": date.today().isoformat(),
            "question_file": rel(questions),
            "question_count": len(question_rows),
            "model": model,
            "answer_mode": answer_mode,
            "variant_suffix": variant_suffix,
            "rerank_top_k": rerank_top_k,
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
            "method_count": len(methods),
            "mechanical_gate_passed": bool(methods) and all(method["mechanical_gate_passed"] for method in methods),
        },
        "methods": methods,
    }
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(render_markdown(payload), encoding="utf-8")
    print(f"Expanded LLM diagnostics JSON: {output_json}")
    print(f"Expanded LLM diagnostics report: {output_md}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run expanded FinanceBench LlamaIndex LLM diagnostics.")
    parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS)
    parser.add_argument("--pdf-dir", type=Path, default=DEFAULT_PDF_DIR)
    parser.add_argument("--method", choices=sorted(METHODS), action="append")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--answer-mode", choices=("heuristic", "llm"), default="llm")
    parser.add_argument("--variant-suffix", default="concept_v2")
    parser.add_argument("--rerank-top-k", type=int, default=3)
    parser.add_argument("--chunk-size", type=int, default=900)
    parser.add_argument("--chunk-overlap", type=int, default=160)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--continue-on-error", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--summary-only", action="store_true")
    parser.add_argument(
        "--summary-selected-only",
        action="store_true",
        help="Summarize only --method selections. By default the aggregate report summarizes all known methods.",
    )
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    args = parser.parse_args()

    run_configs = [METHODS[method] for method in selected_methods(args.method)]
    if not args.summary_only:
        if not args.dry_run and not has_model_key():
            raise SystemExit(
                "No model API key found in the current shell. Set a provider env var such as "
                "DEEPSEEK_API_KEY or DASHSCOPE_API_KEY before running expanded LLM diagnostics."
            )
        for config in run_configs:
            run_method(
                config,
                questions=args.questions,
                pdf_dir=args.pdf_dir,
                model=args.model,
                answer_mode=args.answer_mode,
                variant_suffix=args.variant_suffix,
                rerank_top_k=args.rerank_top_k,
                chunk_size=args.chunk_size,
                chunk_overlap=args.chunk_overlap,
                force=args.force,
                continue_on_error=args.continue_on_error,
                dry_run=args.dry_run,
            )

    if not args.dry_run:
        # The default report is an aggregate artifact. Keep it stable even when
        # rerunning only one method, so a partial rerun does not erase the other row.
        summary_methods = args.method if args.summary_selected_only else None
        summary_configs = [METHODS[method] for method in selected_methods(summary_methods)]
        write_summary(
            configs=summary_configs,
            questions=args.questions,
            model=args.model,
            answer_mode=args.answer_mode,
            variant_suffix=args.variant_suffix,
            rerank_top_k=args.rerank_top_k,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap,
            output_json=args.output_json,
            output_md=args.output_md,
        )


if __name__ == "__main__":
    main()
