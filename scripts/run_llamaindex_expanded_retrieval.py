from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchlab.schemas import BenchmarkResult  # noqa: E402


DEFAULT_QUESTIONS = ROOT / "datasets" / "financebench" / "expanded_questions_25.jsonl"
DEFAULT_PDF_DIR = ROOT / "datasets" / "raw" / "financebench" / "pdfs"
DEFAULT_OUTPUT_JSON = ROOT / "reports" / "llamaindex_expanded_retrieval.json"
DEFAULT_OUTPUT_MD = ROOT / "reports" / "llamaindex_expanded_retrieval.md"


@dataclass(frozen=True)
class MethodConfig:
    key: str
    label: str
    runner: Path
    base_report_dir: Path


METHODS = {
    "vector": MethodConfig(
        key="llamaindex_vector_rag",
        label="LlamaIndex Vector RAG + finance rerank",
        runner=ROOT / "scripts" / "run_llamaindex_vector_rag_mvp.py",
        base_report_dir=ROOT / "reports" / "llamaindex_vector_rag",
    ),
    "hybrid": MethodConfig(
        key="llamaindex_hybrid_rag",
        label="LlamaIndex Hybrid RAG + finance rerank",
        runner=ROOT / "scripts" / "run_llamaindex_hybrid_rag_mvp.py",
        base_report_dir=ROOT / "reports" / "llamaindex_hybrid_rag",
    ),
}


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def load_json(path: Path) -> dict[str, Any]:
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


def rounded(value: float | None, digits: int = 3) -> float | None:
    return round(value, digits) if value is not None else None


def format_value(value: Any, digits: int = 3) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def selected_methods(values: list[str] | None) -> list[str]:
    return values or ["vector", "hybrid"]


def selected_rerank_values(values: list[int] | None) -> list[int]:
    return values or [3, 6, 12]


def variant_stem(
    questions: Path,
    method: str,
    rerank_top_k: int,
    chunk_size: int,
    chunk_overlap: int,
    variant_suffix: str | None = None,
) -> str:
    stem = f"{questions.stem}_{method}_r{rerank_top_k}_c{chunk_size}_o{chunk_overlap}"
    return f"{stem}_{variant_suffix}" if variant_suffix else stem


def run_command(command: list[str], *, dry_run: bool) -> None:
    print("+ " + subprocess.list2cmdline([Path(command[0]).name, *command[1:]]))
    if not dry_run:
        subprocess.run(command, cwd=ROOT, check=True)


def run_method(
    config: MethodConfig,
    *,
    method: str,
    questions: Path,
    pdf_dir: Path,
    rerank_top_k: int,
    chunk_size: int,
    chunk_overlap: int,
    variant_suffix: str | None,
    force: bool,
    continue_on_error: bool,
    dry_run: bool,
) -> dict[str, Path]:
    stem = variant_stem(questions, method, rerank_top_k, chunk_size, chunk_overlap, variant_suffix)
    results_dir = config.base_report_dir / stem
    manifest = config.base_report_dir / f"{stem}_manifest.json"
    evidence_eval = config.base_report_dir / f"evidence_eval_{stem}.json"

    command = [
        sys.executable,
        str(config.runner),
        "--questions",
        str(questions),
        "--pdf-dir",
        str(pdf_dir),
        "--no-llm",
        "--rerank-top-k",
        str(rerank_top_k),
        "--chunk-size",
        str(chunk_size),
        "--chunk-overlap",
        str(chunk_overlap),
        "--output-dir",
        str(results_dir),
        "--manifest",
        str(manifest),
    ]
    if force:
        command.append("--force")
    if continue_on_error:
        command.append("--continue-on-error")
    run_command(command, dry_run=dry_run)

    eval_command = [
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
        eval_command.append("--continue-on-error")
    run_command(eval_command, dry_run=dry_run)

    return {
        "results_dir": results_dir,
        "manifest": manifest,
        "evidence_eval": evidence_eval,
    }


def summarize_method(
    config: MethodConfig,
    *,
    method: str,
    questions: Path,
    rerank_top_k: int,
    chunk_size: int,
    chunk_overlap: int,
    paths: dict[str, Path],
) -> dict[str, Any]:
    question_rows = load_jsonl(questions)
    manifest = load_json(paths["manifest"]) if paths["manifest"].exists() else []
    evidence = load_json(paths["evidence_eval"]) if paths["evidence_eval"].exists() else {"summary": {}, "failures": []}
    results = load_results(paths["results_dir"])

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
    latencies = [result.latency_ms for result in results if result.latency_ms is not None]
    manifest_failures = [row for row in manifest if row.get("status") == "failed"]
    evidence_summary = evidence.get("summary", {})

    return {
        "method": method,
        "method_key": config.key,
        "label": config.label,
        "question_file": rel(questions),
        "question_count": len(question_rows),
        "result_count": evidence_summary.get("result_count", len(results)),
        "coverage": rounded((evidence_summary.get("result_count", len(results)) / len(question_rows)) if question_rows else None),
        "failure_count": evidence_summary.get("failure_count", 0),
        "manifest_failure_count": len(manifest_failures),
        "average_evidence_recall": evidence_summary.get("average_evidence_recall"),
        "average_citation_precision": evidence_summary.get("average_citation_precision"),
        "average_context_chunks": rounded(safe_mean([float(value) for value in context_chunks])),
        "average_context_words": rounded(safe_mean([float(value) for value in context_words])),
        "average_latency_ms": rounded(safe_mean([float(value) for value in latencies])),
        "rerank_top_k": rerank_top_k,
        "chunk_size": chunk_size,
        "chunk_overlap": chunk_overlap,
        "results_dir": rel(paths["results_dir"]),
        "manifest": rel(paths["manifest"]),
        "evidence_eval": rel(paths["evidence_eval"]),
        "manifest_failures": manifest_failures,
    }


def failure_rows(row: dict[str, Any], questions_by_id: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    evidence_path = ROOT / row["evidence_eval"]
    if not evidence_path.exists():
        return []
    evidence = load_json(evidence_path)
    failures = []
    for item in evidence.get("per_question", []):
        if item.get("evidence_recall") == 1.0:
            continue
        question = questions_by_id[item["question_id"]]
        failures.append(
            {
                "method": row["method"],
                "label": row["label"],
                "rerank_top_k": row["rerank_top_k"],
                "question_id": item["question_id"],
                "doc_name": question["doc_name"],
                "question_type": question.get("question_type"),
                "question_reasoning": question.get("question_reasoning"),
                "gold_pages_one_indexed": item.get("gold_pages_one_indexed", []),
                "predicted_pages": item.get("predicted_pages", []),
                "evidence_recall": item.get("evidence_recall"),
                "citation_precision": item.get("citation_precision"),
                "question": question["question"],
            }
        )
    return failures


def render_markdown(payload: dict[str, Any]) -> str:
    variant_suffix = payload["summary"].get("variant_suffix")
    variant_label = f"`{variant_suffix}`" if variant_suffix else "default"
    lines = [
        "# LlamaIndex Expanded Retrieval Diagnostics",
        "",
        f"Date: {payload['summary']['date']}",
        "",
        "## Scope",
        "",
        "This report runs retrieval-only LlamaIndex finance-aware candidates on the expanded FinanceBench subset. It does not evaluate LLM answer quality; it checks whether the low-context `rerank_top_k=3` setting still retrieves the gold evidence pages before spending answer-generation budget.",
        "",
        f"- Question file: `{payload['summary']['question_file']}`",
        f"- Variant suffix: {variant_label}",
        f"- Chunking: `chunk_size={payload['summary']['chunk_size']}`, `chunk_overlap={payload['summary']['chunk_overlap']}`",
        "",
        "## Results",
        "",
        "| Method | rerank_top_k | Questions | Results | Coverage | Evidence recall | Citation precision | Avg context words | Manifest failures |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in payload["methods"]:
        lines.append(
            "| {label} | {rerank} | {questions} | {results} | {coverage} | {recall} | {precision} | {words} | {failures} |".format(
                label=row["label"],
                rerank=row["rerank_top_k"],
                questions=row["question_count"],
                results=row["result_count"],
                coverage=format_value(row["coverage"]),
                recall=format_value(row["average_evidence_recall"]),
                precision=format_value(row["average_citation_precision"]),
                words=format_value(row["average_context_words"]),
                failures=row["manifest_failure_count"],
            )
        )

    if payload.get("failures"):
        lines.extend(
            [
                "",
                "## Failure Cases",
                "",
                "| Method | rerank_top_k | Question | Document | Gold pages | Predicted pages | Recall | Question type |",
                "|---|---:|---|---|---|---|---:|---|",
            ]
        )
        for row in payload["failures"]:
            lines.append(
                "| {label} | {rerank} | `{qid}` | `{doc}` | {gold} | {predicted} | {recall} | {qtype} |".format(
                    label=row["label"],
                    rerank=row["rerank_top_k"],
                    qid=row["question_id"],
                    doc=row["doc_name"],
                    gold=", ".join(str(page) for page in row["gold_pages_one_indexed"]),
                    predicted=", ".join(str(page) for page in row["predicted_pages"]),
                    recall=format_value(row["evidence_recall"]),
                    qtype=row.get("question_type") or "n/a",
                )
            )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- This is a generalization check for the 12-question MVP tuning result, not a final benchmark claim.",
            "- A method should move to expanded LLM answer generation only if retrieval coverage is complete and evidence recall remains high enough to justify API cost.",
            "- Failures in this report should be investigated per question before changing benchmark conclusions.",
        ]
    )
    if payload.get("failures"):
        lines.append("- The failed rows above show that this retrieval configuration is not ready for expanded LLM answer generation.")
    else:
        lines.append("- No evidence failures were observed; `rerank_top_k=3` gives the smallest answer context among the passing variants.")

    lines.extend(["", "## Artifacts", ""])
    for row in payload["methods"]:
        lines.extend(
            [
                f"### {row['label']}",
                "",
                f"- rerank_top_k: `{row['rerank_top_k']}`",
                f"- Results: `{row['results_dir']}`",
                f"- Manifest: `{row['manifest']}`",
                f"- Evidence eval: `{row['evidence_eval']}`",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run retrieval-only LlamaIndex diagnostics on an expanded FinanceBench subset.")
    parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS)
    parser.add_argument("--pdf-dir", type=Path, default=DEFAULT_PDF_DIR)
    parser.add_argument("--method", choices=sorted(METHODS), action="append")
    parser.add_argument("--rerank-top-k", type=int, action="append", default=None)
    parser.add_argument("--chunk-size", type=int, default=900)
    parser.add_argument("--chunk-overlap", type=int, default=160)
    parser.add_argument("--variant-suffix", default=None, help="Append a suffix to output artifact names.")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--continue-on-error", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--summary-only", action="store_true")
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    args = parser.parse_args()

    method_rows = []
    for method in selected_methods(args.method):
        config = METHODS[method]
        for rerank_top_k in selected_rerank_values(args.rerank_top_k):
            paths = {
                "results_dir": config.base_report_dir
                / variant_stem(
                    args.questions,
                    method,
                    rerank_top_k,
                    args.chunk_size,
                    args.chunk_overlap,
                    args.variant_suffix,
                ),
                "manifest": config.base_report_dir
                / (
                    f"{variant_stem(args.questions, method, rerank_top_k, args.chunk_size, args.chunk_overlap, args.variant_suffix)}"
                    "_manifest.json"
                ),
                "evidence_eval": config.base_report_dir
                / (
                    "evidence_eval_"
                    f"{variant_stem(args.questions, method, rerank_top_k, args.chunk_size, args.chunk_overlap, args.variant_suffix)}.json"
                ),
            }
            if not args.summary_only:
                paths = run_method(
                    config,
                    method=method,
                    questions=args.questions,
                    pdf_dir=args.pdf_dir,
                    rerank_top_k=rerank_top_k,
                    chunk_size=args.chunk_size,
                    chunk_overlap=args.chunk_overlap,
                    variant_suffix=args.variant_suffix,
                    force=args.force,
                    continue_on_error=args.continue_on_error,
                    dry_run=args.dry_run,
                )
            if not args.dry_run:
                method_rows.append(
                    summarize_method(
                        config,
                        method=method,
                        questions=args.questions,
                        rerank_top_k=rerank_top_k,
                        chunk_size=args.chunk_size,
                        chunk_overlap=args.chunk_overlap,
                        paths=paths,
                    )
                )

    if args.dry_run:
        return

    question_rows = load_jsonl(args.questions)
    questions_by_id = {row["question_id"]: row for row in question_rows}
    failures = []
    for row in method_rows:
        failures.extend(failure_rows(row, questions_by_id))

    payload = {
        "summary": {
            "date": date.today().isoformat(),
            "question_file": rel(args.questions),
            "method_count": len(method_rows),
            "rerank_top_k_values": selected_rerank_values(args.rerank_top_k),
            "chunk_size": args.chunk_size,
            "chunk_overlap": args.chunk_overlap,
            "variant_suffix": args.variant_suffix,
        },
        "methods": method_rows,
        "failures": failures,
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text(render_markdown(payload), encoding="utf-8")
    print(f"Expanded retrieval JSON: {args.output_json}")
    print(f"Expanded retrieval report: {args.output_md}")


if __name__ == "__main__":
    main()
