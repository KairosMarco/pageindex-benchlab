from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_READINESS = ROOT / "reports" / "pageindex" / "expanded_readiness.json"
DEFAULT_QA_MANIFEST = ROOT / "reports" / "pageindex" / "qa_expanded_25_manifest.json"
DEFAULT_EVIDENCE = ROOT / "reports" / "pageindex" / "evidence_eval_qa_expanded_25.json"
DEFAULT_OUTPUT_JSON = ROOT / "reports" / "pageindex" / "expanded_partial_summary.json"
DEFAULT_OUTPUT_MD = ROOT / "reports" / "pageindex" / "expanded_partial_summary.md"


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def status_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        status = str(row.get("status", "unknown"))
        counts[status] = counts.get(status, 0) + 1
    return counts


def evidence_issue_rows(evidence: dict[str, Any]) -> list[dict[str, Any]]:
    issues = []
    for row in evidence.get("per_question", []):
        if row.get("evidence_recall") != 1.0 or row.get("citation_precision") != 1 / 3:
            issues.append(
                {
                    "question_id": row["question_id"],
                    "doc_name": row["metadata"]["doc_name"],
                    "evidence_recall": row["evidence_recall"],
                    "citation_precision": row["citation_precision"],
                    "gold_pages_one_indexed": row["gold_pages_one_indexed"],
                    "predicted_pages": row["predicted_pages"],
                }
            )
    return issues


def build_payload(readiness_path: Path, manifest_path: Path, evidence_path: Path) -> dict[str, Any]:
    readiness = load_json(readiness_path)
    manifest = load_json(manifest_path)
    evidence = load_json(evidence_path)
    generated_rows = [row for row in manifest if row.get("status") == "generated"]
    failed_rows = [row for row in manifest if row.get("status") == "failed"]

    return {
        "summary": {
            "date": date.today().isoformat(),
            "question_count": readiness["summary"]["question_count"],
            "unique_doc_count": readiness["summary"]["unique_doc_count"],
            "ready_doc_count": readiness["summary"]["ready_doc_count"],
            "missing_structure_count": readiness["summary"]["missing_structure_count"],
            "missing_pdf_count": readiness["summary"]["missing_pdf_count"],
            "runnable_question_count": readiness["summary"]["runnable_question_count"],
            "qa_generated_count": len(generated_rows),
            "qa_failed_count": len(failed_rows),
            "qa_status_counts": status_counts(manifest),
            "evidence_result_count": evidence["summary"]["result_count"],
            "average_evidence_recall": evidence["summary"]["average_evidence_recall"],
            "average_citation_precision": evidence["summary"]["average_citation_precision"],
            "full_expanded_ready": readiness["summary"]["full_expanded_ready"],
            "readiness_report": rel(readiness_path),
            "qa_manifest": rel(manifest_path),
            "evidence_eval": rel(evidence_path),
        },
        "missing_structures": readiness["missing_structures"],
        "qa_failures": failed_rows,
        "evidence_issues": evidence_issue_rows(evidence),
    }


def fmt(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    full_run = (
        summary["full_expanded_ready"]
        and summary["qa_generated_count"] == summary["question_count"]
        and summary["qa_failed_count"] == 0
        and summary["evidence_result_count"] == summary["question_count"]
    )
    title = "PageIndex Expanded Retrieval Summary" if full_run else "PageIndex Expanded Partial Summary"
    scope = (
        "This report summarizes the complete 25-question PageIndex expanded retrieval-only run. "
        "It does not include LLM answer generation."
        if full_run
        else "This report summarizes the current partial PageIndex expanded retrieval-only run. "
        "It does not include LLM answer generation."
    )
    lines = [
        f"# {title}",
        "",
        f"Date: {summary['date']}",
        "",
        "## Scope",
        "",
        scope,
        "",
        "## Coverage",
        "",
        f"- Questions: `{summary['question_count']}`",
        f"- Unique source documents: `{summary['unique_doc_count']}`",
        f"- Documents with PageIndex structures and PDFs: `{summary['ready_doc_count']}`",
        f"- Missing PageIndex structures: `{summary['missing_structure_count']}`",
        f"- Missing PDFs: `{summary['missing_pdf_count']}`",
        f"- Runnable questions with current structures: `{summary['runnable_question_count']}`",
        f"- Retrieval-only QA generated: `{summary['qa_generated_count']}`",
        f"- Retrieval-only QA failed: `{summary['qa_failed_count']}`",
        f"- Full expanded PageIndex QA ready: `{summary['full_expanded_ready']}`",
        "",
        "## Retrieval Metrics",
        "",
        f"- Evaluated PageIndex results: `{summary['evidence_result_count']}`",
        f"- Average evidence recall: `{fmt(summary['average_evidence_recall'])}`",
        f"- Average citation precision: `{fmt(summary['average_citation_precision'])}`",
        "",
        "## Missing Structures",
        "",
    ]
    if payload["missing_structures"]:
        lines.extend(f"- `{doc_name}`" for doc_name in payload["missing_structures"])
    else:
        lines.append("No missing structures.")

    lines.extend(["", "## QA Failures", ""])
    if payload["qa_failures"]:
        for row in payload["qa_failures"]:
            lines.append(f"- `{row['question_id']}` / `{row['doc_name']}`: {row['error']}")
    else:
        lines.append("No QA failures.")

    lines.extend(
        [
            "",
            "## Evidence Issues",
            "",
            "| Question | Document | Recall | Precision | Gold pages | Predicted pages |",
            "|---|---|---:|---:|---|---|",
        ]
    )
    if payload["evidence_issues"]:
        for row in payload["evidence_issues"]:
            lines.append(
                "| {qid} | {doc} | {recall} | {precision} | {gold} | {predicted} |".format(
                    qid=f"`{row['question_id']}`",
                    doc=f"`{row['doc_name']}`",
                    recall=fmt(row["evidence_recall"]),
                    precision=fmt(row["citation_precision"]),
                    gold=", ".join(str(page) for page in row["gold_pages_one_indexed"]),
                    predicted=", ".join(str(page) for page in row["predicted_pages"]),
                )
            )
    else:
        lines.append("| none | none | n/a | n/a | n/a | n/a |")

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
        ]
    )
    if full_run:
        lines.extend(
            [
                "- PageIndex generated retrieval-only outputs for all `25 / 25` expanded questions with no QA failures.",
                "- The full expanded retrieval-only run reached `0.760` average evidence recall and `0.253` average citation precision.",
                "- The six evidence misses show that complete structure coverage alone is not enough; PageIndex ranking needs further work before strong expanded-set claims.",
                "- The next PageIndex benchmark step is expanded LLM answer generation, followed by evidence and answer evaluation against the same 25-question set.",
                "- The retained `expanded_partial_summary` file name is historical; the current contents summarize the full retrieval-only run.",
            ]
        )
    else:
        lines.extend(
            [
                "- The current PageIndex expanded run is a partial retrieval-only result, not a complete 25-question comparison.",
                f"- PageIndex generated retrieval outputs for `{summary['qa_generated_count']} / {summary['question_count']}` questions and reached `{fmt(summary['average_evidence_recall'])}` average evidence recall on those generated outputs.",
                "- Some questions remain blocked by missing structures, not by QA adapter failures.",
                "- Additional PageIndex indexing robustness is needed before running full expanded PageIndex LLM answer generation.",
            ]
        )
    lines.extend(
        [
            "",
            "## Source Artifacts",
            "",
            f"- Readiness: `{summary['readiness_report']}`",
            f"- QA manifest: `{summary['qa_manifest']}`",
            f"- Evidence evaluation: `{summary['evidence_eval']}`",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize PageIndex expanded retrieval-only results.")
    parser.add_argument("--readiness", type=Path, default=DEFAULT_READINESS)
    parser.add_argument("--qa-manifest", type=Path, default=DEFAULT_QA_MANIFEST)
    parser.add_argument("--evidence", type=Path, default=DEFAULT_EVIDENCE)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    args = parser.parse_args()

    payload = build_payload(args.readiness, args.qa_manifest, args.evidence)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text(render_markdown(payload), encoding="utf-8")
    print(f"PageIndex expanded retrieval JSON: {args.output_json}")
    print(f"PageIndex expanded retrieval report: {args.output_md}")


if __name__ == "__main__":
    main()
