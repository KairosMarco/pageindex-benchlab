from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchlab.schemas import BenchmarkQuestion, BenchmarkResult  # noqa: E402


DEFAULT_QUESTIONS = ROOT / "datasets" / "financebench" / "expanded_questions_25.jsonl"
DEFAULT_RESULTS_DIR = ROOT / "reports" / "structured_rag" / "qa_expanded_25"
DEFAULT_EVIDENCE_EVAL = ROOT / "reports" / "structured_rag" / "evidence_eval_qa_expanded_25.json"
DEFAULT_MANIFEST = ROOT / "reports" / "structured_rag" / "qa_expanded_25_manifest.json"
DEFAULT_OUTPUT_JSON = ROOT / "reports" / "structured_rag" / "expanded_diagnostics.json"
DEFAULT_OUTPUT_MD = ROOT / "reports" / "structured_rag" / "expanded_diagnostics.md"


def load_questions(path: Path) -> dict[str, BenchmarkQuestion]:
    return {
        question.question_id: question
        for question in (BenchmarkQuestion.model_validate_json(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
    }


def load_results(path: Path) -> dict[str, BenchmarkResult]:
    return {
        result_path.stem: BenchmarkResult.model_validate_json(result_path.read_text(encoding="utf-8"))
        for result_path in sorted(path.glob("*.json"))
    }


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def average(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def median(values: list[float]) -> float:
    return statistics.median(values) if values else 0.0


def format_pages(values: list[int] | None) -> str:
    return ", ".join(str(value) for value in (values or []))


def build_payload(
    questions: dict[str, BenchmarkQuestion],
    results: dict[str, BenchmarkResult],
    evidence_eval: dict[str, Any],
    manifest: list[dict[str, Any]],
) -> dict[str, Any]:
    evidence_rows = {row["question_id"]: row for row in evidence_eval.get("per_question", [])}
    manifest_rows = {row["question_id"]: row for row in manifest}
    rows: list[dict[str, Any]] = []

    for question_id, question in questions.items():
        result = results.get(question_id)
        evidence = evidence_rows.get(question_id, {})
        manifest_row = manifest_rows.get(question_id, {})
        predicted_pages = evidence.get("predicted_pages", [])
        gold_pages = evidence.get("gold_pages_one_indexed", [])
        rows.append(
            {
                "question_id": question_id,
                "doc_name": question.doc_name,
                "question_type": question.question_type,
                "question_reasoning": question.question_reasoning,
                "evidence_recall": evidence.get("evidence_recall", 0.0),
                "citation_precision": evidence.get("citation_precision", 0.0),
                "gold_pages_one_indexed": gold_pages,
                "predicted_pages_one_indexed": predicted_pages,
                "matched_pages_zero_indexed": evidence.get("matched_pages", []),
                "citation_count": len(result.citations) if result else 0,
                "node_count": manifest_row.get("node_count"),
                "entity_count": manifest_row.get("entity_count"),
                "edge_count": manifest_row.get("edge_count"),
                "latency_ms": manifest_row.get("latency_ms"),
                "top_sections": [citation.section for citation in (result.citations if result else [])],
            }
        )

    full_hits = [row for row in rows if row["evidence_recall"] >= 1.0]
    misses = [row for row in rows if row["evidence_recall"] <= 0.0]
    partials = [row for row in rows if 0.0 < row["evidence_recall"] < 1.0]
    latency_values = [float(row["latency_ms"]) for row in rows if isinstance(row.get("latency_ms"), (int, float))]
    node_values = [float(row["node_count"]) for row in rows if isinstance(row.get("node_count"), (int, float))]

    return {
        "summary": {
            "method": "structured_tree_graph_rag",
            "question_count": len(rows),
            "generated_count": len(results),
            "average_evidence_recall": average([float(row["evidence_recall"]) for row in rows]),
            "average_citation_precision": average([float(row["citation_precision"]) for row in rows]),
            "full_hit_count": len(full_hits),
            "partial_hit_count": len(partials),
            "miss_count": len(misses),
            "median_latency_ms": median(latency_values),
            "average_latency_ms": average(latency_values),
            "median_node_count": median(node_values),
            "average_node_count": average(node_values),
        },
        "per_question": rows,
        "misses": misses,
        "partials": partials,
    }


def write_markdown(payload: dict[str, Any], output: Path) -> None:
    summary = payload["summary"]
    lines = [
        "# Structured Tree-Graph RAG Expanded Diagnostics",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Questions | {summary['question_count']} |",
        f"| Generated outputs | {summary['generated_count']} |",
        f"| Average evidence recall | {summary['average_evidence_recall']:.3f} |",
        f"| Average citation precision | {summary['average_citation_precision']:.3f} |",
        f"| Full hits | {summary['full_hit_count']} |",
        f"| Partial hits | {summary['partial_hit_count']} |",
        f"| Misses | {summary['miss_count']} |",
        f"| Median latency ms | {summary['median_latency_ms']:.0f} |",
        f"| Average latency ms | {summary['average_latency_ms']:.0f} |",
        f"| Median node count | {summary['median_node_count']:.0f} |",
        "",
        "## Interpretation",
        "",
        "This local baseline is useful as a controlled structural retrieval floor, not as a claim of superiority. It is weaker than PageIndex on the expanded FinanceBench subset, but it gives BenchLab a license-safe tree-plus-graph implementation surface while full BookRAG runtime work continues.",
        "",
        "## Misses",
        "",
        "| Question | Document | Recall | Gold pages | Predicted pages | Question type |",
        "|---|---|---:|---|---|---|",
    ]
    for row in payload["misses"]:
        lines.append(
            "| `{question_id}` | `{doc_name}` | {recall:.3f} | {gold} | {predicted} | {qtype} |".format(
                question_id=row["question_id"],
                doc_name=row["doc_name"],
                recall=float(row["evidence_recall"]),
                gold=format_pages(row["gold_pages_one_indexed"]),
                predicted=format_pages(row["predicted_pages_one_indexed"]),
                qtype=row.get("question_type") or "",
            )
        )

    lines.extend(
        [
            "",
            "## Per Question",
            "",
            "| Question | Document | Recall | Precision | Gold pages | Predicted pages | Latency ms | Nodes |",
            "|---|---|---:|---:|---|---|---:|---:|",
        ]
    )
    for row in payload["per_question"]:
        lines.append(
            "| `{question_id}` | `{doc_name}` | {recall:.3f} | {precision:.3f} | {gold} | {predicted} | {latency} | {nodes} |".format(
                question_id=row["question_id"],
                doc_name=row["doc_name"],
                recall=float(row["evidence_recall"]),
                precision=float(row["citation_precision"]),
                gold=format_pages(row["gold_pages_one_indexed"]),
                predicted=format_pages(row["predicted_pages_one_indexed"]),
                latency=row.get("latency_ms") if row.get("latency_ms") is not None else "",
                nodes=row.get("node_count") if row.get("node_count") is not None else "",
            )
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize structured RAG expanded diagnostics.")
    parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS)
    parser.add_argument("--results-dir", type=Path, default=DEFAULT_RESULTS_DIR)
    parser.add_argument("--evidence-eval", type=Path, default=DEFAULT_EVIDENCE_EVAL)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    args = parser.parse_args()

    payload = build_payload(
        questions=load_questions(args.questions),
        results=load_results(args.results_dir),
        evidence_eval=load_json(args.evidence_eval),
        manifest=load_json(args.manifest),
    )

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_markdown(payload, args.output_md)
    print(f"Structured RAG diagnostics JSON: {args.output_json}")
    print(f"Structured RAG diagnostics MD: {args.output_md}")
    print(
        "questions={question_count} recall={average_evidence_recall:.3f} "
        "precision={average_citation_precision:.3f} misses={miss_count}".format(**payload["summary"])
    )


if __name__ == "__main__":
    main()
