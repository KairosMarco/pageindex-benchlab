from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchlab.schemas import BenchmarkQuestion, BenchmarkResult  # noqa: E402
from evaluators.answer import evaluate_answer_heuristic, evaluate_answer_llm  # noqa: E402


DEFAULT_QUESTIONS = ROOT / "datasets" / "financebench" / "mvp_questions.jsonl"
DEFAULT_RESULTS_DIR = ROOT / "reports" / "pageindex" / "qa_llm"
DEFAULT_OUTPUT = ROOT / "reports" / "pageindex" / "answer_eval.json"


def load_questions(path: Path) -> dict[str, BenchmarkQuestion]:
    with path.open(encoding="utf-8") as f:
        return {
            question.question_id: question
            for question in (BenchmarkQuestion.model_validate_json(line) for line in f if line.strip())
        }


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def average(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def has_model_key() -> bool:
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


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate answer accuracy for MVP benchmark results.")
    parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS)
    parser.add_argument("--results-dir", type=Path, default=DEFAULT_RESULTS_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--glob", default="*.json")
    parser.add_argument("--mode", choices=("heuristic", "llm"), default="heuristic")
    parser.add_argument("--model", default=None, help="LiteLLM model used when --mode llm is selected.")
    parser.add_argument("--question-id", action="append", help="Evaluate only the given question id. Can be repeated.")
    parser.add_argument("--continue-on-error", action="store_true")
    args = parser.parse_args()

    if args.mode == "llm" and not args.model:
        raise SystemExit("--model is required when --mode llm is selected.")
    if args.mode == "llm" and not has_model_key():
        raise SystemExit("No model API key found in the current shell.")

    questions = load_questions(args.questions)
    result_paths = sorted(args.results_dir.glob(args.glob))
    if args.question_id:
        requested = set(args.question_id)
        result_paths = [path for path in result_paths if path.stem in requested]
        missing = sorted(requested - {path.stem for path in result_paths})
        if missing:
            raise SystemExit(f"Result JSON not found for question_id: {missing}")

    evaluations = []
    failures: list[dict[str, str]] = []
    for result_path in result_paths:
        try:
            result = BenchmarkResult.model_validate_json(result_path.read_text(encoding="utf-8"))
            question = questions[result.question_id]
            if args.mode == "llm":
                evaluation = evaluate_answer_llm(question, result, model=args.model or "")
            else:
                evaluation = evaluate_answer_heuristic(question, result)
            row = evaluation.model_dump()
            row["metadata"] = {
                **row.get("metadata", {}),
                "result_path": rel(result_path),
                "method": result.method,
                "doc_name": question.doc_name,
            }
            evaluations.append(row)
        except Exception as exc:
            failures.append({"result_path": rel(result_path), "error": str(exc)})
            if not args.continue_on_error:
                raise

    scores = [row["score"] for row in evaluations]
    verdict_counts = {
        verdict: sum(1 for row in evaluations if row["verdict"] == verdict)
        for verdict in ("correct", "partial", "incorrect")
    }
    payload: dict[str, Any] = {
        "summary": {
            "result_count": len(evaluations),
            "failure_count": len(failures),
            "average_answer_score": average(scores),
            "accuracy": verdict_counts["correct"] / len(evaluations) if evaluations else 0.0,
            "verdict_counts": verdict_counts,
            "mode": args.mode,
            "model": args.model,
            "results_dir": rel(args.results_dir),
        },
        "per_question": evaluations,
        "failures": failures,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Answer evaluation: {args.output}")
    print(
        "result_count={result_count} failure_count={failure_count} "
        "avg_score={average_answer_score:.3f} accuracy={accuracy:.3f} verdicts={verdict_counts}".format(
            **payload["summary"]
        )
    )


if __name__ == "__main__":
    main()
