# Stage 1 Next Baseline Plan

Date: 2026-06-16

## Goal

Strengthen the current Stage 1 comparison by replacing dependency-light TF-IDF Vector/Hybrid MVPs with embedding-based LlamaIndex baselines and a stronger reranker.

The goal is not to prove PageIndex is better by assumption. The goal is to run stronger competing baselines under the same schema, same questions, same answer model, same evidence evaluator, and same answer judge.

## Current Evidence Position

The current 12-question MVP supports only narrow claims:

- PageIndex, Vector RAG, and Hybrid RAG reached `1.000` page-level evidence recall on the MVP subset.
- Long-context reached `1.000` answer accuracy but used far more tokens.
- Vector RAG had one answer failure even with the correct evidence page.
- Hybrid RAG matched PageIndex's current evidence recall and answer accuracy on this subset.

The current MVP does not support broad superiority claims across all FinanceBench, legal documents, medical documents, or general long-document QA.

## Stronger Baseline Requirements

### Vector RAG With LlamaIndex

Required behavior:

```text
PDF pages -> chunks -> embedding index -> top-k retrieval -> reranker -> LLM answer -> BenchmarkResult
```

Minimum controls:

- Same 12 MVP questions first.
- Same PDF files.
- Same output schema.
- Same LLM answer model as current runs.
- Same evidence and answer evaluators.
- Record embedding model, reranker model, chunk size, overlap, top-k, latency, and token usage.

### Hybrid RAG With LlamaIndex

Required behavior:

```text
PDF pages -> chunks -> BM25 retriever + vector retriever -> fusion -> reranker -> LLM answer -> BenchmarkResult
```

Minimum controls:

- Same chunking as the Vector RAG LlamaIndex baseline unless explicitly testing chunking.
- Same LLM answer model as current runs.
- Same evidence and answer evaluators.
- Record BM25 top-k, vector top-k, fusion strategy, reranker model, latency, and token usage.

## Data Required Before Making Claims

For each method and each question:

- predicted citation pages
- matched gold pages
- evidence recall
- citation precision
- answer verdict
- answer judge rationale
- input tokens
- output tokens
- total tokens
- latency
- adapter configuration
- model configuration

For each method overall:

- average evidence recall
- average citation precision
- answer accuracy
- average and median total tokens
- average and median latency
- failure count
- failure examples

## Required Validation

Every new baseline must pass:

```powershell
python scripts\summarize_stage1_metrics.py
python scripts\generate_stage1_evidence_report.py
python scripts\validate_stage1_artifacts.py
```

The validation report must show:

```text
status=pass
failed_check_count=0
```

## Claim Discipline

Allowed after current MVP:

- "On the 12-question MVP subset..."
- "This run shows..."
- "This failure case suggests..."
- "The next larger subset should test..."

Not allowed yet:

- "PageIndex is generally better than RAG."
- "PageIndex is better for legal or medical books."
- "Hybrid RAG is worse than PageIndex."
- "Long-context is always too expensive."

These stronger claims require a larger dataset, stronger baselines, and cost assumptions.

## Next Implementation Order

1. Install and verify LlamaIndex dependencies in the benchmark environment.
2. Add `pipelines/llamaindex_vector_rag/adapter.py`.
3. Add `scripts/run_llamaindex_vector_rag_mvp.py`.
4. Run no-LLM smoke tests.
5. Run LLM answer generation on the same 12 questions.
6. Evaluate evidence and answers.
7. Regenerate detailed evidence reports and validation reports.
8. Only then update benchmark conclusions.
