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

from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

load_dotenv(ROOT / ".env")

from benchlab.schemas import BenchmarkResult  # noqa: E402


DEFAULT_MODEL = "deepseek/deepseek-v4-pro"
DEFAULT_OUTPUT_JSON = ROOT / "reports" / "llamaindex_finance_llm_diagnostics.json"
DEFAULT_OUTPUT_MD = ROOT / "reports" / "llamaindex_finance_llm_diagnostics.md"


@dataclass(frozen=True)
class CandidateConfig:
    key: str
    label: str
    runner: Path
    results_dir: Path
    manifest: Path
    evidence_eval: Path
    answer_eval: Path


CANDIDATES = {
    "vector": CandidateConfig(
        key="llamaindex_vector_rag_finance",
        label="LlamaIndex Vector RAG + finance rerank",
        runner=ROOT / "scripts" / "run_llamaindex_vector_rag_mvp.py",
        results_dir=ROOT / "reports" / "llamaindex_vector_rag" / "qa_llm_finance",
        manifest=ROOT / "reports" / "llamaindex_vector_rag" / "qa_llm_finance_manifest.json",
        evidence_eval=ROOT / "reports" / "llamaindex_vector_rag" / "evidence_eval_llm_finance.json",
        answer_eval=ROOT / "reports" / "llamaindex_vector_rag" / "answer_eval_llm_finance.json",
    ),
    "hybrid": CandidateConfig(
        key="llamaindex_hybrid_rag_finance",
        label="LlamaIndex Hybrid RAG + finance rerank",
        runner=ROOT / "scripts" / "run_llamaindex_hybrid_rag_mvp.py",
        results_dir=ROOT / "reports" / "llamaindex_hybrid_rag" / "qa_llm_finance",
        manifest=ROOT / "reports" / "llamaindex_hybrid_rag" / "qa_llm_finance_manifest.json",
        evidence_eval=ROOT / "reports" / "llamaindex_hybrid_rag" / "evidence_eval_llm_finance.json",
        answer_eval=ROOT / "reports" / "llamaindex_hybrid_rag" / "answer_eval_llm_finance.json",
    ),
}


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def has_model_key() -> bool:
    import os

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


def load_json_if_exists(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


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


def command_label(command: list[str]) -> str:
    display = [Path(command[0]).name if i == 0 else item for i, item in enumerate(command)]
    return subprocess.list2cmdline(display)


def run_command(command: list[str], *, dry_run: bool) -> None:
    print(f"+ {command_label(command)}")
    if dry_run:
        return
    subprocess.run(command, cwd=ROOT, check=True)


def run_candidate(config: CandidateConfig, *, model: str, answer_mode: str, force: bool, continue_on_error: bool, dry_run: bool) -> None:
    run_args = [
        sys.executable,
        str(config.runner),
        "--model",
        model,
        "--output-dir",
        str(config.results_dir),
        "--manifest",
        str(config.manifest),
    ]
    if force:
        run_args.append("--force")
    if continue_on_error:
        run_args.append("--continue-on-error")
    run_command(run_args, dry_run=dry_run)

    evidence_args = [
        sys.executable,
        str(ROOT / "scripts" / "evaluate_evidence_mvp.py"),
        "--results-dir",
        str(config.results_dir),
        "--output",
        str(config.evidence_eval),
    ]
    if continue_on_error:
        evidence_args.append("--continue-on-error")
    run_command(evidence_args, dry_run=dry_run)

    answer_args = [
        sys.executable,
        str(ROOT / "scripts" / "evaluate_answers_mvp.py"),
        "--results-dir",
        str(config.results_dir),
        "--output",
        str(config.answer_eval),
        "--mode",
        answer_mode,
    ]
    if answer_mode == "llm":
        answer_args.extend(["--model", model])
    if continue_on_error:
        answer_args.append("--continue-on-error")
    run_command(answer_args, dry_run=dry_run)


def summarize_candidate(config: CandidateConfig) -> dict[str, Any]:
    results = load_results(config.results_dir)
    evidence = load_json_if_exists(config.evidence_eval)
    answer = load_json_if_exists(config.answer_eval)
    manifest = load_json_if_exists(config.manifest)

    total_tokens = [result.token_usage.total for result in results if result.token_usage.total is not None]
    latencies = [result.latency_ms for result in results if result.latency_ms is not None]
    failures = []
    if evidence:
        failures.extend({"source": "evidence", **item} for item in evidence.get("failures", []))
    if answer:
        failures.extend({"source": "answer", **item} for item in answer.get("failures", []))

    return {
        "key": config.key,
        "label": config.label,
        "status": "complete" if evidence and answer and len(results) > 0 else "missing_artifacts",
        "result_count": len(results),
        "manifest_count": len(manifest or []),
        "failure_count": len(failures),
        "average_evidence_recall": (evidence or {}).get("summary", {}).get("average_evidence_recall"),
        "average_citation_precision": (evidence or {}).get("summary", {}).get("average_citation_precision"),
        "answer_accuracy": (answer or {}).get("summary", {}).get("accuracy"),
        "average_answer_score": (answer or {}).get("summary", {}).get("average_answer_score"),
        "answer_verdict_counts": (answer or {}).get("summary", {}).get("verdict_counts"),
        "average_total_tokens": rounded(safe_mean([float(value) for value in total_tokens])),
        "median_total_tokens": rounded(safe_median([float(value) for value in total_tokens])),
        "total_tokens": sum(total_tokens) if total_tokens else None,
        "average_latency_ms": rounded(safe_mean([float(value) for value in latencies])),
        "median_latency_ms": rounded(safe_median([float(value) for value in latencies])),
        "results_dir": rel(config.results_dir),
        "manifest": rel(config.manifest),
        "evidence_eval": rel(config.evidence_eval),
        "answer_eval": rel(config.answer_eval),
        "failures": failures,
    }


def format_value(value: Any, digits: int = 3) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# LlamaIndex Finance-aware LLM Diagnostics",
        "",
        f"Date: {payload['summary']['date']}",
        "",
        "## Scope",
        "",
        "This report is for candidate LlamaIndex baselines that use embedding retrieval plus a label-free finance-aware reranker.",
        "It is separate from the main Stage 1 comparison table until answer generation, evidence evaluation, and answer judging are complete and reviewed.",
        "",
        "## Summary",
        "",
        "| Method | Status | Questions | Evidence recall | Citation precision | Answer accuracy | Avg total tokens | Avg latency ms | Failures |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for method in payload["methods"]:
        lines.append(
            "| {label} | {status} | {questions} | {recall} | {precision} | {accuracy} | {tokens} | {latency} | {failures} |".format(
                label=method["label"],
                status=method["status"],
                questions=method["result_count"],
                recall=format_value(method["average_evidence_recall"]),
                precision=format_value(method["average_citation_precision"]),
                accuracy=format_value(method["answer_accuracy"]),
                tokens=format_value(method["average_total_tokens"]),
                latency=format_value(method["average_latency_ms"]),
                failures=method["failure_count"],
            )
        )

    lines.extend(
        [
            "",
            "## Promotion Gate",
            "",
            "Do not promote these rows into the main Stage 1 table until both candidate methods have:",
            "",
            "- 12 generated answer files.",
            "- evidence eval and answer eval with zero evaluation failures.",
            "- token usage and latency recorded for every question.",
            "- reviewed failure cases if answer accuracy is below the existing Hybrid RAG baseline.",
            "",
            "## Artifacts",
            "",
        ]
    )
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


def write_summary(configs: list[CandidateConfig], output_json: Path, output_md: Path) -> None:
    methods = [summarize_candidate(config) for config in configs]
    payload = {
        "summary": {
            "date": date.today().isoformat(),
            "candidate_count": len(methods),
            "complete_count": sum(1 for method in methods if method["status"] == "complete"),
        },
        "methods": methods,
    }
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(render_markdown(payload), encoding="utf-8")
    print(f"Diagnostics JSON: {output_json}")
    print(f"Diagnostics report: {output_md}")


def selected_configs(methods: list[str] | None) -> list[CandidateConfig]:
    keys = methods or ["vector", "hybrid"]
    return [CANDIDATES[key] for key in keys]


def main() -> None:
    parser = argparse.ArgumentParser(description="Run finance-aware LlamaIndex LLM diagnostics and evaluations.")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="LiteLLM model used for answer generation and LLM judging.")
    parser.add_argument("--method", choices=sorted(CANDIDATES), action="append", help="Run one candidate. Can be repeated.")
    parser.add_argument("--answer-mode", choices=("heuristic", "llm"), default="llm")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--continue-on-error", action="store_true")
    parser.add_argument("--dry-run", action="store_true", help="Print commands without running them.")
    parser.add_argument("--summary-only", action="store_true", help="Only regenerate the diagnostics summary from existing artifacts.")
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    args = parser.parse_args()

    configs = selected_configs(args.method)
    if not args.summary_only:
        if not args.dry_run and not has_model_key():
            raise SystemExit(
                "No model API key found in the current shell. Set a provider env var such as "
                "DEEPSEEK_API_KEY or DASHSCOPE_API_KEY before running LLM diagnostics."
            )
        for config in configs:
            run_candidate(
                config,
                model=args.model,
                answer_mode=args.answer_mode,
                force=args.force,
                continue_on_error=args.continue_on_error,
                dry_run=args.dry_run,
            )

    if not args.dry_run:
        write_summary(configs, args.output_json, args.output_md)


if __name__ == "__main__":
    main()
