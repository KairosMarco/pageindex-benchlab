from __future__ import annotations

import json
from pathlib import Path


SELECTED_IDS = [
    "financebench_id_03029",
    "financebench_id_08135",
    "financebench_id_00995",
    "financebench_id_01279",
    "financebench_id_00685",
    "financebench_id_01091",
    "financebench_id_04209",
    "financebench_id_04700",
    "financebench_id_01163",
    "financebench_id_01928",
    "financebench_id_02049",
    "financebench_id_01488",
]


def load_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def main() -> None:
    root = Path(__file__).resolve().parent
    questions = load_jsonl(root / "financebench_open_source.jsonl")
    docs = {row["doc_name"]: row for row in load_jsonl(root / "financebench_document_information.jsonl")}
    by_id = {row["financebench_id"]: row for row in questions}

    selected = []
    for order, source_id in enumerate(SELECTED_IDS, start=1):
        row = by_id[source_id]
        doc = docs.get(row["doc_name"], {})
        evidence = []
        for ev in row.get("evidence", []):
            page_zero = ev.get("evidence_page_num")
            if page_zero is None:
                continue
            evidence.append(
                {
                    "document_id": ev.get("evidence_doc_name") or row["doc_name"],
                    "page_zero_indexed": page_zero,
                    "page_one_indexed": page_zero + 1,
                    "text": ev.get("evidence_text"),
                }
            )

        selected.append(
            {
                "question_id": f"fb_mvp_{order:03d}",
                "source_id": source_id,
                "dataset": "financebench",
                "company": row["company"],
                "doc_name": row["doc_name"],
                "doc_type": doc.get("doc_type"),
                "doc_period": doc.get("doc_period"),
                "question": row["question"],
                "gold_answer": row["answer"],
                "gold_evidence": evidence,
                "question_type": row.get("question_type"),
                "question_reasoning": row.get("question_reasoning"),
                "pdf_url": f"https://raw.githubusercontent.com/patronus-ai/financebench/main/pdfs/{row['doc_name']}.pdf",
                "metadata": {
                    "selection_reason": "MVP coverage across extraction, numerical reasoning, logical reasoning, and novel questions.",
                    "justification": row.get("justification"),
                },
            }
        )

    output = root / "mvp_questions.jsonl"
    with output.open("w", encoding="utf-8") as f:
        for row in selected:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"Wrote {len(selected)} questions to {output}")


if __name__ == "__main__":
    main()

