# PageIndex QA MVP Report

Date: 2026-06-16

## Scope

This report covers the first PageIndex retrieval-only benchmark run for the FinanceBench MVP subset.

- Dataset: `datasets/financebench/mvp_questions.jsonl`
- Questions: 12
- Unique PDFs: 11
- Method: `pageindex_tree_qa`
- Adapter mode: `tree_page_scoring`
- LLM answering: disabled (`--no-llm`)
- Citation pages per question: 3

This run evaluates retrieval evidence only. It does not yet evaluate final natural-language answer accuracy.

## Commands

```powershell
D:\pageindex-demo\PageIndex\.venv\Scripts\python.exe scripts\run_pageindex_qa_mvp.py --no-llm --force --continue-on-error
D:\pageindex-demo\PageIndex\.venv\Scripts\python.exe scripts\evaluate_evidence_mvp.py --continue-on-error
```

## Summary

| Metric | Value |
|---|---:|
| Result count | 12 |
| Failure count | 0 |
| Average evidence recall | 1.000 |
| Average citation precision | 0.333 |

Interpretation:

- PageIndex structures plus page-level scoring found the gold evidence page for every MVP question.
- Precision is `1/3` because the adapter returns 3 citation pages per question and each MVP question currently has one gold evidence page.
- The current result is strong enough to proceed to baseline comparisons.

## Per-Question Evidence Results

| Question | Document | Gold page | Predicted pages | Recall | Precision |
|---|---|---:|---|---:|---:|
| `fb_mvp_001` | `3M_2018_10K` | 60 | 49, 60, 83 | 1.000 | 0.333 |
| `fb_mvp_002` | `AMAZON_2017_10K` | 38 | 49, 38, 48 | 1.000 | 0.333 |
| `fb_mvp_003` | `AMD_2022_10K` | 4 | 60, 4, 7 | 1.000 | 0.333 |
| `fb_mvp_004` | `AMD_2022_10K` | 58 | 59, 58, 51 | 1.000 | 0.333 |
| `fb_mvp_005` | `BESTBUY_2023_10K` | 40 | 40, 25, 28 | 1.000 | 0.333 |
| `fb_mvp_006` | `BOEING_2022_10K` | 113 | 113, 19, 20 | 1.000 | 0.333 |
| `fb_mvp_007` | `COSTCO_2021_10K` | 38 | 38, 51, 45 | 1.000 | 0.333 |
| `fb_mvp_008` | `MICROSOFT_2016_10K` | 52 | 52, 31, 58 | 1.000 | 0.333 |
| `fb_mvp_009` | `NIKE_2023_10K` | 62 | 62, 69, 93 | 1.000 | 0.333 |
| `fb_mvp_010` | `AMCOR_2023Q4_EARNINGS` | 12 | 11, 7, 12 | 1.000 | 0.333 |
| `fb_mvp_011` | `JPMORGAN_2023Q2_10Q` | 85 | 85, 54, 87 | 1.000 | 0.333 |
| `fb_mvp_012` | `JOHNSON_JOHNSON_2023_8K_dated-2023-08-30` | 4 | 4, 6, 8 | 1.000 | 0.333 |

## Current Limitations

- The run is retrieval-only. LLM answer generation is not included in these metrics.
- The scoring layer is lexical and finance-term based. It is intentionally simple so the first MVP is easy to audit.
- Evidence precision is page-level, not span-level.
- The MVP subset is small and should not be presented as a full benchmark.

## Next Work

1. Run LLM answer generation on the same PageIndex citations.
2. Add the Long-context baseline on the same 12 questions.
3. Add Vector RAG + reranker and Hybrid RAG baselines.
4. Produce a cross-method report with answer accuracy, evidence recall, citation precision, latency, and token usage.
