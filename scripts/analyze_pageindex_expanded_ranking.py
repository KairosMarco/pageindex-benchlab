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

from benchlab.schemas import BenchmarkQuestion  # noqa: E402
from pipelines.finance_rerank import financial_line_item_boost  # noqa: E402
from pipelines.pageindex.adapter import flatten_nodes, load_structure  # noqa: E402
from pipelines.pageindex.qa_adapter import (  # noqa: E402
    DEFAULT_MAX_PAGES,
    best_section_for_page,
    expanded_question_terms,
    extract_all_pages,
    keywords,
    page_sections,
    score_pages,
)


DEFAULT_QUESTIONS = ROOT / "datasets" / "financebench" / "expanded_questions_25.jsonl"
DEFAULT_PDF_DIR = ROOT / "datasets" / "raw" / "financebench" / "pdfs"
DEFAULT_STRUCTURE_DIR = ROOT / "reports" / "pageindex" / "structures"
DEFAULT_OUTPUT_JSON = ROOT / "reports" / "pageindex" / "pageindex_ranking_diagnostics.json"
DEFAULT_OUTPUT_MD = ROOT / "reports" / "pageindex" / "pageindex_ranking_diagnostics.md"


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def load_questions(path: Path) -> list[BenchmarkQuestion]:
    with path.open(encoding="utf-8") as f:
        return [BenchmarkQuestion.model_validate_json(line) for line in f if line.strip()]


def compact_text(value: str, max_chars: int = 240) -> str:
    text = " ".join(str(value or "").split()).replace("|", "/")
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3].rstrip() + "..."


def page_text_by_number(pages: list[dict[str, Any]]) -> dict[int, str]:
    return {int(page["page"]): page.get("text") or "" for page in pages}


def evaluate_pages(gold_pages: list[int], predicted_pages: list[int]) -> dict[str, Any]:
    gold = set(gold_pages)
    predicted = set(predicted_pages)
    matched = sorted(gold & predicted)
    return {
        "predicted_pages": predicted_pages,
        "matched_pages": matched,
        "evidence_recall": len(matched) / len(gold) if gold else 0.0,
        "citation_precision": len(matched) / len(predicted_pages) if predicted_pages else 0.0,
    }


def enrich_baseline_scores(
    baseline_scores: list[dict[str, Any]],
    *,
    max_rank: int | None = None,
) -> list[dict[str, Any]]:
    rows = []
    for rank, item in enumerate(baseline_scores, start=1):
        if max_rank is not None and rank > max_rank:
            break
        rows.append(
            {
                "rank": rank,
                "page": item["page"],
                "score": item["score"],
                "matched_page_terms": item.get("matched_page_terms", []),
                "matched_section_terms": item.get("matched_section_terms", []),
                "section": (item.get("section") or {}).get("title"),
            }
        )
    return rows


def legacy_score_pages(
    pages: list[dict[str, Any]],
    sections_by_page: dict[int, list[dict[str, Any]]],
    question: BenchmarkQuestion,
) -> list[dict[str, Any]]:
    """Reproduce the pre-finance-boost PageIndex page scorer for before/after diagnostics."""

    terms = expanded_question_terms(question)
    scored: list[dict[str, Any]] = []
    for page in pages:
        page_no = int(page["page"])
        page_text = page.get("text") or ""
        sections = sections_by_page.get(page_no, [])
        section_text = " ".join(node.get("title") or "" for node in sections)
        page_terms = keywords(page_text)
        section_terms = keywords(section_text)
        matched_page_terms = sorted(terms & page_terms)
        matched_section_terms = sorted(terms & section_terms)
        phrase_boost = 0
        lower_text = page_text.lower()
        combined_text = f"{section_text}\n{page_text}".lower()
        for phrase in (
            "cash flows",
            "statement of cash flows",
            "statements of operations",
            "statements of income",
            "balance sheets",
            "total assets",
            "gross profit",
            "cost of revenue",
            "legal proceedings",
            "non-gaap",
            "adjusted ebitda",
            "discontinued operations",
        ):
            phrase_terms = set(phrase.replace("-", " ").split())
            if phrase in lower_text and phrase_terms & terms:
                phrase_boost += 3
        if any(
            marker in combined_text
            for marker in (
                "consolidated statements of operations",
                "consolidated statements of earnings",
                "income statements",
            )
        ) and terms & {"cogs", "cost", "earnings", "gross", "income", "margin", "revenue", "sales"}:
            phrase_boost += 10
        if "total net sales" in combined_text and terms & {"revenue", "sales"}:
            phrase_boost += 8
        if (
            "gross profit" in combined_text
            and "revenue" in combined_text
            and "cost of sales" in combined_text
            and terms & {"gross", "margin", "margins"}
        ):
            phrase_boost += 10
        if "total cost of revenue" in combined_text and terms & {"cogs", "cost", "revenue"}:
            phrase_boost += 8
        if "consolidated balance sheets" in combined_text and terms & {"assets", "balance", "liabilities"}:
            phrase_boost += 10
        if "consolidated statements of cash flows" in combined_text and terms & {"cash", "flow", "flows"}:
            phrase_boost += 10

        score = len(matched_page_terms) * 3 + len(matched_section_terms) * 2 + phrase_boost
        if score:
            scored.append(
                {
                    "page": page_no,
                    "score": score,
                    "phrase_boost": phrase_boost,
                    "finance_boost": 0.0,
                    "finance_reasons": [],
                    "text": page_text,
                    "section": best_section_for_page(sections, terms),
                    "matched_page_terms": matched_page_terms,
                    "matched_section_terms": matched_section_terms,
                }
            )
    scored.sort(key=lambda item: (-item["score"], item["page"]))
    return scored


def ranked_lookup(scored: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    lookup = {}
    for rank, item in enumerate(scored, start=1):
        lookup[int(item["page"])] = {**item, "rank": rank}
    return lookup


def gold_page_rows(gold_pages: list[int], scored: list[dict[str, Any]]) -> list[dict[str, Any]]:
    lookup = ranked_lookup(scored)
    rows = []
    for page in gold_pages:
        item = lookup.get(page)
        finance_reasons = []
        if item:
            finance_reasons = item.get("finance_boost_reasons") or item.get("finance_reasons") or []
        rows.append(
            {
                "page": page,
                "rank": item.get("rank") if item else None,
                "score": item.get("score") if item else None,
                "base_score": item.get("base_score") if item else item.get("score") if item else None,
                "finance_boost": item.get("finance_boost") if item else None,
                "finance_reasons": finance_reasons,
                "matched_page_terms": item.get("matched_page_terms") if item else [],
                "matched_section_terms": item.get("matched_section_terms") if item else [],
                "section": (item.get("section") or {}).get("title") if item else None,
            }
        )
    return rows


def method_summary(rows: list[dict[str, Any]], method_key: str) -> dict[str, Any]:
    recalls = [row[method_key]["evidence_recall"] for row in rows]
    precisions = [row[method_key]["citation_precision"] for row in rows]
    full_hits = sum(1 for value in recalls if value == 1.0)
    zero_hits = sum(1 for value in recalls if value == 0.0)
    return {
        "question_count": len(rows),
        "full_hit_count": full_hits,
        "zero_hit_count": zero_hits,
        "average_evidence_recall": sum(recalls) / len(recalls) if recalls else 0.0,
        "average_citation_precision": sum(precisions) / len(precisions) if precisions else 0.0,
    }


def analyze_question(
    question: BenchmarkQuestion,
    *,
    pdf_dir: Path,
    structure_dir: Path,
    max_pages: int,
    top_n: int,
) -> dict[str, Any]:
    pdf_path = pdf_dir / f"{question.doc_name}.pdf"
    structure_path = structure_dir / f"{question.doc_name}_structure.json"
    structure = load_structure(structure_path)
    all_nodes = flatten_nodes(structure.get("structure", []))
    sections_by_page = page_sections(all_nodes)
    pages = extract_all_pages(pdf_path)

    baseline_scores = legacy_score_pages(pages, sections_by_page, question)
    finance_scores = score_pages(pages, sections_by_page, question)
    gold_pages = sorted({evidence.page_one_indexed for evidence in question.gold_evidence})
    page_text = page_text_by_number(pages)

    baseline_top = [item["page"] for item in baseline_scores[:max_pages]]
    finance_top = [item["page"] for item in finance_scores[:max_pages]]
    return {
        "question_id": question.question_id,
        "doc_name": question.doc_name,
        "question": question.question,
        "gold_pages_one_indexed": gold_pages,
        "baseline": {
            **evaluate_pages(gold_pages, baseline_top),
            "gold_pages": gold_page_rows(gold_pages, baseline_scores),
            "top_pages": enrich_baseline_scores(baseline_scores, max_rank=top_n),
        },
        "finance_boost_candidate": {
            **evaluate_pages(gold_pages, finance_top),
            "gold_pages": gold_page_rows(gold_pages, finance_scores),
            "top_pages": enrich_baseline_scores(finance_scores, max_rank=top_n),
        },
        "gold_page_snippets": {
            str(page): compact_text(page_text.get(page, ""), max_chars=360)
            for page in gold_pages
        },
    }


def render_gold_rank(rows: list[dict[str, Any]]) -> str:
    parts = []
    for row in rows:
        rank = row.get("rank")
        score = row.get("score")
        if rank is None:
            parts.append(f"p{row['page']}: unranked")
        else:
            parts.append(f"p{row['page']}: r{rank}, s{score:.1f}")
    return "; ".join(parts)


def render_top_pages(rows: list[dict[str, Any]]) -> str:
    return ", ".join(f"p{row['page']}:{row['score']:.1f}" for row in rows[:5])


def render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# PageIndex Expanded Ranking Diagnostics",
        "",
        f"Date: {summary['date']}",
        "",
        "## Scope",
        "",
        "This report diagnoses PageIndex page ranking on the expanded 25-question FinanceBench subset. It does not call an LLM and does not use gold evidence during scoring.",
        "",
        "## Summary",
        "",
        "| Method | Questions | Full hit count | Zero hit count | Evidence recall | Citation precision |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for key in ("baseline", "finance_boost_candidate"):
        row = summary[key]
        label = (
            "Legacy PageIndex scorer"
            if key == "baseline"
            else "Current scorer + finance line-item boost"
        )
        lines.append(
            "| {label} | {questions} | {full} | {zero} | {recall:.3f} | {precision:.3f} |".format(
                label=label,
                questions=row["question_count"],
                full=row["full_hit_count"],
                zero=row["zero_hit_count"],
                recall=row["average_evidence_recall"],
                precision=row["average_citation_precision"],
            )
        )

    lines.extend(
        [
            "",
            "## Baseline Miss Diagnostics",
            "",
            "| Question | Document | Gold pages | Baseline top pages | Baseline gold rank | Candidate top pages | Candidate gold rank |",
            "|---|---|---|---|---|---|---|",
        ]
    )
    for row in payload["baseline_misses"]:
        lines.append(
            "| `{qid}` | `{doc}` | {gold} | {base_top} | {base_rank} | {cand_top} | {cand_rank} |".format(
                qid=row["question_id"],
                doc=row["doc_name"],
                gold=", ".join(str(page) for page in row["gold_pages_one_indexed"]),
                base_top=render_top_pages(row["baseline"]["top_pages"]),
                base_rank=render_gold_rank(row["baseline"]["gold_pages"]),
                cand_top=render_top_pages(row["finance_boost_candidate"]["top_pages"]),
                cand_rank=render_gold_rank(row["finance_boost_candidate"]["gold_pages"]),
            )
        )

    lines.extend(
        [
            "",
            "## Candidate Improvements",
            "",
            "| Question | Baseline recall | Candidate recall | Gold pages | Candidate predicted pages | Finance reasons on gold pages |",
            "|---|---:|---:|---|---|---|",
        ]
    )
    for row in payload["candidate_improvements"]:
        reasons = []
        for gold_row in row["finance_boost_candidate"]["gold_pages"]:
            if gold_row.get("finance_reasons"):
                reasons.append(f"p{gold_row['page']}: {', '.join(gold_row['finance_reasons'])}")
        lines.append(
            "| `{qid}` | {base:.3f} | {cand:.3f} | {gold} | {predicted} | {reasons} |".format(
                qid=row["question_id"],
                base=row["baseline"]["evidence_recall"],
                cand=row["finance_boost_candidate"]["evidence_recall"],
                gold=", ".join(str(page) for page in row["gold_pages_one_indexed"]),
                predicted=", ".join(str(page) for page in row["finance_boost_candidate"]["predicted_pages"]),
                reasons=compact_text("; ".join(reasons), max_chars=220) or "n/a",
            )
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- The baseline reproduces the pre-fix PageIndex page scorer: question terms, section-title terms, and a small set of financial phrase boosts.",
            "- The current scorer adds the existing label-free finance line-item boost used by LlamaIndex diagnostics. It uses only question text and candidate page text.",
            "- This diagnostic explains the ranking effect of the current scorer without calling an LLM or using gold pages during scoring.",
            "- The current scorer has been validated by the full retrieval-only QA and evidence evaluation artifacts for the same 25-question subset.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    rows = [
        analyze_question(
            question,
            pdf_dir=args.pdf_dir,
            structure_dir=args.structure_dir,
            max_pages=args.max_pages,
            top_n=args.top_n,
        )
        for question in load_questions(args.questions)
    ]
    baseline_misses = [row for row in rows if row["baseline"]["evidence_recall"] < 1.0]
    candidate_improvements = [
        row
        for row in rows
        if row["finance_boost_candidate"]["evidence_recall"] > row["baseline"]["evidence_recall"]
    ]
    candidate_regressions = [
        row
        for row in rows
        if row["finance_boost_candidate"]["evidence_recall"] < row["baseline"]["evidence_recall"]
    ]
    return {
        "summary": {
            "date": date.today().isoformat(),
            "question_file": rel(args.questions),
            "structure_dir": rel(args.structure_dir),
            "pdf_dir": rel(args.pdf_dir),
            "max_pages": args.max_pages,
            "top_n": args.top_n,
            "baseline": method_summary(rows, "baseline"),
            "finance_boost_candidate": method_summary(rows, "finance_boost_candidate"),
            "baseline_miss_count": len(baseline_misses),
            "candidate_improvement_count": len(candidate_improvements),
            "candidate_regression_count": len(candidate_regressions),
        },
        "baseline_misses": baseline_misses,
        "candidate_improvements": candidate_improvements,
        "candidate_regressions": candidate_regressions,
        "per_question": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Diagnose PageIndex expanded page ranking.")
    parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS)
    parser.add_argument("--pdf-dir", type=Path, default=DEFAULT_PDF_DIR)
    parser.add_argument("--structure-dir", type=Path, default=DEFAULT_STRUCTURE_DIR)
    parser.add_argument("--max-pages", type=int, default=DEFAULT_MAX_PAGES)
    parser.add_argument("--top-n", type=int, default=12)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    args = parser.parse_args()

    payload = build_payload(args)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text(render_markdown(payload), encoding="utf-8")
    print(f"PageIndex ranking diagnostics JSON: {args.output_json}")
    print(f"PageIndex ranking diagnostics report: {args.output_md}")
    print(
        "baseline_recall={baseline:.3f} candidate_recall={candidate:.3f} improvements={improvements} regressions={regressions}".format(
            baseline=payload["summary"]["baseline"]["average_evidence_recall"],
            candidate=payload["summary"]["finance_boost_candidate"]["average_evidence_recall"],
            improvements=payload["summary"]["candidate_improvement_count"],
            regressions=payload["summary"]["candidate_regression_count"],
        )
    )


if __name__ == "__main__":
    main()
