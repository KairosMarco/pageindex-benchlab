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
- Average evidence recall: `1.000`
- Average citation precision: `0.347`

## Missing Structures

No missing structures.

## QA Failures

No QA failures.

## Evidence Issues

| Question | Document | Recall | Precision | Gold pages | Predicted pages |
|---|---|---:|---:|---|---|
| none | none | n/a | n/a | n/a | n/a |

## Interpretation

- PageIndex generated retrieval-only outputs for all `25 / 25` expanded questions with no QA failures.
- The full expanded retrieval-only run reached `1.000` average evidence recall and `0.347` average citation precision.
- No evidence recall misses remain in the current retrieval-only run.
- The paired ranking diagnostics explain the legacy-to-current scorer improvement without using gold evidence during scoring.
- The next PageIndex benchmark step is larger-set or non-finance validation plus answer-reasoning analysis for the remaining LLM answer issues.
- The retained `expanded_partial_summary` file name is historical; the current contents summarize the full retrieval-only run.

## Source Artifacts

- Readiness: `reports\pageindex\expanded_readiness.json`
- QA manifest: `reports\pageindex\qa_expanded_25_manifest.json`
- Evidence evaluation: `reports\pageindex\evidence_eval_qa_expanded_25.json`
- Ranking diagnostics: `reports\pageindex\pageindex_ranking_diagnostics.md`
