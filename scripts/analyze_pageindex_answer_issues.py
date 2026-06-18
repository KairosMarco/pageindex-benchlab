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

from benchlab.schemas import BenchmarkQuestion, BenchmarkResult  # noqa: E402


DEFAULT_QUESTIONS = ROOT / "datasets" / "financebench" / "expanded_questions_25.jsonl"
DEFAULT_RESULTS_DIR = ROOT / "reports" / "pageindex" / "qa_llm_expanded_25"
DEFAULT_EVIDENCE_EVAL = ROOT / "reports" / "pageindex" / "evidence_eval_qa_llm_expanded_25.json"
DEFAULT_ANSWER_EVAL = ROOT / "reports" / "pageindex" / "answer_eval_qa_llm_expanded_25.json"
DEFAULT_PROMPT_VARIANTS = ROOT / "reports" / "finance_prompt_variant_summary.json"
DEFAULT_OUTPUT_JSON = ROOT / "reports" / "pageindex" / "pageindex_answer_issue_analysis.json"
DEFAULT_OUTPUT_MD = ROOT / "reports" / "pageindex" / "pageindex_answer_issue_analysis.md"


ISSUE_ANALYSIS = {
    "fb_exp_019": {
        "issue_type": "rounding_or_judge_strictness",
        "failure_mode": "The retrieved evidence is correct and the answer extracts the exact table value, but the judge compares `$0.389 billion` against the rounded gold answer `$0.40`.",
        "recommended_action": "Add an evaluator tolerance or answer-format policy for USD billions when the source table reports millions and the gold answer is rounded.",
    },
    "fb_exp_020": {
        "issue_type": "finance_concept_definition",
        "failure_mode": "The retrieved evidence is correct, but the answer uses a narrow fixed-asset ratio interpretation while the gold answer treats low ROA and the broader goodwill-heavy asset base as capital intensity evidence.",
        "recommended_action": "Add prompt guidance or benchmark notes that capital intensity questions may require ROA and broad asset-base reasoning, not only PP&E divided by total assets.",
    },
}


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_json_if_exists(path: Path) -> Any | None:
    return load_json(path) if path.exists() else None


def load_questions(path: Path) -> dict[str, BenchmarkQuestion]:
    with path.open(encoding="utf-8") as f:
        return {
            question.question_id: question
            for question in (BenchmarkQuestion.model_validate_json(line) for line in f if line.strip())
        }


def compact(value: Any, max_chars: int = 480) -> str:
    text = " ".join(str(value or "").split()).replace("|", "/")
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3].rstrip() + "..."


def row_by_question(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["question_id"]: row for row in payload.get("per_question", [])}


def non_correct_question_ids(answer_eval: dict[str, Any]) -> list[str]:
    return [
        row["question_id"]
        for row in answer_eval.get("per_question", [])
        if row.get("verdict") and row.get("verdict") != "correct"
    ]


def prompt_variant_outcomes(payload: dict[str, Any] | None, question_id: str) -> list[dict[str, Any]]:
    if not payload:
        return []
    rows = []
    for group_key in ("variants", "probes"):
        for run in payload.get(group_key, []):
            selected = run.get("selected_question_outcomes") or {}
            verdict = selected.get(question_id)
            for issue in run.get("issue_rows", []):
                if issue.get("question_id") == question_id:
                    verdict = issue.get("verdict")
            if verdict:
                rows.append(
                    {
                        "run_type": group_key[:-1],
                        "key": run.get("key"),
                        "label": run.get("label"),
                        "verdict": verdict,
                        "answer_accuracy": run.get("answer_accuracy"),
                        "average_total_tokens": run.get("average_total_tokens"),
                    }
                )
    return rows


def build_issue_row(
    *,
    question_id: str,
    question: BenchmarkQuestion,
    result: BenchmarkResult,
    evidence_row: dict[str, Any],
    answer_row: dict[str, Any],
    prompt_variants: dict[str, Any] | None,
) -> dict[str, Any]:
    analysis = ISSUE_ANALYSIS.get(
        question_id,
        {
            "issue_type": "answer_generation_or_judge_case",
            "failure_mode": "The answer judge marked this case as non-correct after evidence retrieval.",
            "recommended_action": "Inspect the question, gold answer, predicted answer, and judge rationale before changing retrieval logic.",
        },
    )
    matched_pages_zero = evidence_row.get("matched_pages") or []
    matched_pages_one = [int(page) + 1 for page in matched_pages_zero]
    gold_pages = evidence_row.get("gold_pages_one_indexed") or [
        evidence.page_one_indexed for evidence in question.gold_evidence
    ]
    selected_pages = result.metadata.get("selected_pages_one_indexed") or [
        citation.page for citation in result.citations if citation.page is not None
    ]
    return {
        "question_id": question_id,
        "doc_name": question.doc_name,
        "question": question.question,
        "issue_type": analysis["issue_type"],
        "failure_mode": analysis["failure_mode"],
        "recommended_action": analysis["recommended_action"],
        "gold_answer": question.gold_answer,
        "predicted_answer": result.answer,
        "judge_verdict": answer_row.get("verdict"),
        "judge_score": answer_row.get("score"),
        "judge_rationale": answer_row.get("rationale"),
        "gold_pages_one_indexed": gold_pages,
        "selected_pages_one_indexed": selected_pages,
        "matched_pages_zero_indexed": matched_pages_zero,
        "matched_pages_one_indexed": matched_pages_one,
        "evidence_recall": evidence_row.get("evidence_recall"),
        "citation_precision": evidence_row.get("citation_precision"),
        "retrieval_succeeded": evidence_row.get("evidence_recall") == 1.0,
        "token_usage": result.token_usage.model_dump(),
        "latency_ms": result.latency_ms,
        "prompt_variant_outcomes": prompt_variant_outcomes(prompt_variants, question_id),
        "result_path": rel(DEFAULT_RESULTS_DIR / f"{question_id}.json"),
    }


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    questions = load_questions(args.questions)
    answer_eval = load_json(args.answer_eval)
    evidence_eval = load_json(args.evidence_eval)
    prompt_variants = load_json_if_exists(args.prompt_variants)
    answer_by_id = row_by_question(answer_eval)
    evidence_by_id = row_by_question(evidence_eval)
    issue_ids = args.question_id or non_correct_question_ids(answer_eval)
    rows = []
    for question_id in issue_ids:
        result_path = args.results_dir / f"{question_id}.json"
        result = BenchmarkResult.model_validate_json(result_path.read_text(encoding="utf-8"))
        rows.append(
            build_issue_row(
                question_id=question_id,
                question=questions[question_id],
                result=result,
                evidence_row=evidence_by_id.get(question_id, {}),
                answer_row=answer_by_id.get(question_id, {}),
                prompt_variants=prompt_variants,
            )
        )

    return {
        "summary": {
            "date": date.today().isoformat(),
            "method": "pageindex_tree_qa_llm",
            "question_file": rel(args.questions),
            "results_dir": rel(args.results_dir),
            "evidence_eval": rel(args.evidence_eval),
            "answer_eval": rel(args.answer_eval),
            "prompt_variant_summary": rel(args.prompt_variants) if args.prompt_variants.exists() else None,
            "issue_count": len(rows),
            "issue_ids": [row["question_id"] for row in rows],
            "retrieval_succeeded_count": sum(1 for row in rows if row["retrieval_succeeded"]),
        },
        "issues": rows,
    }


def render_variant_table(rows: list[dict[str, Any]]) -> list[str]:
    lines = [
        "| Run | Verdict | Accuracy | Avg tokens |",
        "|---|---|---:|---:|",
    ]
    if not rows:
        lines.append("| none | n/a | n/a | n/a |")
        return lines
    for row in rows:
        lines.append(
            "| {label} | {verdict} | {accuracy} | {tokens} |".format(
                label=row.get("label") or row.get("key"),
                verdict=row.get("verdict"),
                accuracy=fmt(row.get("answer_accuracy")),
                tokens=fmt(row.get("average_total_tokens")),
            )
        )
    return lines


def fmt(value: Any, digits: int = 3) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# PageIndex Expanded Answer Issue Analysis",
        "",
        f"Date: {summary['date']}",
        "",
        "## Scope",
        "",
        "This report analyzes the non-correct PageIndex answer verdicts after the expanded retrieval fix. It does not call an LLM.",
        "",
        f"- Question file: `{summary['question_file']}`",
        f"- Results: `{summary['results_dir']}`",
        f"- Answer eval: `{summary['answer_eval']}`",
        f"- Evidence eval: `{summary['evidence_eval']}`",
        "",
        "## Summary",
        "",
        f"- Non-correct PageIndex answer cases: `{summary['issue_count']}`",
        f"- Retrieval succeeded for those cases: `{summary['retrieval_succeeded_count']} / {summary['issue_count']}`",
        f"- Issue ids: `{', '.join(summary['issue_ids']) or 'none'}`",
        "",
        "| Question | Document | Verdict | Evidence recall | Citation precision | Issue type | Recommended action |",
        "|---|---|---|---:|---:|---|---|",
    ]
    for row in payload["issues"]:
        lines.append(
            "| `{qid}` | `{doc}` | {verdict} | {recall} | {precision} | {issue_type} | {action} |".format(
                qid=row["question_id"],
                doc=row["doc_name"],
                verdict=row["judge_verdict"],
                recall=fmt(row["evidence_recall"]),
                precision=fmt(row["citation_precision"]),
                issue_type=row["issue_type"],
                action=compact(row["recommended_action"], max_chars=220),
            )
        )

    for row in payload["issues"]:
        lines.extend(
            [
                "",
                f"## {row['question_id']} - {row['issue_type']}",
                "",
                f"- Document: `{row['doc_name']}`",
                f"- Evidence recall: `{fmt(row['evidence_recall'])}`",
                f"- Gold pages: `{', '.join(str(page) for page in row['gold_pages_one_indexed'])}`",
                f"- Selected pages: `{', '.join(str(page) for page in row['selected_pages_one_indexed'])}`",
                f"- Matched pages: `{', '.join(str(page) for page in row['matched_pages_one_indexed'])}`",
                f"- Matched pages zero-indexed: `{', '.join(str(page) for page in row['matched_pages_zero_indexed'])}`",
                "",
                "Question:",
                "",
                f"> {compact(row['question'], max_chars=700)}",
                "",
                "Gold answer:",
                "",
                f"> {compact(row['gold_answer'], max_chars=700)}",
                "",
                "Predicted answer:",
                "",
                f"> {compact(row['predicted_answer'], max_chars=900)}",
                "",
                "Judge rationale:",
                "",
                f"> {compact(row['judge_rationale'], max_chars=900)}",
                "",
                "Diagnosis:",
                "",
                f"- {row['failure_mode']}",
                f"- Recommended next action: {row['recommended_action']}",
                "",
                "Prompt-variant evidence:",
                "",
            ]
        )
        lines.extend(render_variant_table(row["prompt_variant_outcomes"]))

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- These are not current PageIndex retrieval failures; both cases retrieved the gold evidence pages.",
            "- `fb_exp_019` should be treated as a rounding or judge-policy case before changing retrieval or prompts.",
            "- `fb_exp_020` is a genuine finance-reasoning case shared across methods: models often choose a fixed-asset ratio definition while the gold answer uses ROA and broad asset intensity.",
            "- The next useful experiment is a PageIndex answer-prompt ablation mirroring the existing LlamaIndex `finance_reasoning_v2/v3` probes.",
            "",
            "## Source Artifacts",
            "",
            f"- PageIndex LLM diagnostics: `reports\\pageindex_expanded_llm_diagnostics.json`",
            f"- Finance prompt variants: `{summary['prompt_variant_summary']}`",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze non-correct PageIndex expanded answer cases.")
    parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS)
    parser.add_argument("--results-dir", type=Path, default=DEFAULT_RESULTS_DIR)
    parser.add_argument("--evidence-eval", type=Path, default=DEFAULT_EVIDENCE_EVAL)
    parser.add_argument("--answer-eval", type=Path, default=DEFAULT_ANSWER_EVAL)
    parser.add_argument("--prompt-variants", type=Path, default=DEFAULT_PROMPT_VARIANTS)
    parser.add_argument("--question-id", action="append", help="Analyze only the given non-correct question id.")
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    args = parser.parse_args()

    payload = build_payload(args)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text(render_markdown(payload), encoding="utf-8")
    print(f"PageIndex answer issue analysis JSON: {args.output_json}")
    print(f"PageIndex answer issue analysis report: {args.output_md}")
    print(
        "issue_count={issue_count} retrieval_succeeded={retrieval_succeeded_count}".format(
            **payload["summary"]
        )
    )


if __name__ == "__main__":
    main()
