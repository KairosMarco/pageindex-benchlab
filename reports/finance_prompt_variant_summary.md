# Finance Prompt Variant Summary

Date: 2026-06-17

## Scope

This report compares answer-prompt variants for the LlamaIndex Vector RAG expanded FinanceBench run.

- Question file: `datasets\financebench\expanded_questions_25.jsonl`
- Full-run question count: `25`
- Retrieval setup: `concept_v2`, `rerank_top_k=3`, `chunk_size=900`, `chunk_overlap=160`
- Model: `deepseek/deepseek-v4-pro`

## Full-run Summary

| Variant | Complete | Results | Evidence recall | Citation precision | Answer accuracy | Correct | Partial | Incorrect | Avg tokens | Avg latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| default prompt | yes | 25 | 1.000 | 0.360 | 0.920 | 23 | 1 | 1 | 2543.200 | 16497.160 |
| finance reasoning v2 | yes | 25 | 1.000 | 0.360 | 0.960 | 24 | 0 | 1 | 2885.240 | 22909.960 |
| finance reasoning v3 | yes | 25 | 1.000 | 0.360 | 0.920 | 23 | 2 | 0 | 2978.320 | 23454.760 |

## Probe Summary

| Probe | Results | Evidence recall | Citation precision | Answer accuracy | Correct | Partial | Incorrect |
|---|---:|---:|---:|---:|---:|---:|---:|
| v1 hard-case probe | 1 | 1.000 | 0.667 | 0.000 | 0 | 0 | 1 |
| v2 hard-case probe | 1 | 1.000 | 0.667 | 1.000 | 1 | 0 | 0 |
| v3 rounding plus hard-case probe | 2 | 1.000 | 0.500 | 1.000 | 2 | 0 | 0 |

## Key Question Outcomes

| Variant | `fb_exp_017` working capital | `fb_exp_019` rounding | `fb_exp_020` capital intensity | `fb_mvp_006` legal scope |
|---|---|---|---|---|
| default prompt | partial | correct | incorrect | correct |
| finance reasoning v2 | correct | incorrect | correct | correct |
| finance reasoning v3 | partial | correct | correct | partial |

## Non-correct Full-run Cases

| Variant | Question | Verdict | Rationale |
|---|---|---|---|
| default prompt | `fb_exp_017` | partial | The predicted answer correctly states that Corning has positive working capital, matching the gold answer's yes/no conclusion. However, it calculates working capital using total... |
| default prompt | `fb_exp_020` | incorrect | The predicted answer concludes 'No, CVS Health does not appear to be a highly capital-intensive business', while the gold answer states 'Yes, CVS Health requires an extensive as... |
| finance reasoning v2 | `fb_exp_019` | incorrect | The gold answer states $0.40 billion, but the predicted answer is $0.389 billion (approximately $0.39 billion). These amounts materially differ, and the predicted answer does no... |
| finance reasoning v3 | `fb_exp_017` | partial | The predicted answer correctly states that Corning had positive working capital in FY2022, which aligns with the gold answer's core conclusion. However, it calculates working ca... |
| finance reasoning v3 | `fb_mvp_006` | partial | The predicted answer correctly identifies that Boeing reported materially important ongoing legal battles and specifically mentions the lawsuits related to the 2018 Lion Air and... |

## Interpretation

- The default prompt remains the most stable committed baseline for cross-method comparison because it is short and less prescriptive.
- `finance_reasoning_v2` improved LlamaIndex Vector correct-only answer accuracy from `0.920` to `0.960`, fixing the capital-intensity failure, but it introduced a rounding-format failure on `fb_exp_019`.
- `finance_reasoning_v3` fixed both targeted probe questions (`fb_exp_019` and `fb_exp_020`) but the full run still had two partial answers, showing that stronger prompts can trade one failure mode for another.
- This supports a conservative next step: treat prompt engineering as an answer-generation ablation, not as a replacement for broader retrieval and evaluation improvements.

## Artifacts

### default prompt

- Diagnostics: `reports\llamaindex_expanded_llm_diagnostics.json`
- Results: `reports\llamaindex_vector_rag\qa_llm_expanded_25_concept_v2_r3`
- Evidence eval: `reports\llamaindex_vector_rag\evidence_eval_qa_llm_expanded_25_concept_v2_r3.json`
- Answer eval: `reports\llamaindex_vector_rag\answer_eval_qa_llm_expanded_25_concept_v2_r3.json`

### finance reasoning v2

- Diagnostics: `reports\llamaindex_expanded_llm_diagnostics_finance_reasoning_v2.json`
- Results: `reports\llamaindex_vector_rag\qa_llm_expanded_25_concept_v2_r3_finance_reasoning_v2`
- Evidence eval: `reports\llamaindex_vector_rag\evidence_eval_qa_llm_expanded_25_concept_v2_r3_finance_reasoning_v2.json`
- Answer eval: `reports\llamaindex_vector_rag\answer_eval_qa_llm_expanded_25_concept_v2_r3_finance_reasoning_v2.json`

### finance reasoning v3

- Diagnostics: `reports\llamaindex_expanded_llm_diagnostics_finance_reasoning_v3.json`
- Results: `reports\llamaindex_vector_rag\qa_llm_expanded_25_concept_v2_r3_finance_reasoning_v3`
- Evidence eval: `reports\llamaindex_vector_rag\evidence_eval_qa_llm_expanded_25_concept_v2_r3_finance_reasoning_v3.json`
- Answer eval: `reports\llamaindex_vector_rag\answer_eval_qa_llm_expanded_25_concept_v2_r3_finance_reasoning_v3.json`
