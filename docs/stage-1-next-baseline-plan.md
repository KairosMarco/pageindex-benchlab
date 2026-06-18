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
10. Run expanded LLM answer generation only after retrieval quality is acceptable. Completed for LlamaIndex Vector and Hybrid `concept_v2`, `rerank_top_k=3`.
11. Run expanded Long-context LLM baseline on the same 25-question set. Completed.
12. Add expanded cost estimates and decide whether to test stricter finance reasoning prompts. Completed.
13. Decide whether to preserve the current reasoning failures as benchmark findings or run a stricter answer-prompt variant. Completed as a prompt-ablation diagnostic.

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

The finance-aware LlamaIndex Vector candidate passes the mechanical promotion gate on the 12-question MVP subset. The first expanded 25-question retrieval run exposed failures on concept-heavy finance questions. The `concept_v2` label-free reranker signals restored 1.000 evidence recall on the 25-question retrieval-only run. The expanded LLM run with `concept_v2`, `rerank_top_k=3` preserved 1.000 evidence recall and reached 0.920 LLM-judge answer accuracy.

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

The finance-aware LlamaIndex Hybrid candidate passes the mechanical promotion gate on the 12-question MVP subset. The first expanded 25-question retrieval run exposed failures on concept-heavy finance questions. The `concept_v2` label-free reranker signals restored 1.000 evidence recall on the 25-question retrieval-only run. The expanded LLM run with `concept_v2`, `rerank_top_k=3` preserved 1.000 evidence recall and reached 0.880 LLM-judge answer accuracy.

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

## Expanded LLM Result

The 25-question expanded answer-generation run used the validated `concept_v2`, `rerank_top_k=3` configuration:

```powershell
python scripts\run_llamaindex_expanded_llm_diagnostics.py --force --continue-on-error
python scripts\validate_expanded_llm_artifacts.py
```

Results:

```text
Vector concept_v2 r3:
questions: 25
evidence recall: 1.000
citation precision: 0.360
answer accuracy: 0.920
verdicts: 23 correct, 1 partial, 1 incorrect
average total tokens: 2,543
average context words: 1,138

Hybrid concept_v2 r3:
questions: 25
evidence recall: 1.000
citation precision: 0.360
answer accuracy: 0.880
verdicts: 22 correct, 2 partial, 1 incorrect
average total tokens: 2,553
average context words: 1,160
```

Validation:

```text
reports/expanded_llm_validation_report.json
status=pass
checks=37
failed=0
```

Observed issue cases:

```text
fb_exp_017: working-capital definition mismatch after retrieving the right page.
fb_exp_019: Hybrid answer used $0.389 billion; judge marked it partial against rounded gold $0.40.
fb_exp_020: capital-intensity interpretation failure after retrieving the right pages.
```

Interpretation:

The expanded LLM run shows that the current LlamaIndex candidates are no longer failing primarily at retrieval on this 25-question subset. The remaining gap is answer reasoning and judging strictness on concept-heavy financial questions.

## Finance Prompt Variant Result

Prompt-variant diagnostics were run for LlamaIndex Vector RAG only. The default prompt remains the cross-method comparison baseline; the finance prompts are answer-generation ablations.

Run commands:

```powershell
python scripts\run_llamaindex_expanded_llm_diagnostics.py --method vector --summary-selected-only --answer-prompt-mode finance_reasoning_v2 --force --continue-on-error
python scripts\run_llamaindex_expanded_llm_diagnostics.py --method vector --summary-selected-only --answer-prompt-mode finance_reasoning_v3 --force --continue-on-error
python scripts\summarize_finance_prompt_variants.py
```

Results:

```text
Default prompt:
answer accuracy: 0.920
verdicts: 23 correct, 1 partial, 1 incorrect
average total tokens: 2,543

finance_reasoning_v2:
answer accuracy: 0.960
verdicts: 24 correct, 0 partial, 1 incorrect
average total tokens: 2,885

finance_reasoning_v3:
answer accuracy: 0.920
verdicts: 23 correct, 2 partial, 0 incorrect
average total tokens: 2,978
```

Validation:

```text
reports/expanded_llm_validation_report_finance_reasoning_v2.json
status=pass
checks=21
failed=0

reports/expanded_llm_validation_report_finance_reasoning_v3.json
status=pass
checks=21
failed=0
```

Interpretation:

`finance_reasoning_v2` improved correct-only accuracy by fixing `fb_exp_020`, but it introduced a rounding-format failure on `fb_exp_019`. `finance_reasoning_v3` fixed the targeted rounding and capital-intensity probes, but the full run still had two partial answers. This confirms that prompt tuning should be treated as an ablation with tradeoffs, not a universally stronger replacement for the default prompt.

## Expanded Long-context Result

The 25-question Long-context answer-generation run used the same answer model and judge:

```powershell
python scripts\run_long_context_expanded_llm_diagnostics.py --force --continue-on-error
python scripts\validate_expanded_long_context_artifacts.py
```

Results:

```text
Long-context LLM:
questions: 25
evidence recall: 0.800
citation precision: 0.267
answer accuracy: 0.920
verdicts: 23 correct, 1 partial, 1 incorrect
average total tokens: 92,500
average context chars: 397,913
average context pages: 113
average latency: 12,772 ms
```

Validation:

```text
reports/expanded_long_context_validation_report.json
status=pass
checks=21
failed=0
```

Observed issue cases:

```text
Evidence citation misses: fb_exp_014, fb_exp_017, fb_exp_020, fb_exp_023, fb_mvp_005.
Answer issues: fb_exp_020 incorrect, fb_mvp_003 partial.
```

Interpretation:

Long-context matched LlamaIndex Vector's `0.920` answer accuracy on this 25-question subset, but with about `36x` higher average token use and lower citation evidence recall (`0.800` vs `1.000`). The result is useful because it shows that larger context alone does not guarantee better citation grounding. The shared hard case is `fb_exp_020`, where both Long-context and LlamaIndex candidates retrieved or had access to relevant evidence but misinterpreted capital intensity.

## Expanded Cost And Quality Summary

The cross-method expanded summary is:

```text
reports/expanded_cost_quality_summary.md
reports/expanded_cost_quality_summary.json
```

Key rows:

```text
LlamaIndex Vector: answer accuracy 0.920, evidence recall 1.000, avg tokens 2,543, token x 1.000
LlamaIndex Hybrid: answer accuracy 0.880, evidence recall 1.000, avg tokens 2,553, token x 1.004
PageIndex: answer accuracy 0.760, evidence recall 0.760, avg tokens 3,046, token x 1.198
Long-context: answer accuracy 0.920, evidence recall 0.800, avg tokens 92,500, token x 36.371
```

Current decision point:

```text
Option A: preserve current failures as benchmark evidence.
Option B: run a stricter finance-reasoning answer prompt variant and compare whether fb_exp_020 improves without hurting simpler extraction questions.
```
