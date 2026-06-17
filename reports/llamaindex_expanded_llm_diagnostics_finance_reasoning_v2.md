# LlamaIndex Expanded LLM Diagnostics

Date: 2026-06-17

## Scope

This report runs answer generation and answer judging for the lowest-context expanded LlamaIndex candidates that passed the retrieval-only precheck.

- Question file: `datasets\financebench\expanded_questions_25.jsonl`
- Question count: `25`
- Model: `deepseek/deepseek-v4-pro`
- Reranker variant label: `concept_v2`
- Answer prompt mode: `finance_reasoning_v2`
- Chunking: `chunk_size=900`, `chunk_overlap=160`
- Rerank top-k: `3`

The reranker uses only question text and candidate chunk text. Gold evidence pages are used only by the evaluator after generation.

## Summary

| Method | Status | Questions | Gen failures | Eval failures | Evidence recall | Citation precision | Answer accuracy | Avg total tokens | Avg context words | Avg latency ms | Gate |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| LlamaIndex Vector RAG + finance concept_v2 rerank | complete | 25 | 0 | 0 | 1.000 | 0.360 | 0.960 | 2885.240 | 1138.200 | 22909.960 | passed |

## Failure And Issue Cases

| Method | Issue | Question | Verdict/Recall | Gold pages | Predicted pages | Rationale |
|---|---|---|---:|---|---|---|
| LlamaIndex Vector RAG + finance concept_v2 rerank | answer | `fb_exp_019` | incorrect | 86 | 86, 66, 93 | The gold answer states $0.40 billion, but the predicted answer is $0.389 billion (approximately $0.39 billion). These amounts materially differ, and the predicted answer does no... |

## Per-question Diagnostics

| Method | Question | Evidence recall | Citation precision | Verdict | Total tokens | Context words | Latency ms |
|---|---|---:|---:|---|---:|---:|---:|
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_exp_013` | 1.000 | 0.333 | correct | 3106 | 989 | 24899 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_exp_014` | 1.000 | 0.333 | correct | 3480 | 1453 | 32302 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_exp_015` | 1.000 | 0.500 | correct | 2238 | 706 | 25423 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_exp_016` | 1.000 | 0.333 | correct | 3788 | 977 | 25114 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_exp_017` | 1.000 | 0.333 | correct | 2615 | 827 | 20469 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_exp_018` | 1.000 | 0.333 | correct | 3325 | 988 | 18955 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_exp_019` | 1.000 | 0.333 | incorrect | 2859 | 1324 | 23560 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_exp_020` | 1.000 | 0.667 | correct | 3344 | 1237 | 31072 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_exp_021` | 1.000 | 0.333 | correct | 2467 | 921 | 17435 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_exp_022` | 1.000 | 0.333 | correct | 2972 | 1532 | 27015 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_exp_023` | 1.000 | 0.333 | correct | 2658 | 867 | 21875 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_exp_024` | 1.000 | 0.333 | correct | 3162 | 1016 | 21518 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_exp_025` | 1.000 | 0.500 | correct | 2747 | 884 | 21407 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_mvp_001` | 1.000 | 0.333 | correct | 2808 | 1145 | 21094 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_mvp_002` | 1.000 | 0.333 | correct | 2141 | 797 | 25240 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_mvp_003` | 1.000 | 0.333 | correct | 3546 | 1815 | 23932 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_mvp_004` | 1.000 | 0.333 | correct | 2481 | 1064 | 20190 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_mvp_005` | 1.000 | 0.333 | correct | 3095 | 1180 | 25296 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_mvp_006` | 1.000 | 0.333 | correct | 2613 | 1273 | 28000 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_mvp_007` | 1.000 | 0.333 | correct | 2690 | 1084 | 20653 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_mvp_008` | 1.000 | 0.333 | correct | 2728 | 1289 | 16596 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_mvp_009` | 1.000 | 0.333 | correct | 2696 | 1179 | 17197 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_mvp_010` | 1.000 | 0.333 | correct | 3366 | 1504 | 20695 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_mvp_011` | 1.000 | 0.333 | correct | 2584 | 1164 | 23044 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_mvp_012` | 1.000 | 0.333 | correct | 2622 | 1240 | 19768 |

## Interpretation

- This is a prompt-variant diagnostic run. Compare it against the default-prompt expanded LLM baseline before making any quality claim.
- A stricter finance reasoning prompt is useful only if it fixes reasoning failures without causing regressions on extraction and arithmetic questions.

## Artifacts

### LlamaIndex Vector RAG + finance concept_v2 rerank

- Results: `reports\llamaindex_vector_rag\qa_llm_expanded_25_concept_v2_r3_finance_reasoning_v2`
- Manifest: `reports\llamaindex_vector_rag\qa_llm_expanded_25_concept_v2_r3_finance_reasoning_v2_manifest.json`
- Evidence eval: `reports\llamaindex_vector_rag\evidence_eval_qa_llm_expanded_25_concept_v2_r3_finance_reasoning_v2.json`
- Answer eval: `reports\llamaindex_vector_rag\answer_eval_qa_llm_expanded_25_concept_v2_r3_finance_reasoning_v2.json`
