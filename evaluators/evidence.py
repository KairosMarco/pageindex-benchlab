from __future__ import annotations

from benchlab.schemas import BenchmarkQuestion, BenchmarkResult, EvidenceEvalResult


def _citation_pages(result: BenchmarkResult) -> list[int]:
    pages = []
    for citation in result.citations:
        if citation.page is not None:
            pages.append(citation.page)
    return pages


def evaluate_evidence_pages(
    question: BenchmarkQuestion,
    result: BenchmarkResult,
    *,
    citation_page_base: int = 1,
) -> EvidenceEvalResult:
    """Evaluate page-level evidence recall and citation precision.

    FinanceBench evidence pages are zero-indexed. PageIndex structure output
    uses one-indexed page ranges in local demo outputs. The `citation_page_base`
    argument tells the evaluator how to normalize predicted citation pages.
    """

    gold_zero = sorted({ev.page_zero_indexed for ev in question.gold_evidence})
    gold_one = sorted({ev.page_one_indexed for ev in question.gold_evidence})
    predicted_raw = _citation_pages(result)
    predicted_zero = [
        page if citation_page_base == 0 else page - 1 for page in predicted_raw
    ]

    gold_set = set(gold_zero)
    predicted_set = set(predicted_zero)
    matched = sorted(gold_set & predicted_set)

    evidence_recall = len(matched) / len(gold_set) if gold_set else 0.0
    citation_precision = len(matched) / len(predicted_set) if predicted_set else 0.0

    return EvidenceEvalResult(
        question_id=question.question_id,
        gold_pages_zero_indexed=gold_zero,
        gold_pages_one_indexed=gold_one,
        predicted_pages=predicted_raw,
        evidence_recall=evidence_recall,
        citation_precision=citation_precision,
        matched_pages=matched,
        metadata={"citation_page_base": citation_page_base},
    )

