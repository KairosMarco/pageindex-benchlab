# PageIndex Expanded Indexing Notes

Date: 2026-06-18

## Summary

The expanded PageIndex indexing run now covers the full 25-question FinanceBench expanded subset.

Final coverage:

```text
Questions: 25
Unique source documents: 24
Documents with PageIndex structures and PDFs: 24
Runnable questions with current structures: 25
Missing PageIndex structures: 0
```

## Generated Structures

The expanded run added these structures beyond the original MVP structures:

```text
ADOBE_2016_10K
AMERICANEXPRESS_2022_10K
AMERICANWATERWORKS_2020_10K
BLOCK_2016_10K
COCACOLA_2021_10K
CORNING_2022_10K
CVSHEALTH_2022_10K
FOOTLOCKER_2022_8K_dated-2022-05-20
GENERALMILLS_2020_10K
MGMRESORTS_2022Q4_EARNINGS
PEPSICO_2023Q1_EARNINGS
PFIZER_2021_10K
ULTABEAUTY_2023Q4_EARNINGS
```

Key manifests:

```text
reports/pageindex/indexing_manifest_expanded_smoke.json
reports/pageindex/indexing_manifest_AMERICANEXPRESS_2022_10K.json
reports/pageindex/indexing_manifest_expanded_short_docs.json
reports/pageindex/indexing_manifest_expanded_mid_batch_1.json
reports/pageindex/indexing_manifest_PFIZER_2021_10K_retry.json
reports/pageindex/indexing_manifest_CVSHEALTH_2022_10K_retry.json
reports/pageindex/indexing_manifest_GENERALMILLS_2020_10K.json
reports/pageindex/indexing_manifest_AMERICANWATERWORKS_2020_10K.json
reports/pageindex/indexing_manifest_COCACOLA_2021_10K_retry.json
```

The failed `CVSHEALTH_2022_10K` and `COCACOLA_2021_10K` first-attempt manifests are retained as robustness evidence. Both documents succeeded after local PageIndex defensive patches.

## Local PageIndex Robustness Fixes Used

These fixes were applied in the local PageIndex checkout before the final successful structures were generated:

- Normalize model-produced TOC JSON to a list before list operations such as `.extend()`.
- Skip page-offset addition when detected offset is missing.
- Return low-confidence no-TOC structures instead of raising when verification remains below threshold.
- Leave unresolved TOC items unresolved when `add_page_number_to_toc()` returns an empty list or omits `physical_index`, rather than failing the whole document.

These are PageIndex upstream contribution candidates. They are not algorithmic ranking changes; they only prevent crashes or hard failures caused by incomplete LLM JSON.

## Retrieval-only Expanded Result

After all structures were available, PageIndex retrieval-only QA was run on the full 25-question set.

```text
Generated QA outputs: 25 / 25
Failed QA outputs: 0
Average evidence recall: 0.760
Average citation precision: 0.253
```

Evidence misses:

```text
fb_exp_014
fb_exp_017
fb_exp_020
fb_exp_022
fb_exp_023
fb_exp_025
```

Artifacts:

```text
reports/pageindex/qa_expanded_25_manifest.json
reports/pageindex/evidence_eval_qa_expanded_25.json
reports/pageindex/expanded_partial_summary.md
reports/pageindex/expanded_partial_summary.json
```

The `expanded_partial_summary` filename is historical. The current file contents summarize the complete retrieval-only run.

## Expanded LLM Result

PageIndex LLM answer generation has also been run on the same 25-question expanded set.

```text
Model: deepseek/deepseek-v4-pro
Generated answers: 25 / 25
Generation failures: 0
Evaluation failures: 0
Evidence recall: 0.760
Citation precision: 0.253
Answer accuracy: 0.760
Verdicts: 19 correct, 1 partial, 5 incorrect
Average total tokens: 3,046
Average latency: 5,787 ms
Validation: pass, 20 checks, 0 failed
```

Artifacts:

```text
reports/pageindex_expanded_llm_diagnostics.md
reports/pageindex_expanded_llm_diagnostics.json
reports/expanded_pageindex_llm_validation_report.json
reports/pageindex/qa_llm_expanded_25/
reports/pageindex/qa_llm_expanded_25_manifest.json
reports/pageindex/evidence_eval_qa_llm_expanded_25.json
reports/pageindex/answer_eval_qa_llm_expanded_25.json
```

## Interpretation

- The expanded run is now complete mechanically: all structures, retrieval outputs, LLM answers, evidence eval, and answer eval exist.
- PageIndex remains strong on the original 12-question MVP set, but the 25-question expanded set exposes ranking gaps.
- The next PageIndex contribution should focus on retrieval/ranking diagnostics for the six evidence misses, plus upstreaming the JSON resilience fixes used to complete indexing.
