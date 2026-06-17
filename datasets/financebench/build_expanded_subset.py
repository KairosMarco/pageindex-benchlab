from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DEFAULT_TARGET_COUNT = 25
DEFAULT_MAX_PER_DOC = 2
DEFAULT_MAX_PER_COMPANY = 3
QUESTION_TYPE_ORDER = ("metrics-generated", "domain-relevant", "novel-generated")


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def normalize_reasoning(value: str | None) -> str:
    if value is None:
        return "<missing>"
    stripped = value.strip()
    return stripped or "<missing>"


def pdf_url(doc_name: str) -> str:
    return f"https://raw.githubusercontent.com/patronus-ai/financebench/main/pdfs/{doc_name}.pdf"


def normalize_evidence(row: dict[str, Any]) -> list[dict[str, Any]]:
    evidence = []
    for item in row.get("evidence", []):
        page_zero = item.get("evidence_page_num")
        if page_zero is None:
            continue
        document_id = item.get("evidence_doc_name") or item.get("doc_name") or row["doc_name"]
        evidence.append(
            {
                "document_id": document_id,
                "page_zero_indexed": page_zero,
                "page_one_indexed": page_zero + 1,
                "text": item.get("evidence_text"),
            }
        )
    return evidence


def normalize_source_row(
    row: dict[str, Any],
    doc: dict[str, Any],
    *,
    question_id: str,
    selection_origin: str,
    selection_reason: str,
    source_mvp_question_id: str | None = None,
) -> dict[str, Any]:
    metadata = {
        "selection_origin": selection_origin,
        "selection_reason": selection_reason,
        "justification": row.get("justification"),
    }
    if source_mvp_question_id:
        metadata["source_mvp_question_id"] = source_mvp_question_id

    return {
        "question_id": question_id,
        "source_id": row["financebench_id"],
        "dataset": "financebench",
        "company": row["company"],
        "doc_name": row["doc_name"],
        "doc_type": doc.get("doc_type"),
        "doc_period": doc.get("doc_period"),
        "question": row["question"],
        "gold_answer": row["answer"],
        "gold_evidence": normalize_evidence(row),
        "question_type": row.get("question_type"),
        "question_reasoning": row.get("question_reasoning"),
        "pdf_url": pdf_url(row["doc_name"]),
        "metadata": metadata,
    }


def target_type_counts(target_count: int) -> dict[str, int]:
    base, remainder = divmod(target_count, len(QUESTION_TYPE_ORDER))
    return {
        question_type: base + (1 if index < remainder else 0)
        for index, question_type in enumerate(QUESTION_TYPE_ORDER)
    }


def selected_counts(rows: list[dict[str, Any]]) -> dict[str, Counter[str]]:
    return {
        "question_type": Counter(row.get("question_type") or "<missing>" for row in rows),
        "reasoning": Counter(normalize_reasoning(row.get("question_reasoning")) for row in rows),
        "doc": Counter(row["doc_name"] for row in rows),
        "company": Counter(row["company"] for row in rows),
    }


def choose_candidate(
    candidates: list[dict[str, Any]],
    selected_source_ids: set[str],
    counts: dict[str, Counter[str]],
    *,
    question_type: str,
    max_per_doc: int,
    max_per_company: int,
    enforce_limits: bool,
) -> dict[str, Any] | None:
    available = []
    for row in candidates:
        if row["financebench_id"] in selected_source_ids:
            continue
        if row.get("question_type") != question_type:
            continue
        if enforce_limits and counts["doc"][row["doc_name"]] >= max_per_doc:
            continue
        if enforce_limits and counts["company"][row["company"]] >= max_per_company:
            continue
        available.append(row)

    if not available:
        return None

    def score(row: dict[str, Any]) -> tuple[int, int, int, int, str, str]:
        reasoning = normalize_reasoning(row.get("question_reasoning"))
        evidence_page_count = len({item.get("evidence_page_num") for item in row.get("evidence", [])})
        return (
            counts["reasoning"][reasoning],
            counts["doc"][row["doc_name"]],
            counts["company"][row["company"]],
            abs(evidence_page_count - 1),
            row["doc_name"],
            row["financebench_id"],
        )

    return sorted(available, key=score)[0]


def add_selected(
    selected: list[dict[str, Any]],
    selected_source_ids: set[str],
    counts: dict[str, Counter[str]],
    row: dict[str, Any],
) -> None:
    selected.append(row)
    selected_source_ids.add(row["source_id"])
    counts["question_type"][row.get("question_type") or "<missing>"] += 1
    counts["reasoning"][normalize_reasoning(row.get("question_reasoning"))] += 1
    counts["doc"][row["doc_name"]] += 1
    counts["company"][row["company"]] += 1


def build_subset(
    raw_questions: list[dict[str, Any]],
    docs_by_name: dict[str, dict[str, Any]],
    *,
    target_count: int,
    mvp_questions: list[dict[str, Any]],
    include_mvp: bool,
    max_per_doc: int,
    max_per_company: int,
) -> list[dict[str, Any]]:
    raw_by_id = {row["financebench_id"]: row for row in raw_questions}
    selected: list[dict[str, Any]] = []
    selected_source_ids: set[str] = set()
    counts = selected_counts([])

    if include_mvp:
        for mvp_row in mvp_questions:
            raw_row = raw_by_id[mvp_row["source_id"]]
            doc = docs_by_name.get(raw_row["doc_name"], {})
            normalized = normalize_source_row(
                raw_row,
                doc,
                question_id=mvp_row["question_id"],
                selection_origin="mvp_seed",
                selection_reason="Preserved from the committed 12-question MVP subset for continuity.",
                source_mvp_question_id=mvp_row["question_id"],
            )
            add_selected(selected, selected_source_ids, counts, normalized)

    targets = target_type_counts(target_count)
    next_index = len(selected) + 1

    while len(selected) < target_count:
        made_progress = False
        needed_types = [
            question_type
            for question_type in QUESTION_TYPE_ORDER
            if counts["question_type"][question_type] < targets[question_type]
        ]
        if not needed_types:
            needed_types = list(QUESTION_TYPE_ORDER)

        for question_type in needed_types:
            if len(selected) >= target_count:
                break
            candidate = choose_candidate(
                raw_questions,
                selected_source_ids,
                counts,
                question_type=question_type,
                max_per_doc=max_per_doc,
                max_per_company=max_per_company,
                enforce_limits=True,
            )
            if candidate is None:
                candidate = choose_candidate(
                    raw_questions,
                    selected_source_ids,
                    counts,
                    question_type=question_type,
                    max_per_doc=max_per_doc,
                    max_per_company=max_per_company,
                    enforce_limits=False,
                )
            if candidate is None:
                continue

            doc = docs_by_name.get(candidate["doc_name"], {})
            selected_row = normalize_source_row(
                candidate,
                doc,
                question_id=f"fb_exp_{next_index:03d}",
                selection_origin="expanded_balanced",
                selection_reason=(
                    "Deterministically selected to balance question_type coverage, "
                    "reasoning labels, companies, and source documents."
                ),
            )
            add_selected(selected, selected_source_ids, counts, selected_row)
            next_index += 1
            made_progress = True

        if not made_progress:
            raise RuntimeError(f"Could not select {target_count} questions from the available source rows.")

    return selected


def summarize(rows: list[dict[str, Any]], raw_questions: list[dict[str, Any]], args: argparse.Namespace) -> dict[str, Any]:
    counts = selected_counts(rows)
    return {
        "summary": {
            "source_question_count": len(raw_questions),
            "selected_question_count": len(rows),
            "include_mvp": args.include_mvp,
            "target_count": args.target_count,
            "max_per_doc": args.max_per_doc,
            "max_per_company": args.max_per_company,
            "question_type_counts": dict(sorted(counts["question_type"].items())),
            "reasoning_counts": dict(sorted(counts["reasoning"].items())),
            "doc_counts": dict(sorted(counts["doc"].items())),
            "company_counts": dict(sorted(counts["company"].items())),
        },
        "selected_questions": [
            {
                "question_id": row["question_id"],
                "source_id": row["source_id"],
                "company": row["company"],
                "doc_name": row["doc_name"],
                "question_type": row.get("question_type"),
                "question_reasoning": row.get("question_reasoning"),
                "selection_origin": row["metadata"].get("selection_origin"),
                "selection_reason": row["metadata"].get("selection_reason"),
            }
            for row in rows
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a deterministic expanded FinanceBench subset.")
    parser.add_argument("--target-count", type=int, default=DEFAULT_TARGET_COUNT)
    parser.add_argument("--source-questions", type=Path, default=ROOT / "financebench_open_source.jsonl")
    parser.add_argument("--source-docs", type=Path, default=ROOT / "financebench_document_information.jsonl")
    parser.add_argument("--mvp-questions", type=Path, default=ROOT / "mvp_questions.jsonl")
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--manifest", type=Path, default=None)
    parser.add_argument("--max-per-doc", type=int, default=DEFAULT_MAX_PER_DOC)
    parser.add_argument("--max-per-company", type=int, default=DEFAULT_MAX_PER_COMPANY)
    parser.add_argument("--exclude-mvp", dest="include_mvp", action="store_false")
    parser.set_defaults(include_mvp=True)
    args = parser.parse_args()

    if args.target_count <= 0:
        raise SystemExit("--target-count must be positive.")

    output = args.output or ROOT / f"expanded_questions_{args.target_count}.jsonl"
    manifest = args.manifest or ROOT / f"expanded_questions_{args.target_count}_manifest.json"

    raw_questions = load_jsonl(args.source_questions)
    docs_by_name = {row["doc_name"]: row for row in load_jsonl(args.source_docs)}
    mvp_questions = load_jsonl(args.mvp_questions) if args.include_mvp else []
    if args.include_mvp and args.target_count < len(mvp_questions):
        raise SystemExit("--target-count must be at least the MVP question count when MVP seeding is enabled.")

    selected = build_subset(
        raw_questions,
        docs_by_name,
        target_count=args.target_count,
        mvp_questions=mvp_questions,
        include_mvp=args.include_mvp,
        max_per_doc=args.max_per_doc,
        max_per_company=args.max_per_company,
    )
    write_jsonl(output, selected)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps(summarize(selected, raw_questions, args), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(selected)} questions to {output}")
    print(f"Wrote manifest to {manifest}")


if __name__ == "__main__":
    main()
