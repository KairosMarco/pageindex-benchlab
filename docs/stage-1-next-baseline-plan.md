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

1. Install and verify LlamaIndex dependencies in the benchmark environment. Completed.
2. Add `pipelines/llamaindex_vector_rag/adapter.py`. Completed.
3. Add `scripts/run_llamaindex_vector_rag_mvp.py`. Completed.
4. Run no-LLM smoke tests. Completed as diagnostic runs.
5. Improve reranking or add Hybrid fusion before LLM answer generation. Completed for retrieval-only diagnostics with label-free finance-aware reranking.
6. Run LLM answer generation on the same 12 questions only after retrieval quality is acceptable. Completed for finance-aware LlamaIndex Vector and Hybrid diagnostics.
7. Evaluate evidence and answers. Completed for finance-aware LlamaIndex Vector and Hybrid diagnostics.
8. Regenerate detailed evidence reports and validation reports. Completed in `reports/llamaindex_finance_llm_diagnostics.md` and `.json`.
9. Expand retrieval validation to 25 FinanceBench questions. Completed for retrieval-only mode.
10. Run expanded LLM answer generation only after retrieval quality is acceptable.

## LlamaIndex Vector Diagnostic Result

Current no-LLM retrieval diagnostics:

```text
Generic reranker:
max_citations=3:  evidence recall 0.667, citation precision 0.222
max_citations=6:  evidence recall 0.833, citation precision 0.139
max_citations=12: evidence recall 0.917, citation precision 0.083

Finance-aware reranker:
questions: 12
failures: 0
max_citations=3: evidence recall 1.000, citation precision 0.333
```

Interpretation:

The generic LlamaIndex vector retriever with `sentence-transformers/all-MiniLM-L6-v2` often places gold pages in the wider candidate set, but it does not reliably rank them into the top citations. The label-free finance-aware reranker fixes top-three evidence retrieval on the 12-question MVP subset by using only the question text and candidate chunk text.

LLM diagnostic result:

```text
questions: 12
failures: 0
evidence recall: 1.000
citation precision: 0.333
LLM-judge answer accuracy: 1.000
average total tokens: 8,964
average latency: 16,723 ms
```

Low-context validation:

```text
rerank_top_k: 3
questions: 12
failures: 0
evidence recall: 1.000
citation precision: 0.333
LLM-judge answer accuracy: 1.000
average total tokens: 2,424
token reduction vs rerank_top_k=12: 73.0%
```

Interpretation:

The finance-aware LlamaIndex Vector candidate passes the mechanical promotion gate on the 12-question MVP subset. The first expanded 25-question retrieval run exposed failures on concept-heavy finance questions. The `concept_v2` label-free reranker signals restored 1.000 evidence recall on the 25-question retrieval-only run, so the next answer-generation candidate is `concept_v2` with `rerank_top_k=3`.

## LlamaIndex Hybrid Diagnostic Result

Current single-question diagnostic on `fb_mvp_001`:

```text
Generic reranker:
top-3 citations: evidence recall 0.000
top-6 citations: evidence recall 1.000, citation precision 0.167
top-12 citations: evidence recall 1.000, citation precision 0.091
cross-encoder rerank top-3: evidence recall 0.000

Finance-aware reranker:
questions: 12
failures: 0
max_citations=3: evidence recall 1.000, citation precision 0.333
```

Interpretation:

BM25/vector fusion finds the relevant evidence in a wider candidate set, but the generic reranker still fails to promote the financial statement page into the top three citations. The tested generic cross-encoder did not improve the first diagnostic case. The label-free finance-aware reranker fixes top-three evidence retrieval on the 12-question MVP subset.

LLM diagnostic result:

```text
questions: 12
failures: 0
evidence recall: 1.000
citation precision: 0.333
LLM-judge answer accuracy: 1.000
average total tokens: 9,216
average latency: 18,596 ms
```

Low-context validation:

```text
rerank_top_k: 3
questions: 12
failures: 0
evidence recall: 1.000
citation precision: 0.347
LLM-judge answer accuracy: 1.000
average total tokens: 2,520
token reduction vs rerank_top_k=12: 72.7%
```

Interpretation:

The finance-aware LlamaIndex Hybrid candidate passes the mechanical promotion gate on the 12-question MVP subset. The first expanded 25-question retrieval run exposed failures on concept-heavy finance questions. The `concept_v2` label-free reranker signals restored 1.000 evidence recall on the 25-question retrieval-only run, so the next answer-generation candidate is `concept_v2` with `rerank_top_k=3`.

## Expanded Retrieval Result

Default 25-question retrieval-only run:

```text
Vector r3/r6/r12: evidence recall 0.880
Hybrid r3/r6/r12: evidence recall 0.840
```

The failed questions are listed in `reports/llamaindex_expanded_retrieval.md`.

`concept_v2` 25-question retrieval-only run:

```text
Vector r3: evidence recall 1.000, citation precision 0.360, average context words 1,138
Hybrid r3: evidence recall 1.000, citation precision 0.360, average context words 1,160
```

Validation:

```powershell
python scripts\validate_expanded_retrieval_artifacts.py
```

Current validation status:

```text
status=pass
checks=22
failed=0
```
