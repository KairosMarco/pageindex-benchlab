# PageIndex Expanded Partial Summary

Date: 2026-06-18

## Scope

This report summarizes the current partial PageIndex expanded retrieval-only run. It does not include LLM answer generation.

## Coverage

- Questions: `25`
- Unique source documents: `24`
- Documents with PageIndex structures and PDFs: `19`
- Missing PageIndex structures: `5`
- Missing PDFs: `0`
- Runnable questions with current structures: `20`
- Retrieval-only QA generated: `20`
- Retrieval-only QA failed: `5`
- Full expanded PageIndex QA ready: `False`

## Retrieval Metrics

- Evaluated PageIndex results: `20`
- Average evidence recall: `0.850`
- Average citation precision: `0.283`

## Missing Structures

- `AMERICANWATERWORKS_2020_10K`
- `COCACOLA_2021_10K`
- `CVSHEALTH_2022_10K`
- `GENERALMILLS_2020_10K`
- `PFIZER_2021_10K`

## QA Failures

- `fb_exp_019` / `AMERICANWATERWORKS_2020_10K`: Missing PageIndex structure: reports\pageindex\structures\AMERICANWATERWORKS_2020_10K_structure.json
- `fb_exp_020` / `CVSHEALTH_2022_10K`: Missing PageIndex structure: reports\pageindex\structures\CVSHEALTH_2022_10K_structure.json
- `fb_exp_022` / `COCACOLA_2021_10K`: Missing PageIndex structure: reports\pageindex\structures\COCACOLA_2021_10K_structure.json
- `fb_exp_023` / `PFIZER_2021_10K`: Missing PageIndex structure: reports\pageindex\structures\PFIZER_2021_10K_structure.json
- `fb_exp_024` / `GENERALMILLS_2020_10K`: Missing PageIndex structure: reports\pageindex\structures\GENERALMILLS_2020_10K_structure.json

## Evidence Issues

| Question | Document | Recall | Precision | Gold pages | Predicted pages |
|---|---|---:|---:|---|---|
| `fb_exp_014` | `AMERICANEXPRESS_2022_10K` | 0.000 | 0.000 | 96 | 104, 121, 134 |
| `fb_exp_017` | `CORNING_2022_10K` | 0.000 | 0.000 | 60 | 34, 16, 66 |
| `fb_exp_025` | `ULTABEAUTY_2023Q4_EARNINGS` | 0.000 | 0.000 | 2 | 3, 6, 9 |

## Interpretation

- The current PageIndex expanded run is a partial retrieval-only result, not a complete 25-question comparison.
- PageIndex generated retrieval outputs for `20 / 25` questions and reached `0.850` average evidence recall on those generated outputs.
- The five missing questions are blocked by missing structures, not by QA adapter failures.
- Additional PageIndex indexing robustness is needed before running full expanded PageIndex LLM answer generation.

## Source Artifacts

- Readiness: `reports\pageindex\expanded_readiness.json`
- QA manifest: `reports\pageindex\qa_expanded_25_manifest.json`
- Evidence evaluation: `reports\pageindex\evidence_eval_qa_expanded_25.json`
