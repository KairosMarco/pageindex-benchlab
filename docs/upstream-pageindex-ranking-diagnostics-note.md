# Upstream PageIndex Ranking Diagnostics Note

Target repository:

```text
https://github.com/VectifyAI/PageIndex
```

Suggested issue or discussion title:

```text
Benchmark note: PageIndex page-ranking diagnostics on FinanceBench evidence QA
```

## Summary

I ran PageIndex on a 25-question FinanceBench subset and compared two local benchmark adapter page scorers over PageIndex-produced structures:

- a legacy scorer using question terms, PageIndex section-title terms, and a small set of phrase boosts
- a current scorer that adds label-free finance line-item signals from the question text and candidate page text

The current scorer does not inspect FinanceBench gold evidence during retrieval.

## Result

```text
Dataset: FinanceBench expanded 25-question subset
Documents: 24 unique source PDFs
Answer model: deepseek/deepseek-v4-pro
Citation budget: 3 pages
```

| Benchmark adapter scorer | Questions | Full hit count | Zero hit count | Evidence recall | Citation precision |
|---|---:|---:|---:|---:|---:|
| Legacy PageIndex scorer | 25 | 19 | 6 | 0.760 | 0.253 |
| Current scorer + finance line-item boost | 25 | 25 | 0 | 1.000 | 0.347 |

The current benchmark adapter scorer improved six cases and introduced no observed regressions on this subset.

## Fixed Cases

| Question | Document | Gold pages | Current top pages | Main diagnostic signal |
|---|---|---|---|---|
| `fb_exp_014` | `AMERICANEXPRESS_2022_10K` | 96 | 47, 96, 136 | income statement and financial-services income lines |
| `fb_exp_017` | `CORNING_2022_10K` | 60 | 60, 20, 93 | balance sheet and working-capital line items |
| `fb_exp_020` | `CVSHEALTH_2022_10K` | 108, 110 | 110, 133, 108 | income statement plus balance sheet asset-base lines |
| `fb_exp_022` | `COCACOLA_2021_10K` | 62 | 68, 62, 101 | income statement line items |
| `fb_exp_023` | `PFIZER_2021_10K` | 59 | 59, 72, 61 | balance sheet and PP&E line items |
| `fb_exp_025` | `ULTABEAUTY_2023Q4_EARNINGS` | 2 | 2, 1, 6 | SG&A driver narrative terms |

## Why This Is Useful Upstream

The ranking diagnostics separate three concerns that are easy to mix together:

- PageIndex structure generation: all 24 expanded source documents have structures and PDFs.
- Page selection: the current scorer retrieves all gold evidence pages in the top three selected pages.
- Answer reasoning: the remaining PageIndex answer issues are not retrieval misses.

Current PageIndex expanded LLM result:

```text
Questions: 25
Evidence recall: 1.000
Citation precision: 0.347
Answer accuracy: 0.920
Verdicts: 23 correct, 0 partial, 2 incorrect
Average total tokens: 2,882
Average latency: 4,840 ms
```

Remaining answer issues:

- `fb_exp_019`: rounding or judge strictness. PageIndex retrieved page 86 and extracted `$389 million`, while the gold answer is rounded to `$0.40` billion.
- `fb_exp_020`: finance concept definition. PageIndex retrieved pages 108 and 110, but the answer used a narrow fixed-asset ratio interpretation while the gold answer uses low ROA and broad asset-base reasoning.

## Suggested Upstream Contribution Shape

This should be split into small reviewable contributions:

1. Documentation note: add a PageIndex benchmark reproduction note for evidence-page QA.
2. Diagnostic script or example: show how to compare legacy/current page scoring without LLM answer calls.
3. Robustness PR: add defensive JSON and page-offset handling for noisy model outputs during structure generation.
4. Follow-up answer prompt note: document finance-reasoning failure modes separately from retrieval failures.

## Local Artifacts

```text
reports/pageindex/pageindex_ranking_diagnostics.md
reports/pageindex/pageindex_ranking_diagnostics.json
reports/pageindex/expanded_partial_summary.md
reports/pageindex/pageindex_answer_issue_analysis.md
reports/pageindex_expanded_llm_diagnostics.md
reports/expanded_cost_quality_summary.md
```

## Conservative Claim

This result does not prove broad PageIndex superiority. It supports a narrower claim:

```text
On this 25-question FinanceBench subset, PageIndex can match the strongest tested retrieval baselines on page-level evidence recall while using a compact three-page answer context, after adding label-free finance line-item ranking diagnostics.
```
