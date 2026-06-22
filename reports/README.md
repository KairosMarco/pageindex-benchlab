# Reports

This directory stores generated benchmark reports and raw result artifacts.

## Read These First

| Report | Purpose |
|---|---|
| `expanded_cost_quality_summary.md` | Cross-method 25-question summary |
| `pageindex_expanded_llm_diagnostics.md` | PageIndex expanded answer-generation diagnostics |
| `pageindex/pageindex_ranking_diagnostics.md` | PageIndex page-ranking before/after diagnostics |
| `pageindex/pageindex_answer_issue_analysis.md` | Remaining PageIndex answer issue analysis |
| `finance_prompt_variant_summary.md` | Prompt-ablation summary |

## Validation Artifacts

| File | Purpose |
|---|---|
| `stage1_validation_report.json` | MVP artifact validation |
| `expanded_retrieval_validation_report.json` | Expanded retrieval validation |
| `expanded_llm_validation_report.json` | Expanded LlamaIndex LLM validation |
| `expanded_pageindex_llm_validation_report.json` | Expanded PageIndex LLM validation |
| `expanded_long_context_validation_report.json` | Expanded long-context validation |

## Raw Outputs

Subdirectories such as `pageindex/qa_llm_expanded_25/`, `long_context/qa_llm_expanded_25/`, and `llamaindex_*` contain generated per-question artifacts.

Do not commit private documents, API keys, or paid credentials. Local PDFs remain under ignored dataset directories.
