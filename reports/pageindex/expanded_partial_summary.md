# PageIndex Expanded Retrieval Summary

Date: 2026-06-18

## Scope

This report summarizes the complete 25-question PageIndex expanded retrieval-only run. It does not include LLM answer generation.

## Coverage

- Questions: `25`
- Unique source documents: `24`
- Documents with PageIndex structures and PDFs: `24`
- Missing PageIndex structures: `0`
- Missing PDFs: `0`
- Runnable questions with current structures: `25`
- Retrieval-only QA generated: `25`
- Retrieval-only QA failed: `0`
- Full expanded PageIndex QA ready: `True`

## Retrieval Metrics

- Evaluated PageIndex results: `25`
- Average evidence recall: `0.760`
- Average citation precision: `0.253`

## Missing Structures

No missing structures.

## QA Failures

No QA failures.

## Evidence Issues

| Question | Document | Recall | Precision | Gold pages | Predicted pages |
|---|---|---:|---:|---|---|
| `fb_exp_014` | `AMERICANEXPRESS_2022_10K` | 0.000 | 0.000 | 96 | 104, 121, 134 |
| `fb_exp_017` | `CORNING_2022_10K` | 0.000 | 0.000 | 60 | 34, 16, 66 |
| `fb_exp_020` | `CVSHEALTH_2022_10K` | 0.000 | 0.000 | 108, 110 | 30, 32, 63 |
| `fb_exp_022` | `COCACOLA_2021_10K` | 0.000 | 0.000 | 62 | 68, 77, 85 |
| `fb_exp_023` | `PFIZER_2021_10K` | 0.000 | 0.000 | 59 | 63, 76, 10 |
| `fb_exp_025` | `ULTABEAUTY_2023Q4_EARNINGS` | 0.000 | 0.000 | 2 | 3, 6, 9 |

## Interpretation

- PageIndex generated retrieval-only outputs for all `25 / 25` expanded questions with no QA failures.
- The full expanded retrieval-only run reached `0.760` average evidence recall and `0.253` average citation precision.
- The six evidence misses show that complete structure coverage alone is not enough; PageIndex ranking needs further work before strong expanded-set claims.
- The next PageIndex benchmark step is expanded LLM answer generation, followed by evidence and answer evaluation against the same 25-question set.
- The retained `expanded_partial_summary` file name is historical; the current contents summarize the full retrieval-only run.

## Source Artifacts

- Readiness: `reports\pageindex\expanded_readiness.json`
- QA manifest: `reports\pageindex\qa_expanded_25_manifest.json`
- Evidence evaluation: `reports\pageindex\evidence_eval_qa_expanded_25.json`
