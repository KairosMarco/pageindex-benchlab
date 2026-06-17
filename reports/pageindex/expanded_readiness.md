# PageIndex Expanded Readiness

Date: 2026-06-17

## Summary

- Question file: `datasets\financebench\expanded_questions_25.jsonl`
- Questions: `25`
- Unique source documents: `24`
- Documents with PageIndex structures and PDFs: `11`
- Missing PageIndex structures: `13`
- Missing PDFs: `0`
- Runnable questions with current structures: `12`
- Full expanded PageIndex QA ready: `False`

## Missing Structures

- `ADOBE_2016_10K`
- `AMERICANEXPRESS_2022_10K`
- `AMERICANWATERWORKS_2020_10K`
- `BLOCK_2016_10K`
- `COCACOLA_2021_10K`
- `CORNING_2022_10K`
- `CVSHEALTH_2022_10K`
- `FOOTLOCKER_2022_8K_dated-2022-05-20`
- `GENERALMILLS_2020_10K`
- `MGMRESORTS_2022Q4_EARNINGS`
- `PEPSICO_2023Q1_EARNINGS`
- `PFIZER_2021_10K`
- `ULTABEAUTY_2023Q4_EARNINGS`

## Document Coverage

| Document | Questions | PDF | Structure |
|---|---:|---|---|
| `3M_2018_10K` | 1 | yes | yes |
| `ADOBE_2016_10K` | 1 | yes | missing |
| `AMAZON_2017_10K` | 1 | yes | yes |
| `AMCOR_2023Q4_EARNINGS` | 1 | yes | yes |
| `AMD_2022_10K` | 2 | yes | yes |
| `AMERICANEXPRESS_2022_10K` | 1 | yes | missing |
| `AMERICANWATERWORKS_2020_10K` | 1 | yes | missing |
| `BESTBUY_2023_10K` | 1 | yes | yes |
| `BLOCK_2016_10K` | 1 | yes | missing |
| `BOEING_2022_10K` | 1 | yes | yes |
| `COCACOLA_2021_10K` | 1 | yes | missing |
| `CORNING_2022_10K` | 1 | yes | missing |
| `COSTCO_2021_10K` | 1 | yes | yes |
| `CVSHEALTH_2022_10K` | 1 | yes | missing |
| `FOOTLOCKER_2022_8K_dated-2022-05-20` | 1 | yes | missing |
| `GENERALMILLS_2020_10K` | 1 | yes | missing |
| `JOHNSON_JOHNSON_2023_8K_dated-2023-08-30` | 1 | yes | yes |
| `JPMORGAN_2023Q2_10Q` | 1 | yes | yes |
| `MGMRESORTS_2022Q4_EARNINGS` | 1 | yes | missing |
| `MICROSOFT_2016_10K` | 1 | yes | yes |
| `NIKE_2023_10K` | 1 | yes | yes |
| `PEPSICO_2023Q1_EARNINGS` | 1 | yes | missing |
| `PFIZER_2021_10K` | 1 | yes | missing |
| `ULTABEAUTY_2023Q4_EARNINGS` | 1 | yes | missing |

## Commands

Index missing structures:

```powershell
$env:DEEPSEEK_API_KEY="YOUR_KEY"
python scripts\run_pageindex_mvp.py --questions datasets\financebench\expanded_questions_25.jsonl --pdf-dir datasets\raw\financebench\pdfs --output-dir reports\pageindex\structures --model deepseek/deepseek-v4-pro --continue-on-error --doc-name ADOBE_2016_10K --doc-name AMERICANEXPRESS_2022_10K --doc-name AMERICANWATERWORKS_2020_10K --doc-name BLOCK_2016_10K --doc-name COCACOLA_2021_10K --doc-name CORNING_2022_10K --doc-name CVSHEALTH_2022_10K --doc-name FOOTLOCKER_2022_8K_dated-2022-05-20 --doc-name GENERALMILLS_2020_10K --doc-name MGMRESORTS_2022Q4_EARNINGS --doc-name PEPSICO_2023Q1_EARNINGS --doc-name PFIZER_2021_10K --doc-name ULTABEAUTY_2023Q4_EARNINGS
```

Run PageIndex expanded retrieval-only QA after all structures exist:

```powershell
python scripts\run_pageindex_qa_mvp.py --questions datasets\financebench\expanded_questions_25.jsonl --structure-dir reports\pageindex\structures --output-dir reports\pageindex\qa_expanded_25 --manifest reports\pageindex\qa_expanded_25_manifest.json --no-llm --force --continue-on-error
python scripts\evaluate_evidence_mvp.py --questions datasets\financebench\expanded_questions_25.jsonl --results-dir reports\pageindex\qa_expanded_25 --output reports\pageindex\evidence_eval_qa_expanded_25.json --continue-on-error
```

## Interpretation

- PageIndex expanded 25-question QA is not ready for a full run until the missing structures are indexed.
- The current 11 covered documents come from the 12-question MVP run. They are useful for smoke tests but do not cover the full expanded set.
- The next PageIndex benchmark step is indexing the 13 missing expanded documents, then running retrieval-only QA and evidence evaluation before LLM answer generation.
