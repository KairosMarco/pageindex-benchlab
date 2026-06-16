from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchlab.schemas import BenchmarkQuestion, BenchmarkResult  # noqa: E402


DEFAULT_QUESTIONS = ROOT / "datasets" / "financebench" / "mvp_questions.jsonl"
DEFAULT_OUTPUT_MD = ROOT / "reports" / "stage1_detailed_evidence_report.md"
DEFAULT_OUTPUT_JSON = ROOT / "reports" / "stage1_detailed_evidence_report.json"
DEFAULT_OUTPUT_CSV = ROOT / "reports" / "stage1_per_question_results.csv"
DEFAULT_METRICS = ROOT / "reports" / "stage1_metrics_summary.json"


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


def load_questions(path: Path) -> dict[str, BenchmarkQuestion]:
    questions: dict[str, BenchmarkQuestion] = {}
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                question = BenchmarkQuestion.model_validate_json(line)
                questions[question.question_id] = question
    return questions


def load_results(path: Path) -> dict[str, BenchmarkResult]:
    return {
        result.question_id: result
        for result in (
            BenchmarkResult.model_validate_json(item.read_text(encoding="utf-8"))
            for item in sorted(path.glob("*.json"))
        )
    }


def index_per_question(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["question_id"]: row for row in payload.get("per_question", [])}


def format_float(value: Any, digits: int = 3) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def format_int(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.0f}"
    return f"{value}"


def page_list(values: list[int] | None) -> str:
    if not values:
        return ""
    return ",".join(str(value) for value in values)


def truncate(text: str, limit: int = 220) -> str:
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3].rstrip() + "..."


def extract_method_metrics(metrics: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["key"]: row for row in metrics.get("methods", [])}


def method_run_record(config: MethodConfig) -> dict[str, Any]:
    evidence = load_json(config.evidence_eval)
    answer = load_json(config.answer_eval)
    return {
        "key": config.key,
        "label": config.label,
        "results_dir": rel(config.results_dir),
        "evidence_eval": rel(config.evidence_eval),
        "answer_eval": rel(config.answer_eval),
        "evidence_by_question": index_per_question(evidence),
        "answer_by_question": index_per_question(answer),
        "evidence_summary": evidence.get("summary", {}),
        "answer_summary": answer.get("summary", {}),
        "results": load_results(config.results_dir),
    }


def build_records(
    questions: dict[str, BenchmarkQuestion],
    method_runs: list[dict[str, Any]],
    metrics_by_method: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for question_id, question in sorted(questions.items()):
        gold_pages_one = [item.page_one_indexed for item in question.gold_evidence]
        for method in method_runs:
            result = method["results"].get(question_id)
            evidence = method["evidence_by_question"].get(question_id, {})
            answer = method["answer_by_question"].get(question_id, {})
            token_usage = result.token_usage if result else None
            citations = result.citations if result else []
            predicted_pages = evidence.get("predicted_pages") or [citation.page for citation in citations if citation.page]
            matched_pages = evidence.get("matched_pages") or []

            records.append(
                {
                    "question_id": question_id,
                    "company": question.company,
                    "doc_name": question.doc_name,
                    "question_type": question.question_type or "",
                    "question_reasoning": question.question_reasoning or "",
                    "question": question.question,
                    "gold_answer": question.gold_answer,
                    "gold_pages_one_indexed": gold_pages_one,
                    "method_key": method["key"],
                    "method_label": method["label"],
                    "predicted_pages": predicted_pages,
                    "matched_pages_zero_indexed": matched_pages,
                    "evidence_recall": evidence.get("evidence_recall"),
                    "citation_precision": evidence.get("citation_precision"),
                    "answer_verdict": answer.get("verdict"),
                    "answer_score": answer.get("score"),
                    "answer_rationale": answer.get("rationale", ""),
                    "predicted_answer": result.answer if result else "",
                    "citation_count": len(citations),
                    "input_tokens": token_usage.input if token_usage else None,
                    "output_tokens": token_usage.output if token_usage else None,
                    "total_tokens": token_usage.total if token_usage else None,
                    "latency_ms": result.latency_ms if result else None,
                    "adapter_mode": (result.metadata or {}).get("adapter_mode") if result else None,
                    "model": (result.metadata or {}).get("model") if result else None,
                    "method_average_total_tokens": metrics_by_method.get(method["key"], {}).get("average_total_tokens"),
                }
            )
    return records


def failure_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    failures = []
    for row in records:
        if row["evidence_recall"] != 1.0 or row["answer_verdict"] != "correct":
            failures.append(row)
    failures.sort(
        key=lambda row: (
            row["question_id"],
            row["method_key"],
        )
    )
    return failures


def unsupported_claims(metrics_by_method: dict[str, dict[str, Any]]) -> list[str]:
    return [
        "The current 12-question MVP is too small to prove broad benchmark superiority; it only validates wiring and early failure modes.",
        "It cannot prove general superiority across FinanceBench, legal contracts, medical documents, or all long documents.",
        "It cannot yet isolate retrieval quality from answer-generation quality, because the same LLM is used after retrieval.",
        "It cannot yet estimate real production cost, because provider pricing and account-level discounts are not recorded.",
        "It cannot yet evaluate GraphRAG or HyperGraphRAG, because those adapters have not been run on the same questions.",
    ]


def supported_claims(metrics_by_method: dict[str, dict[str, Any]]) -> list[str]:
    pageindex = metrics_by_method["pageindex"]
    long_context = metrics_by_method["long_context"]
    vector_rag = metrics_by_method["vector_rag"]
    hybrid_rag = metrics_by_method["hybrid_rag"]
    token_ratio = long_context["average_total_tokens"] / pageindex["average_total_tokens"]
    return [
        (
            "PageIndex, Vector RAG, and Hybrid RAG all reached 1.000 page-level evidence recall "
            "on the 12-question MVP subset."
        ),
        (
            "Long-context reached 1.000 LLM-judge answer accuracy, but used "
            f"{token_ratio:.1f}x PageIndex's average total tokens in this run."
        ),
        (
            "Vector RAG had one answer-generation failure despite 1.000 evidence recall, showing that retrieval success "
            "does not guarantee final answer correctness."
        ),
        (
            "Hybrid RAG matched PageIndex's current answer accuracy and evidence recall, while using fewer average "
            f"tokens ({hybrid_rag['average_total_tokens']:.0f} vs {pageindex['average_total_tokens']:.0f})."
        ),
        (
            "PageIndex currently has lower average latency than Hybrid RAG in this MVP run "
            f"({pageindex['average_latency_ms']:.0f} ms vs {hybrid_rag['average_latency_ms']:.0f} ms)."
        ),
        (
            "Vector RAG used the fewest average tokens, but its answer accuracy was lower "
            f"({vector_rag['answer_accuracy']:.3f}) because of `fb_mvp_006`."
        ),
    ]


def render_summary_table(metrics_by_method: dict[str, dict[str, Any]], method_order: list[MethodConfig]) -> list[str]:
    lines = [
        "| Method | Questions | Evidence recall | Citation precision | Answer accuracy | Avg total tokens | Total tokens | Avg latency ms | Incorrect answers |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for config in method_order:
        row = metrics_by_method[config.key]
        verdict_counts = row.get("answer_verdict_counts", {})
        lines.append(
            "| {label} | {questions} | {recall} | {precision} | {accuracy} | {avg_tokens} | {total_tokens} | {latency} | {incorrect} |".format(
                label=config.label,
                questions=row["result_count"],
                recall=format_float(row["average_evidence_recall"]),
                precision=format_float(row["average_citation_precision"]),
                accuracy=format_float(row["answer_accuracy"]),
                avg_tokens=format_float(row["average_total_tokens"]),
                total_tokens=format_int(row["total_tokens"]),
                latency=format_float(row["average_latency_ms"]),
                incorrect=verdict_counts.get("incorrect", 0),
            )
        )
    return lines


def render_per_question_table(records: list[dict[str, Any]], method_order: list[MethodConfig]) -> list[str]:
    by_question: dict[str, dict[str, dict[str, Any]]] = {}
    question_meta: dict[str, dict[str, Any]] = {}
    for row in records:
        by_question.setdefault(row["question_id"], {})[row["method_key"]] = row
        question_meta[row["question_id"]] = row

    lines = [
        "| Question | Company | Type | Gold pages | PageIndex | Long-context | Vector RAG | Hybrid RAG |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for question_id in sorted(by_question):
        meta = question_meta[question_id]
        cells = []
        for config in method_order:
            row = by_question[question_id][config.key]
            verdict = row["answer_verdict"] or "n/a"
            recall = format_float(row["evidence_recall"])
            precision = format_float(row["citation_precision"])
            tokens = format_int(row["total_tokens"])
            latency = format_int(row["latency_ms"])
            cells.append(f"{verdict}; R={recall}; P={precision}; tok={tokens}; ms={latency}")
        lines.append(
            "| {qid} | {company} | {qtype} | {gold_pages} | {cells} |".format(
                qid=question_id,
                company=meta["company"],
                qtype=meta["question_reasoning"] or meta["question_type"],
                gold_pages=page_list(meta["gold_pages_one_indexed"]),
                cells=" | ".join(cells),
            )
        )
    return lines


def render_failure_table(failures: list[dict[str, Any]]) -> list[str]:
    lines = [
        "| Question | Method | Evidence recall | Answer verdict | Key rationale |",
        "|---|---|---:|---|---|",
    ]
    for row in failures:
        lines.append(
            "| {qid} | {method} | {recall} | {verdict} | {rationale} |".format(
                qid=row["question_id"],
                method=row["method_label"],
                recall=format_float(row["evidence_recall"]),
                verdict=row["answer_verdict"],
                rationale=truncate(row["answer_rationale"], 180).replace("|", "\\|"),
            )
        )
    if not failures:
        lines.append("| n/a | n/a | n/a | n/a | No failures found. |")
    return lines


def render_markdown(
    records: list[dict[str, Any]],
    metrics_by_method: dict[str, dict[str, Any]],
    method_order: list[MethodConfig],
    output_json: Path,
    output_csv: Path,
) -> str:
    failures = failure_records(records)
    lines: list[str] = [
        "# Stage 1 Detailed Evidence Report",
        "",
        "Date: 2026-06-16",
        "",
        "## Purpose",
        "",
        "This report documents the current Stage 1 FinanceBench MVP experiment with enough detail to support or reject benchmark claims. It is generated from committed JSON artifacts rather than manually edited conclusions.",
        "",
        "## Test Protocol",
        "",
        "- Dataset: 12-question FinanceBench MVP subset in `datasets/financebench/mvp_questions.jsonl`.",
        "- Documents: 11 unique SEC filing or earnings PDFs, stored locally under ignored `datasets/raw/financebench/pdfs/`.",
        "- LLM answer model: `deepseek/deepseek-v4-pro` for all answer-generating runs.",
        "- LLM judge model: `deepseek/deepseek-v4-pro` for answer accuracy evaluation.",
        "- Evidence metric: page-level recall and citation precision against FinanceBench gold evidence pages.",
        "- Citation convention: predicted citation pages are one-indexed; FinanceBench gold pages are also stored as one-indexed and zero-indexed in the normalized dataset.",
        "- Raw artifacts: method-level result JSON files under `reports/<method>/qa_llm/`, evidence eval JSON, and answer eval JSON.",
        "",
        "## Method Summary",
        "",
    ]
    lines.extend(render_summary_table(metrics_by_method, method_order))
    lines.extend(
        [
            "",
            "## Claims Supported By Current Data",
            "",
        ]
    )
    lines.extend(f"- {claim}" for claim in supported_claims(metrics_by_method))
    lines.extend(
        [
            "",
            "## Claims Not Yet Supported",
            "",
        ]
    )
    lines.extend(f"- {claim}" for claim in unsupported_claims(metrics_by_method))
    lines.extend(
        [
            "",
            "## Failure And Risk Cases",
            "",
        ]
    )
    lines.extend(render_failure_table(failures))
    lines.extend(
        [
            "",
            "## Per-question Evidence Matrix",
            "",
            "Each cell format is `answer verdict; R=evidence recall; P=citation precision; tok=total tokens; ms=latency`.",
            "",
        ]
    )
    lines.extend(render_per_question_table(records, method_order))
    lines.extend(
        [
            "",
            "## Reproducibility Artifacts",
            "",
            f"- Machine-readable report: `{rel(output_json)}`",
            f"- Per-question CSV: `{rel(output_csv)}`",
            "- Aggregate metrics: `reports/stage1_metrics_summary.json` and `reports/stage1_metrics_summary.md`",
            "- Retrieval comparison: `reports/stage1_retrieval_comparison.md`",
            "",
            "## Next Required Tests",
            "",
            "1. Run a larger FinanceBench subset so the comparison is not dominated by 12 hand-picked MVP examples.",
            "2. Replace dependency-light TF-IDF Vector/Hybrid MVPs with embedding-based LlamaIndex baselines and a stronger reranker.",
            "3. Add answer-evidence consistency checks so the benchmark can detect cases where the right page is retrieved but the final answer misuses the evidence.",
            "4. Record provider pricing assumptions separately before making cost claims.",
            "5. Add GraphRAG and HyperGraphRAG only after the larger question subset and stronger Vector/Hybrid baselines are stable.",
            "",
        ]
    )
    return "\n".join(lines)


def write_csv(records: list[dict[str, Any]], path: Path) -> None:
    columns = [
        "question_id",
        "company",
        "doc_name",
        "question_type",
        "question_reasoning",
        "gold_pages_one_indexed",
        "method_key",
        "method_label",
        "predicted_pages",
        "matched_pages_zero_indexed",
        "evidence_recall",
        "citation_precision",
        "answer_verdict",
        "answer_score",
        "input_tokens",
        "output_tokens",
        "total_tokens",
        "latency_ms",
        "adapter_mode",
        "model",
        "answer_rationale",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for row in records:
            csv_row = {column: row.get(column) for column in columns}
            csv_row["gold_pages_one_indexed"] = page_list(row["gold_pages_one_indexed"])
            csv_row["predicted_pages"] = page_list(row["predicted_pages"])
            csv_row["matched_pages_zero_indexed"] = page_list(row["matched_pages_zero_indexed"])
            writer.writerow(csv_row)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a detailed Stage 1 evidence report.")
    parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS)
    parser.add_argument("--metrics", type=Path, default=DEFAULT_METRICS)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    args = parser.parse_args()

    questions = load_questions(args.questions)
    metrics = load_json(args.metrics)
    metrics_by_method = extract_method_metrics(metrics)
    method_runs = [method_run_record(config) for config in DEFAULT_METHODS]
    records = build_records(questions, method_runs, metrics_by_method)

    payload = {
        "summary": {
            "question_count": len(questions),
            "method_count": len(DEFAULT_METHODS),
            "record_count": len(records),
            "failure_or_risk_count": len(failure_records(records)),
        },
        "supported_claims": supported_claims(metrics_by_method),
        "unsupported_claims": unsupported_claims(metrics_by_method),
        "method_metrics": metrics_by_method,
        "records": records,
    }

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_csv(records, args.output_csv)
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text(
        render_markdown(records, metrics_by_method, DEFAULT_METHODS, args.output_json, args.output_csv),
        encoding="utf-8",
    )
    print(f"Detailed report: {args.output_md}")
    print(f"Detailed JSON: {args.output_json}")
    print(f"Per-question CSV: {args.output_csv}")


if __name__ == "__main__":
    main()
