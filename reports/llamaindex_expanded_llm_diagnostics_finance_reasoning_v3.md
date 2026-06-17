# LlamaIndex Expanded LLM Diagnostics

Date: 2026-06-17

## Scope

This report runs answer generation and answer judging for the lowest-context expanded LlamaIndex candidates that passed the retrieval-only precheck.

- Question file: `datasets\financebench\expanded_questions_25.jsonl`
- Question count: `25`
- Model: `deepseek/deepseek-v4-pro`
- Reranker variant label: `concept_v2`
- Answer prompt mode: `finance_reasoning_v3`
- Chunking: `chunk_size=900`, `chunk_overlap=160`
- Rerank top-k: `3`

The reranker uses only question text and candidate chunk text. Gold evidence pages are used only by the evaluator after generation.

## Summary

| Method | Status | Questions | Gen failures | Eval failures | Evidence recall | Citation precision | Answer accuracy | Avg total tokens | Avg context words | Avg latency ms | Gate |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| LlamaIndex Vector RAG + finance concept_v2 rerank | complete | 25 | 0 | 0 | 1.000 | 0.360 | 0.920 | 2978.320 | 1138.200 | 23454.760 | passed |

## Failure And Issue Cases

| Method | Issue | Question | Verdict/Recall | Gold pages | Predicted pages | Rationale |
|---|---|---|---:|---|---|---|
| LlamaIndex Vector RAG + finance concept_v2 rerank | answer | `fb_exp_017` | partial | 60 | 60, 20, 104 | The predicted answer correctly states that Corning had positive working capital in FY2022, which aligns with the gold answer's core conclusion. However, it calculates working ca... |
| LlamaIndex Vector RAG + finance concept_v2 rerank | answer | `fb_mvp_006` | partial | 113 | 113, 19, 2 | The predicted answer correctly identifies that Boeing reported materially important ongoing legal battles and specifically mentions the lawsuits related to the 2018 Lion Air and... |

## Per-question Diagnostics

| Method | Question | Evidence recall | Citation precision | Verdict | Total tokens | Context words | Latency ms |
|---|---|---:|---:|---|---:|---:|---:|
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_exp_013` | 1.000 | 0.333 | correct | 3169 | 989 | 20446 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_exp_014` | 1.000 | 0.333 | correct | 3518 | 1453 | 32011 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_exp_015` | 1.000 | 0.500 | correct | 2322 | 706 | 19625 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_exp_016` | 1.000 | 0.333 | correct | 4022 | 977 | 36162 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_exp_017` | 1.000 | 0.333 | partial | 2681 | 827 | 20297 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_exp_018` | 1.000 | 0.333 | correct | 3312 | 988 | 19877 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_exp_019` | 1.000 | 0.333 | correct | 3130 | 1324 | 28964 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_exp_020` | 1.000 | 0.667 | correct | 3671 | 1237 | 33394 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_exp_021` | 1.000 | 0.333 | correct | 2368 | 921 | 14041 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_exp_022` | 1.000 | 0.333 | correct | 2962 | 1532 | 30646 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_exp_023` | 1.000 | 0.333 | correct | 2802 | 867 | 23555 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_exp_024` | 1.000 | 0.333 | correct | 3220 | 1016 | 23135 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_exp_025` | 1.000 | 0.500 | correct | 2782 | 884 | 16836 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_mvp_001` | 1.000 | 0.333 | correct | 3031 | 1145 | 25946 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_mvp_002` | 1.000 | 0.333 | correct | 2101 | 797 | 16164 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_mvp_003` | 1.000 | 0.333 | correct | 3904 | 1815 | 27081 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_mvp_004` | 1.000 | 0.333 | correct | 2650 | 1064 | 20644 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_mvp_005` | 1.000 | 0.333 | correct | 3080 | 1180 | 24924 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_mvp_006` | 1.000 | 0.333 | partial | 2884 | 1273 | 38334 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_mvp_007` | 1.000 | 0.333 | correct | 2776 | 1084 | 19797 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_mvp_008` | 1.000 | 0.333 | correct | 2843 | 1289 | 16709 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_mvp_009` | 1.000 | 0.333 | correct | 2816 | 1179 | 23234 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_mvp_010` | 1.000 | 0.333 | correct | 3283 | 1504 | 13678 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_mvp_011` | 1.000 | 0.333 | correct | 2436 | 1164 | 24288 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_mvp_012` | 1.000 | 0.333 | correct | 2695 | 1240 | 16581 |

## Interpretation

- This is a prompt-variant diagnostic run. Compare it against the default-prompt expanded LLM baseline before making any quality claim.
- A stricter finance reasoning prompt is useful only if it fixes reasoning failures without causing regressions on extraction and arithmetic questions.

## Artifacts

### LlamaIndex Vector RAG + finance concept_v2 rerank

- Results: `reports\llamaindex_vector_rag\qa_llm_expanded_25_concept_v2_r3_finance_reasoning_v3`
- Manifest: `reports\llamaindex_vector_rag\qa_llm_expanded_25_concept_v2_r3_finance_reasoning_v3_manifest.json`
- Evidence eval: `reports\llamaindex_vector_rag\evidence_eval_qa_llm_expanded_25_concept_v2_r3_finance_reasoning_v3.json`
- Answer eval: `reports\llamaindex_vector_rag\answer_eval_qa_llm_expanded_25_concept_v2_r3_finance_reasoning_v3.json`
