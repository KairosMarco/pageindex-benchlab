# PageIndex Expanded Indexing Notes

Date: 2026-06-18

## Summary

The expanded PageIndex indexing run improved structure coverage from `11 / 24` unique expanded documents to `19 / 24`.

Current coverage:

```text
Questions: 25
Unique source documents: 24
Documents with PageIndex structures and PDFs: 19
Runnable questions with current structures: 20
Missing PageIndex structures: 5
```

## Newly Generated Structures

```text
ADOBE_2016_10K
AMERICANEXPRESS_2022_10K
BLOCK_2016_10K
CORNING_2022_10K
FOOTLOCKER_2022_8K_dated-2022-05-20
MGMRESORTS_2022Q4_EARNINGS
PEPSICO_2023Q1_EARNINGS
ULTABEAUTY_2023Q4_EARNINGS
```

Indexing manifests:

```text
reports/pageindex/indexing_manifest_expanded_smoke.json
reports/pageindex/indexing_manifest_AMERICANEXPRESS_2022_10K.json
reports/pageindex/indexing_manifest_expanded_short_docs.json
reports/pageindex/indexing_manifest_expanded_mid_batch_1.json
```

## Remaining Missing Structures

```text
AMERICANWATERWORKS_2020_10K
COCACOLA_2021_10K
CVSHEALTH_2022_10K
GENERALMILLS_2020_10K
PFIZER_2021_10K
```

## Observed Indexing Blockers

- `PFIZER_2021_10K` failed during PageIndex indexing with a missing page-offset value. The observed PageIndex error was `TypeError: unsupported operand type(s) for +: 'int' and 'NoneType'`.
- `AMERICANWATERWORKS_2020_10K` was attempted as part of a batch with `CVSHEALTH_2022_10K` and `GENERALMILLS_2020_10K`, but the PageIndex process remained active for an unusually long time without producing a structure or manifest. The process was terminated to unblock the partial expanded QA run.
- `CVSHEALTH_2022_10K` and `GENERALMILLS_2020_10K` were not reached in that batch because `AMERICANWATERWORKS_2020_10K` was still running.
- `COCACOLA_2021_10K` was deferred because it is the largest remaining PDF in this subset.

## Partial Retrieval Result

After indexing the new structures, PageIndex retrieval-only QA was run with `--continue-on-error`.

```text
Generated QA outputs: 20 / 25
Failed QA outputs due to missing structures: 5
Average evidence recall on generated outputs: 0.850
Average citation precision on generated outputs: 0.283
```

Artifacts:

```text
reports/pageindex/qa_expanded_25_manifest.json
reports/pageindex/evidence_eval_qa_expanded_25.json
reports/pageindex/expanded_partial_summary.md
reports/pageindex/expanded_partial_summary.json
```

## Next Step

Before spending on expanded PageIndex LLM answer generation, index the five remaining structures and rerun:

```powershell
python scripts\summarize_pageindex_expanded_readiness.py
python scripts\run_pageindex_qa_mvp.py --questions datasets\financebench\expanded_questions_25.jsonl --structure-dir reports\pageindex\structures --output-dir reports\pageindex\qa_expanded_25 --manifest reports\pageindex\qa_expanded_25_manifest.json --no-llm --force --continue-on-error
python scripts\evaluate_evidence_mvp.py --questions datasets\financebench\expanded_questions_25.jsonl --results-dir reports\pageindex\qa_expanded_25 --output reports\pageindex\evidence_eval_qa_expanded_25.json --continue-on-error
python scripts\summarize_pageindex_expanded_partial.py
```
