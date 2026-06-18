# PageIndex Expanded Readiness

Date: 2026-06-18

## Summary

- Question file: `datasets\financebench\expanded_questions_25.jsonl`
- Questions: `25`
- Unique source documents: `24`
- Documents with PageIndex structures and PDFs: `24`
- Missing PageIndex structures: `0`
- Missing PDFs: `0`
- Runnable questions with current structures: `25`
- Full expanded PageIndex QA ready: `True`

## Missing Structures

No missing structures.

## Document Coverage

| Document | Questions | PDF | Structure |
|---|---:|---|---|
| `3M_2018_10K` | 1 | yes | yes |
| `ADOBE_2016_10K` | 1 | yes | yes |
| `AMAZON_2017_10K` | 1 | yes | yes |
| `AMCOR_2023Q4_EARNINGS` | 1 | yes | yes |
| `AMD_2022_10K` | 2 | yes | yes |
| `AMERICANEXPRESS_2022_10K` | 1 | yes | yes |
| `AMERICANWATERWORKS_2020_10K` | 1 | yes | yes |
| `BESTBUY_2023_10K` | 1 | yes | yes |
| `BLOCK_2016_10K` | 1 | yes | yes |
| `BOEING_2022_10K` | 1 | yes | yes |
| `COCACOLA_2021_10K` | 1 | yes | yes |
| `CORNING_2022_10K` | 1 | yes | yes |
| `COSTCO_2021_10K` | 1 | yes | yes |
| `CVSHEALTH_2022_10K` | 1 | yes | yes |
| `FOOTLOCKER_2022_8K_dated-2022-05-20` | 1 | yes | yes |
| `GENERALMILLS_2020_10K` | 1 | yes | yes |
| `JOHNSON_JOHNSON_2023_8K_dated-2023-08-30` | 1 | yes | yes |
| `JPMORGAN_2023Q2_10Q` | 1 | yes | yes |
| `MGMRESORTS_2022Q4_EARNINGS` | 1 | yes | yes |
| `MICROSOFT_2016_10K` | 1 | yes | yes |
| `NIKE_2023_10K` | 1 | yes | yes |
| `PEPSICO_2023Q1_EARNINGS` | 1 | yes | yes |
| `PFIZER_2021_10K` | 1 | yes | yes |
| `ULTABEAUTY_2023Q4_EARNINGS` | 1 | yes | yes |

## Commands

Run PageIndex expanded retrieval-only QA after all structures exist:

```powershell
python scripts\run_pageindex_qa_mvp.py --questions datasets\financebench\expanded_questions_25.jsonl --structure-dir reports\pageindex\structures --output-dir reports\pageindex\qa_expanded_25 --manifest reports\pageindex\qa_expanded_25_manifest.json --no-llm --force --continue-on-error
python scripts\evaluate_evidence_mvp.py --questions datasets\financebench\expanded_questions_25.jsonl --results-dir reports\pageindex\qa_expanded_25 --output reports\pageindex\evidence_eval_qa_expanded_25.json --continue-on-error
```

## Interpretation

- PageIndex expanded 25-question retrieval-only QA is ready to run.
- The current `24` covered documents support all `25` expanded questions.
- The next PageIndex benchmark step is running expanded LLM answer generation and answer evaluation.
