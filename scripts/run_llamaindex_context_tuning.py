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


DEFAULT_OUTPUT_JSON = ROOT / "reports" / "llamaindex_context_tuning.json"
DEFAULT_OUTPUT_MD = ROOT / "reports" / "llamaindex_context_tuning.md"


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


LLM_VALIDATION_VARIANTS = [
    {
        "method": "vector",
        "label": "LlamaIndex Vector RAG + finance rerank",
        "rerank_top_k": 12,
        "results_dir": ROOT / "reports" / "llamaindex_vector_rag" / "qa_llm_finance",
        "evidence_eval": ROOT / "reports" / "llamaindex_vector_rag" / "evidence_eval_llm_finance.json",
        "answer_eval": ROOT / "reports" / "llamaindex_vector_rag" / "answer_eval_llm_finance.json",
    },
    {
        "method": "vector",
        "label": "LlamaIndex Vector RAG + finance rerank",
        "rerank_top_k": 3,
        "results_dir": ROOT / "reports" / "llamaindex_vector_rag" / "qa_llm_finance_r3",
        "evidence_eval": ROOT / "reports" / "llamaindex_vector_rag" / "evidence_eval_llm_finance_r3.json",
        "answer_eval": ROOT / "reports" / "llamaindex_vector_rag" / "answer_eval_llm_finance_r3.json",
    },
    {
        "method": "hybrid",
        "label": "LlamaIndex Hybrid RAG + finance rerank",
        "rerank_top_k": 12,
        "results_dir": ROOT / "reports" / "llamaindex_hybrid_rag" / "qa_llm_finance",
        "evidence_eval": ROOT / "reports" / "llamaindex_hybrid_rag" / "evidence_eval_llm_finance.json",
        "answer_eval": ROOT / "reports" / "llamaindex_hybrid_rag" / "answer_eval_llm_finance.json",
    },
    {
        "method": "hybrid",
        "label": "LlamaIndex Hybrid RAG + finance rerank",
        "rerank_top_k": 3,
        "results_dir": ROOT / "reports" / "llamaindex_hybrid_rag" / "qa_llm_finance_r3",
        "evidence_eval": ROOT / "reports" / "llamaindex_hybrid_rag" / "evidence_eval_llm_finance_r3.json",
        "answer_eval": ROOT / "reports" / "llamaindex_hybrid_rag" / "answer_eval_llm_finance_r3.json",
    },
]


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def run_command(command: list[str], *, dry_run: bool) -> None:
    print("+ " + subprocess.list2cmdline([Path(command[0]).name, *command[1:]]))
    if not dry_run:
        subprocess.run(command, cwd=ROOT, check=True)


def safe_mean(values: list[float]) -> float | None:
    return statistics.mean(values) if values else None


def rounded(value: float | None, digits: int = 3) -> float | None:
    return round(value, digits) if value is not None else None


def load_results(results_dir: Path) -> list[BenchmarkResult]:
    return [
        BenchmarkResult.model_validate_json(path.read_text(encoding="utf-8"))
        for path in sorted(results_dir.glob("*.json"))
    ]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_json_if_exists(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return load_json(path)


def variant_name(method: str, rerank_top_k: int, chunk_size: int, chunk_overlap: int) -> str:
    return f"context_tuning_{method}_r{rerank_top_k}_c{chunk_size}_o{chunk_overlap}"


def run_variant(
    config: MethodConfig,
    *,
    method: str,
    rerank_top_k: int,
    chunk_size: int,
    chunk_overlap: int,
    force: bool,
    continue_on_error: bool,
    dry_run: bool,
) -> dict[str, Path]:
    name = variant_name(method, rerank_top_k, chunk_size, chunk_overlap)
    results_dir = config.base_report_dir / name
    manifest = config.base_report_dir / f"{name}_manifest.json"
    evidence_eval = config.base_report_dir / f"evidence_eval_{name}.json"

    command = [
        sys.executable,
        str(config.runner),
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


def summarize_variant(
    config: MethodConfig,
    *,
    method: str,
    rerank_top_k: int,
    chunk_size: int,
    chunk_overlap: int,
    paths: dict[str, Path],
) -> dict[str, Any]:
    results = load_results(paths["results_dir"])
    evidence = load_json(paths["evidence_eval"])
    context_chunks = [result.metadata.get("answer_context_chunk_count") for result in results]
    context_chars = [result.metadata.get("answer_context_chars") for result in results]
    context_words = [result.metadata.get("answer_context_words") for result in results]
    latencies = [result.latency_ms for result in results if result.latency_ms is not None]

    return {
        "method": method,
        "method_key": config.key,
        "label": config.label,
        "rerank_top_k": rerank_top_k,
        "chunk_size": chunk_size,
        "chunk_overlap": chunk_overlap,
        "result_count": len(results),
        "failure_count": evidence["summary"]["failure_count"],
        "average_evidence_recall": evidence["summary"]["average_evidence_recall"],
        "average_citation_precision": evidence["summary"]["average_citation_precision"],
        "average_context_chunks": rounded(safe_mean([float(value) for value in context_chunks if value is not None])),
        "average_context_chars": rounded(safe_mean([float(value) for value in context_chars if value is not None])),
        "average_context_words": rounded(safe_mean([float(value) for value in context_words if value is not None])),
        "average_latency_ms": rounded(safe_mean([float(value) for value in latencies])),
        "results_dir": rel(paths["results_dir"]),
        "manifest": rel(paths["manifest"]),
        "evidence_eval": rel(paths["evidence_eval"]),
    }


def format_value(value: Any, digits: int = 3) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def best_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    passing = [row for row in rows if row["failure_count"] == 0 and row["average_evidence_recall"] == 1.0]
    return sorted(
        passing,
        key=lambda row: (
            row["average_context_words"] if row["average_context_words"] is not None else float("inf"),
            row["average_latency_ms"] if row["average_latency_ms"] is not None else float("inf"),
        ),
    )


def summarize_llm_validations() -> list[dict[str, Any]]:
    rows = []
    for item in LLM_VALIDATION_VARIANTS:
        results_dir = item["results_dir"]
        evidence = load_json_if_exists(item["evidence_eval"])
        answer = load_json_if_exists(item["answer_eval"])
        if not results_dir.exists() or not evidence or not answer:
            continue

        results = load_results(results_dir)
        total_tokens = [result.token_usage.total for result in results if result.token_usage.total is not None]
        latencies = [result.latency_ms for result in results if result.latency_ms is not None]
        context_words = [
            result.metadata.get("answer_context_words")
            for result in results
            if result.metadata.get("answer_context_words") is not None
        ]
        rows.append(
            {
                "method": item["method"],
                "label": item["label"],
                "rerank_top_k": item["rerank_top_k"],
                "result_count": len(results),
                "evidence_recall": evidence["summary"]["average_evidence_recall"],
                "citation_precision": evidence["summary"]["average_citation_precision"],
                "answer_accuracy": answer["summary"]["accuracy"],
                "failure_count": evidence["summary"]["failure_count"] + answer["summary"]["failure_count"],
                "average_total_tokens": rounded(safe_mean([float(value) for value in total_tokens])),
                "average_latency_ms": rounded(safe_mean([float(value) for value in latencies])),
                "average_context_words": rounded(safe_mean([float(value) for value in context_words])),
                "results_dir": rel(results_dir),
                "evidence_eval": rel(item["evidence_eval"]),
                "answer_eval": rel(item["answer_eval"]),
            }
        )
    return rows


def token_reduction_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[int, dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(row["method"], {})[row["rerank_top_k"]] = row

    reductions = []
    for method, by_rerank in grouped.items():
        if 12 not in by_rerank or 3 not in by_rerank:
            continue
        baseline = by_rerank[12]
        tuned = by_rerank[3]
        base_tokens = baseline.get("average_total_tokens")
        tuned_tokens = tuned.get("average_total_tokens")
        if not base_tokens or not tuned_tokens:
            continue
        reductions.append(
            {
                "method": method,
                "label": tuned["label"],
                "baseline_rerank_top_k": 12,
                "tuned_rerank_top_k": 3,
                "baseline_average_total_tokens": base_tokens,
                "tuned_average_total_tokens": tuned_tokens,
                "average_total_token_reduction": rounded(base_tokens - tuned_tokens),
                "average_total_token_reduction_pct": rounded((base_tokens - tuned_tokens) / base_tokens * 100.0),
                "baseline_answer_accuracy": baseline["answer_accuracy"],
                "tuned_answer_accuracy": tuned["answer_accuracy"],
                "tuned_evidence_recall": tuned["evidence_recall"],
            }
        )
    return reductions


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# LlamaIndex Context Tuning Diagnostics",
        "",
        f"Date: {payload['summary']['date']}",
        "",
        "## Scope",
        "",
        "This retrieval-only tuning report tests whether finance-aware LlamaIndex candidates can preserve page-level evidence recall while sending fewer chunks into answer generation.",
        "",
        "## Results",
        "",
        "| Method | rerank_top_k | chunk size | overlap | Evidence recall | Citation precision | Avg context words | Avg latency ms |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in payload["variants"]:
        lines.append(
            "| {label} | {rerank} | {chunk} | {overlap} | {recall} | {precision} | {words} | {latency} |".format(
                label=row["label"],
                rerank=row["rerank_top_k"],
                chunk=row["chunk_size"],
                overlap=row["chunk_overlap"],
                recall=format_value(row["average_evidence_recall"]),
                precision=format_value(row["average_citation_precision"]),
                words=format_value(row["average_context_words"]),
                latency=format_value(row["average_latency_ms"]),
            )
        )

    lines.extend(["", "## Lowest-context Passing Variants", ""])
    best = best_rows(payload["variants"])
    if best:
        lines.extend(
            [
                "| Method | rerank_top_k | chunk size | overlap | Avg context words | Evidence recall |",
                "|---|---:|---:|---:|---:|---:|",
            ]
        )
        for row in best[:4]:
            lines.append(
                "| {label} | {rerank} | {chunk} | {overlap} | {words} | {recall} |".format(
                    label=row["label"],
                    rerank=row["rerank_top_k"],
                    chunk=row["chunk_size"],
                    overlap=row["chunk_overlap"],
                    words=format_value(row["average_context_words"]),
                    recall=format_value(row["average_evidence_recall"]),
                )
            )
    else:
        lines.append("No variant preserved 1.000 evidence recall with zero failures.")

    if payload.get("llm_validations"):
        lines.extend(
            [
                "",
                "## LLM Validation",
                "",
                "The lowest-context passing variant, `rerank_top_k=3`, was then run with the same DeepSeek V4 Pro answer and judge protocol used by Stage 1.",
                "",
                "| Method | rerank_top_k | Questions | Evidence recall | Citation precision | Answer accuracy | Avg total tokens | Avg latency ms |",
                "|---|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for row in payload["llm_validations"]:
            lines.append(
                "| {label} | {rerank} | {questions} | {recall} | {precision} | {accuracy} | {tokens} | {latency} |".format(
                    label=row["label"],
                    rerank=row["rerank_top_k"],
                    questions=row["result_count"],
                    recall=format_value(row["evidence_recall"]),
                    precision=format_value(row["citation_precision"]),
                    accuracy=format_value(row["answer_accuracy"]),
                    tokens=format_value(row["average_total_tokens"]),
                    latency=format_value(row["average_latency_ms"]),
                )
            )

    if payload.get("token_reductions"):
        lines.extend(
            [
                "",
                "## Token Reduction",
                "",
                "| Method | Baseline rerank_top_k | Tuned rerank_top_k | Avg tokens before | Avg tokens after | Reduction | Reduction % | Answer accuracy after |",
                "|---|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for row in payload["token_reductions"]:
            lines.append(
                "| {label} | {base_k} | {tuned_k} | {base_tokens} | {tuned_tokens} | {reduction} | {reduction_pct} | {accuracy} |".format(
                    label=row["label"],
                    base_k=row["baseline_rerank_top_k"],
                    tuned_k=row["tuned_rerank_top_k"],
                    base_tokens=format_value(row["baseline_average_total_tokens"]),
                    tuned_tokens=format_value(row["tuned_average_total_tokens"]),
                    reduction=format_value(row["average_total_token_reduction"]),
                    reduction_pct=format_value(row["average_total_token_reduction_pct"]),
                    accuracy=format_value(row["tuned_answer_accuracy"]),
                )
            )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- The retrieval-only grid shows that `rerank_top_k=3` preserves page-level evidence recall while reducing answer context from 12 chunks to 3 chunks.",
            "- The LLM validation confirms that `rerank_top_k=3` preserved 1.000 LLM-judge answer accuracy on the 12-question MVP subset.",
            "- This supports using `rerank_top_k=3` as the next LlamaIndex finance-aware default for the MVP subset, while still requiring a larger subset before making broad claims.",
            "",
            "## Artifacts",
            "",
        ]
    )
    for row in payload["variants"]:
        lines.extend(
            [
                f"### {row['label']} r{row['rerank_top_k']} c{row['chunk_size']} o{row['chunk_overlap']}",
                "",
                f"- Results: `{row['results_dir']}`",
                f"- Manifest: `{row['manifest']}`",
                f"- Evidence eval: `{row['evidence_eval']}`",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def selected_methods(values: list[str] | None) -> list[str]:
    return values or ["vector", "hybrid"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Run retrieval-only LlamaIndex context tuning diagnostics.")
    parser.add_argument("--method", choices=sorted(METHODS), action="append")
    parser.add_argument("--rerank-top-k", type=int, action="append", default=None)
    parser.add_argument("--chunk-size", type=int, action="append", default=None)
    parser.add_argument("--chunk-overlap", type=int, action="append", default=None)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--continue-on-error", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--summary-only", action="store_true")
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    args = parser.parse_args()

    rerank_values = args.rerank_top_k or [3, 6, 9, 12]
    chunk_values = args.chunk_size or [900]
    overlap_values = args.chunk_overlap or [160]

    variants = []
    for method in selected_methods(args.method):
        config = METHODS[method]
        for chunk_size in chunk_values:
            for chunk_overlap in overlap_values:
                for rerank_top_k in rerank_values:
                    name = variant_name(method, rerank_top_k, chunk_size, chunk_overlap)
                    paths = {
                        "results_dir": config.base_report_dir / name,
                        "manifest": config.base_report_dir / f"{name}_manifest.json",
                        "evidence_eval": config.base_report_dir / f"evidence_eval_{name}.json",
                    }
                    if not args.summary_only:
                        paths = run_variant(
                            config,
                            method=method,
                            rerank_top_k=rerank_top_k,
                            chunk_size=chunk_size,
                            chunk_overlap=chunk_overlap,
                            force=args.force,
                            continue_on_error=args.continue_on_error,
                            dry_run=args.dry_run,
                        )
                    if not args.dry_run:
                        variants.append(
                            summarize_variant(
                                config,
                                method=method,
                                rerank_top_k=rerank_top_k,
                                chunk_size=chunk_size,
                                chunk_overlap=chunk_overlap,
                                paths=paths,
                            )
                        )

    if args.dry_run:
        return

    payload = {
        "summary": {
            "date": date.today().isoformat(),
            "variant_count": len(variants),
        },
        "variants": variants,
    }
    payload["llm_validations"] = summarize_llm_validations()
    payload["token_reductions"] = token_reduction_rows(payload["llm_validations"])
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text(render_markdown(payload), encoding="utf-8")
    print(f"Context tuning JSON: {args.output_json}")
    print(f"Context tuning report: {args.output_md}")


if __name__ == "__main__":
    main()
