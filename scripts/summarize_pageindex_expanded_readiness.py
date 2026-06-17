from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


DEFAULT_QUESTIONS = ROOT / "datasets" / "financebench" / "expanded_questions_25.jsonl"
DEFAULT_STRUCTURE_DIR = ROOT / "reports" / "pageindex" / "structures"
DEFAULT_PDF_DIR = ROOT / "datasets" / "raw" / "financebench" / "pdfs"
DEFAULT_OUTPUT_JSON = ROOT / "reports" / "pageindex" / "expanded_readiness.json"
DEFAULT_OUTPUT_MD = ROOT / "reports" / "pageindex" / "expanded_readiness.md"


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def command_for_missing_docs(
    questions: Path,
    missing_docs: list[str],
    *,
    model: str,
    output_dir: Path,
    pdf_dir: Path,
) -> str:
    base = [
        "python",
        "scripts\\run_pageindex_mvp.py",
        "--questions",
        rel(questions),
        "--pdf-dir",
        rel(pdf_dir),
        "--output-dir",
        rel(output_dir),
        "--model",
        model,
        "--continue-on-error",
    ]
    for doc_name in missing_docs:
        base.extend(["--doc-name", doc_name])
    return " ".join(base)


def build_payload(
    *,
    questions: Path,
    structure_dir: Path,
    pdf_dir: Path,
    model: str,
) -> dict[str, Any]:
    question_rows = load_jsonl(questions)
    unique_docs = sorted({row["doc_name"] for row in question_rows})
    question_counts_by_doc: dict[str, int] = {}
    for row in question_rows:
        question_counts_by_doc[row["doc_name"]] = question_counts_by_doc.get(row["doc_name"], 0) + 1

    docs = []
    for doc_name in unique_docs:
        structure_path = structure_dir / f"{doc_name}_structure.json"
        pdf_path = pdf_dir / f"{doc_name}.pdf"
        docs.append(
            {
                "doc_name": doc_name,
                "question_count": question_counts_by_doc[doc_name],
                "has_structure": structure_path.exists(),
                "has_pdf": pdf_path.exists(),
                "structure_path": rel(structure_path),
                "pdf_path": rel(pdf_path),
                "structure_size_bytes": structure_path.stat().st_size if structure_path.exists() else None,
            }
        )

    missing_structures = [row["doc_name"] for row in docs if not row["has_structure"]]
    missing_pdfs = [row["doc_name"] for row in docs if not row["has_pdf"]]
    ready_docs = [row["doc_name"] for row in docs if row["has_structure"] and row["has_pdf"]]
    runnable_question_count = sum(row["question_count"] for row in docs if row["doc_name"] in ready_docs)

    return {
        "summary": {
            "date": date.today().isoformat(),
            "question_file": rel(questions),
            "question_count": len(question_rows),
            "unique_doc_count": len(unique_docs),
            "ready_doc_count": len(ready_docs),
            "missing_structure_count": len(missing_structures),
            "missing_pdf_count": len(missing_pdfs),
            "runnable_question_count": runnable_question_count,
            "full_expanded_ready": not missing_structures and not missing_pdfs,
            "structure_dir": rel(structure_dir),
            "pdf_dir": rel(pdf_dir),
            "model_for_indexing_command": model,
        },
        "docs": docs,
        "ready_docs": ready_docs,
        "missing_structures": missing_structures,
        "missing_pdfs": missing_pdfs,
        "commands": {
            "index_missing_structures": command_for_missing_docs(
                questions,
                missing_structures,
                model=model,
                output_dir=structure_dir,
                pdf_dir=pdf_dir,
            )
            if missing_structures
            else None,
            "run_expanded_pageindex_no_llm": (
                "python scripts\\run_pageindex_qa_mvp.py "
                f"--questions {rel(questions)} "
                f"--structure-dir {rel(structure_dir)} "
                "--output-dir reports\\pageindex\\qa_expanded_25 "
                "--manifest reports\\pageindex\\qa_expanded_25_manifest.json "
                "--no-llm --force --continue-on-error"
            ),
            "evaluate_expanded_pageindex_evidence": (
                "python scripts\\evaluate_evidence_mvp.py "
                f"--questions {rel(questions)} "
                "--results-dir reports\\pageindex\\qa_expanded_25 "
                "--output reports\\pageindex\\evidence_eval_qa_expanded_25.json "
                "--continue-on-error"
            ),
        },
    }


def render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# PageIndex Expanded Readiness",
        "",
        f"Date: {summary['date']}",
        "",
        "## Summary",
        "",
        f"- Question file: `{summary['question_file']}`",
        f"- Questions: `{summary['question_count']}`",
        f"- Unique source documents: `{summary['unique_doc_count']}`",
        f"- Documents with PageIndex structures and PDFs: `{summary['ready_doc_count']}`",
        f"- Missing PageIndex structures: `{summary['missing_structure_count']}`",
        f"- Missing PDFs: `{summary['missing_pdf_count']}`",
        f"- Runnable questions with current structures: `{summary['runnable_question_count']}`",
        f"- Full expanded PageIndex QA ready: `{summary['full_expanded_ready']}`",
        "",
        "## Missing Structures",
        "",
    ]
    if payload["missing_structures"]:
        for doc_name in payload["missing_structures"]:
            lines.append(f"- `{doc_name}`")
    else:
        lines.append("No missing structures.")

    lines.extend(
        [
            "",
            "## Document Coverage",
            "",
            "| Document | Questions | PDF | Structure |",
            "|---|---:|---|---|",
        ]
    )
    for row in payload["docs"]:
        lines.append(
            "| {doc} | {count} | {pdf} | {structure} |".format(
                doc=f"`{row['doc_name']}`",
                count=row["question_count"],
                pdf="yes" if row["has_pdf"] else "missing",
                structure="yes" if row["has_structure"] else "missing",
            )
        )

    lines.extend(["", "## Commands", ""])
    index_command = payload["commands"].get("index_missing_structures")
    if index_command:
        lines.extend(
            [
                "Index missing structures:",
                "",
                "```powershell",
                "$env:DEEPSEEK_API_KEY=\"YOUR_KEY\"",
                index_command,
                "```",
                "",
            ]
        )
    lines.extend(
        [
            "Run PageIndex expanded retrieval-only QA after all structures exist:",
            "",
            "```powershell",
            payload["commands"]["run_expanded_pageindex_no_llm"],
            payload["commands"]["evaluate_expanded_pageindex_evidence"],
            "```",
            "",
            "## Interpretation",
            "",
            "- PageIndex expanded 25-question QA is not ready for a full run until the missing structures are indexed.",
            "- The current 11 covered documents come from the 12-question MVP run. They are useful for smoke tests but do not cover the full expanded set.",
            "- The next PageIndex benchmark step is indexing the 13 missing expanded documents, then running retrieval-only QA and evidence evaluation before LLM answer generation.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize PageIndex readiness for expanded FinanceBench QA.")
    parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS)
    parser.add_argument("--structure-dir", type=Path, default=DEFAULT_STRUCTURE_DIR)
    parser.add_argument("--pdf-dir", type=Path, default=DEFAULT_PDF_DIR)
    parser.add_argument("--model", default="deepseek/deepseek-v4-pro")
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    args = parser.parse_args()

    payload = build_payload(
        questions=args.questions,
        structure_dir=args.structure_dir,
        pdf_dir=args.pdf_dir,
        model=args.model,
    )
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text(render_markdown(payload), encoding="utf-8")
    print(f"PageIndex expanded readiness JSON: {args.output_json}")
    print(f"PageIndex expanded readiness report: {args.output_md}")


if __name__ == "__main__":
    main()
