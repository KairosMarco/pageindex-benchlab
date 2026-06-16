from __future__ import annotations

import json
import re
from typing import Any

from litellm import completion

from benchlab.schemas import AnswerEvalResult, BenchmarkQuestion, BenchmarkResult


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def tokens(text: str) -> set[str]:
    stop = {
        "the",
        "and",
        "for",
        "with",
        "from",
        "what",
        "which",
        "that",
        "this",
        "will",
        "was",
        "were",
        "are",
        "is",
        "has",
        "have",
        "had",
        "been",
        "yes",
        "no",
        "million",
        "millions",
        "usd",
        "fiscal",
        "year",
        "fy",
        "page",
    }
    return {word for word in re.findall(r"[a-z][a-z0-9]+", normalize_text(text)) if len(word) > 2 and word not in stop}


def numbers(text: str) -> list[float]:
    values = []
    for raw in re.findall(r"[-+]?\$?\(?\d[\d,]*(?:\.\d+)?\)?%?", text):
        value = raw.replace("$", "").replace(",", "")
        negative = value.startswith("(") and value.endswith(")")
        value = value.strip("()").rstrip("%")
        try:
            parsed = float(value)
        except ValueError:
            continue
        values.append(-parsed if negative else parsed)
    return values


def number_matches(gold: float, predicted: float) -> bool:
    tolerance = max(0.05, abs(gold) * 0.005)
    return abs(gold - predicted) <= tolerance


def direction_label(text: str) -> str | None:
    normalized = normalize_text(text)
    if re.search(r"\bno\b|not reported|did not|does not|has not", normalized):
        return "no"
    if re.search(r"\byes\b|highest|most|operations|operating activities|consumer health|decreased|decline|consistent", normalized):
        return "yes"
    return None


def keyword_overlap_score(gold: str, predicted: str) -> float:
    gold_terms = tokens(gold)
    if not gold_terms:
        return 0.0
    predicted_terms = tokens(predicted)
    return len(gold_terms & predicted_terms) / len(gold_terms)


def evaluate_answer_heuristic(question: BenchmarkQuestion, result: BenchmarkResult) -> AnswerEvalResult:
    gold = question.gold_answer
    predicted = result.answer
    gold_nums = numbers(gold)
    pred_nums = numbers(predicted)
    overlap = keyword_overlap_score(gold, predicted)

    if gold_nums:
        matched = sum(1 for gold_num in gold_nums if any(number_matches(gold_num, pred_num) for pred_num in pred_nums))
        number_score = matched / len(gold_nums)
        if number_score == 1.0 and overlap >= 0.2:
            return AnswerEvalResult(
                question_id=question.question_id,
                score=1.0,
                verdict="correct",
                rationale="All gold numeric values were found in the predicted answer.",
                gold_answer=gold,
                predicted_answer=predicted,
                metadata={"mode": "heuristic", "number_score": number_score, "keyword_overlap": overlap},
            )
        if number_score > 0:
            return AnswerEvalResult(
                question_id=question.question_id,
                score=0.5,
                verdict="partial",
                rationale="At least one gold numeric value was found, but the answer may be incomplete.",
                gold_answer=gold,
                predicted_answer=predicted,
                metadata={"mode": "heuristic", "number_score": number_score, "keyword_overlap": overlap},
            )

    gold_direction = direction_label(gold)
    pred_direction = direction_label(predicted)
    if gold_direction and pred_direction:
        if gold_direction == pred_direction and overlap >= 0.25:
            return AnswerEvalResult(
                question_id=question.question_id,
                score=1.0,
                verdict="correct",
                rationale="The predicted answer matches the gold direction and key terms.",
                gold_answer=gold,
                predicted_answer=predicted,
                metadata={"mode": "heuristic", "keyword_overlap": overlap, "direction": gold_direction},
            )
        if gold_direction == pred_direction:
            return AnswerEvalResult(
                question_id=question.question_id,
                score=0.5,
                verdict="partial",
                rationale="The predicted answer matches the gold direction but has weak keyword overlap.",
                gold_answer=gold,
                predicted_answer=predicted,
                metadata={"mode": "heuristic", "keyword_overlap": overlap, "direction": gold_direction},
            )

    if overlap >= 0.75:
        verdict = "correct"
        score = 1.0
        rationale = "High keyword overlap with the gold answer."
    elif overlap >= 0.35:
        verdict = "partial"
        score = 0.5
        rationale = "Moderate keyword overlap with the gold answer."
    else:
        verdict = "incorrect"
        score = 0.0
        rationale = "Low keyword or numeric overlap with the gold answer."

    return AnswerEvalResult(
        question_id=question.question_id,
        score=score,
        verdict=verdict,
        rationale=rationale,
        gold_answer=gold,
        predicted_answer=predicted,
        metadata={"mode": "heuristic", "keyword_overlap": overlap},
    )


def extract_json(text: str) -> dict[str, Any]:
    raw = text.strip()
    fenced = re.search(r"```(?:json)?\s*(.*?)\s*```", raw, re.DOTALL)
    if fenced:
        raw = fenced.group(1).strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}")
        if start >= 0 and end > start:
            return json.loads(raw[start : end + 1])
        raise


def evaluate_answer_llm(
    question: BenchmarkQuestion,
    result: BenchmarkResult,
    *,
    model: str,
) -> AnswerEvalResult:
    prompt = f"""You are evaluating a financial QA answer.
Compare the predicted answer against the gold answer. Ignore wording differences.
Mark:
- correct: the predicted answer fully answers the question and matches the gold answer.
- partial: the predicted answer is directionally right but incomplete or missing important detail.
- incorrect: the predicted answer is wrong, unsupported, or materially different.

Return only JSON with keys: verdict, score, rationale.
score must be 1.0 for correct, 0.5 for partial, 0.0 for incorrect.

QUESTION:
{question.question}

GOLD ANSWER:
{question.gold_answer}

PREDICTED ANSWER:
{result.answer}
"""
    response = completion(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    content = response.choices[0].message.content
    payload = extract_json(content)
    verdict = payload.get("verdict", "incorrect")
    if verdict not in {"correct", "partial", "incorrect"}:
        verdict = "incorrect"
    score = float(payload.get("score", {"correct": 1.0, "partial": 0.5, "incorrect": 0.0}[verdict]))
    if verdict == "correct":
        score = 1.0
    elif verdict == "partial":
        score = 0.5
    else:
        score = 0.0
    return AnswerEvalResult(
        question_id=question.question_id,
        score=score,
        verdict=verdict,
        rationale=str(payload.get("rationale", "")).strip() or "No rationale returned.",
        gold_answer=question.gold_answer,
        predicted_answer=result.answer,
        metadata={"mode": "llm_judge", "model": model},
    )
