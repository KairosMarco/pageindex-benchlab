from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class Citation(BaseModel):
    document_id: str
    page: int | None = None
    section: str | None = None
    text: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class RetrievalTraceStep(BaseModel):
    step: int
    action: str
    target: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class TokenUsage(BaseModel):
    input: int | None = None
    output: int | None = None
    total: int | None = None


class BenchmarkResult(BaseModel):
    method: str
    question_id: str
    question: str
    answer: str
    citations: list[Citation] = Field(default_factory=list)
    retrieval_trace: list[RetrievalTraceStep] = Field(default_factory=list)
    token_usage: TokenUsage = Field(default_factory=TokenUsage)
    latency_ms: int | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class GoldEvidence(BaseModel):
    document_id: str
    page_zero_indexed: int
    page_one_indexed: int
    text: str | None = None


class BenchmarkQuestion(BaseModel):
    question_id: str
    source_id: str
    dataset: Literal["financebench"]
    company: str
    doc_name: str
    doc_type: str | None = None
    doc_period: int | None = None
    question: str
    gold_answer: str
    gold_evidence: list[GoldEvidence]
    question_type: str | None = None
    question_reasoning: str | None = None
    pdf_url: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class EvidenceEvalResult(BaseModel):
    question_id: str
    gold_pages_zero_indexed: list[int]
    gold_pages_one_indexed: list[int]
    predicted_pages: list[int]
    evidence_recall: float
    citation_precision: float
    matched_pages: list[int]
    metadata: dict[str, Any] = Field(default_factory=dict)

