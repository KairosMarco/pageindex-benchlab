# LlamaIndex Expanded LLM Diagnostics

Date: 2026-06-17

## Scope

This report runs answer generation and answer judging for the lowest-context expanded LlamaIndex candidates that passed the retrieval-only precheck.

- Question file: `datasets\financebench\expanded_questions_25.jsonl`
- Question count: `25`
- Model: `deepseek/deepseek-v4-pro`
- Reranker variant label: `concept_v2`
- Chunking: `chunk_size=900`, `chunk_overlap=160`
- Rerank top-k: `3`

The reranker uses only question text and candidate chunk text. Gold evidence pages are used only by the evaluator after generation.

## Summary

| Method | Status | Questions | Gen failures | Eval failures | Evidence recall | Citation precision | Answer accuracy | Avg total tokens | Avg context words | Avg latency ms | Gate |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| LlamaIndex Vector RAG + finance concept_v2 rerank | complete | 25 | 0 | 0 | 1.000 | 0.360 | 0.920 | 2543.200 | 1138.200 | 16497.160 | passed |
| LlamaIndex Hybrid RAG + finance concept_v2 rerank | complete | 25 | 0 | 0 | 1.000 | 0.360 | 0.880 | 2553.440 | 1160.440 | 16846.440 | passed |

## Failure And Issue Cases

| Method | Issue | Question | Verdict/Recall | Gold pages | Predicted pages | Rationale |
|---|---|---|---:|---|---|---|
| LlamaIndex Vector RAG + finance concept_v2 rerank | answer | `fb_exp_017` | partial | 60 | 60, 20, 104 | The predicted answer correctly states that Corning has positive working capital, matching the gold answer's yes/no conclusion. However, it calculates working capital using total... |
| LlamaIndex Vector RAG + finance concept_v2 rerank | answer | `fb_exp_020` | incorrect | 108, 110 | 110, 108, 133 | The predicted answer concludes 'No, CVS Health does not appear to be a highly capital-intensive business', while the gold answer states 'Yes, CVS Health requires an extensive as... |
| LlamaIndex Hybrid RAG + finance concept_v2 rerank | answer | `fb_exp_017` | partial | 60 | 60, 20, 34 | The predicted answer correctly states that Corning has positive working capital, which directly addresses the main question. However, it provides a working capital amount of $2,... |
| LlamaIndex Hybrid RAG + finance concept_v2 rerank | answer | `fb_exp_019` | partial | 86 | 86, 66, 93 | The predicted answer provides $0.389 billion (from $389 million), which is close to the gold answer of $0.40 billion, but does not match exactly. The difference likely stems fro... |
| LlamaIndex Hybrid RAG + finance concept_v2 rerank | answer | `fb_exp_020` | incorrect | 108, 110 | 110, 108, 70 | The predicted answer states that CVS Health is not a capital-intensive business based on a low fixed assets ratio of 5.6%, while the gold answer explicitly says Yes, it is capit... |

## Per-question Diagnostics

| Method | Question | Evidence recall | Citation precision | Verdict | Total tokens | Context words | Latency ms |
|---|---|---:|---:|---|---:|---:|---:|
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_exp_013` | 1.000 | 0.333 | correct | 2562 | 989 | 13908 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_exp_014` | 1.000 | 0.333 | correct | 3274 | 1453 | 26026 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_exp_015` | 1.000 | 0.500 | correct | 1948 | 706 | 12599 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_exp_016` | 1.000 | 0.333 | correct | 3261 | 977 | 19575 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_exp_017` | 1.000 | 0.333 | partial | 2343 | 827 | 18540 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_exp_018` | 1.000 | 0.333 | correct | 2748 | 988 | 14071 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_exp_019` | 1.000 | 0.333 | correct | 2534 | 1324 | 15388 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_exp_020` | 1.000 | 0.667 | incorrect | 2828 | 1237 | 20363 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_exp_021` | 1.000 | 0.333 | correct | 1977 | 921 | 11635 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_exp_022` | 1.000 | 0.333 | correct | 2653 | 1532 | 16977 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_exp_023` | 1.000 | 0.333 | correct | 2428 | 867 | 15420 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_exp_024` | 1.000 | 0.333 | correct | 2922 | 1016 | 16794 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_exp_025` | 1.000 | 0.500 | correct | 2650 | 884 | 17430 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_mvp_001` | 1.000 | 0.333 | correct | 2516 | 1145 | 16952 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_mvp_002` | 1.000 | 0.333 | correct | 1918 | 797 | 16495 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_mvp_003` | 1.000 | 0.333 | correct | 3251 | 1815 | 17488 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_mvp_004` | 1.000 | 0.333 | correct | 2181 | 1064 | 16444 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_mvp_005` | 1.000 | 0.333 | correct | 2517 | 1180 | 17715 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_mvp_006` | 1.000 | 0.333 | correct | 2394 | 1273 | 19229 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_mvp_007` | 1.000 | 0.333 | correct | 2376 | 1084 | 14180 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_mvp_008` | 1.000 | 0.333 | correct | 2463 | 1289 | 15282 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_mvp_009` | 1.000 | 0.333 | correct | 2404 | 1179 | 19518 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_mvp_010` | 1.000 | 0.333 | correct | 2982 | 1504 | 11355 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_mvp_011` | 1.000 | 0.333 | correct | 2098 | 1164 | 16880 |
| LlamaIndex Vector RAG + finance concept_v2 rerank | `fb_mvp_012` | 1.000 | 0.333 | correct | 2352 | 1240 | 12165 |
| LlamaIndex Hybrid RAG + finance concept_v2 rerank | `fb_exp_013` | 1.000 | 0.333 | correct | 2696 | 989 | 18461 |
| LlamaIndex Hybrid RAG + finance concept_v2 rerank | `fb_exp_014` | 1.000 | 0.333 | correct | 3079 | 1453 | 22332 |
| LlamaIndex Hybrid RAG + finance concept_v2 rerank | `fb_exp_015` | 1.000 | 0.500 | correct | 1880 | 706 | 12927 |
| LlamaIndex Hybrid RAG + finance concept_v2 rerank | `fb_exp_016` | 1.000 | 0.333 | correct | 3107 | 977 | 17023 |
| LlamaIndex Hybrid RAG + finance concept_v2 rerank | `fb_exp_017` | 1.000 | 0.333 | partial | 2697 | 1146 | 18279 |
| LlamaIndex Hybrid RAG + finance concept_v2 rerank | `fb_exp_018` | 1.000 | 0.333 | correct | 2704 | 1009 | 14253 |
| LlamaIndex Hybrid RAG + finance concept_v2 rerank | `fb_exp_019` | 1.000 | 0.333 | partial | 2510 | 1324 | 18797 |
| LlamaIndex Hybrid RAG + finance concept_v2 rerank | `fb_exp_020` | 1.000 | 0.667 | incorrect | 2188 | 838 | 20564 |
| LlamaIndex Hybrid RAG + finance concept_v2 rerank | `fb_exp_021` | 1.000 | 0.333 | correct | 2091 | 872 | 15594 |
| LlamaIndex Hybrid RAG + finance concept_v2 rerank | `fb_exp_022` | 1.000 | 0.333 | correct | 2545 | 1532 | 18461 |
| LlamaIndex Hybrid RAG + finance concept_v2 rerank | `fb_exp_023` | 1.000 | 0.333 | correct | 2408 | 867 | 18092 |
| LlamaIndex Hybrid RAG + finance concept_v2 rerank | `fb_exp_024` | 1.000 | 0.333 | correct | 2750 | 1016 | 14583 |
| LlamaIndex Hybrid RAG + finance concept_v2 rerank | `fb_exp_025` | 1.000 | 0.333 | correct | 2843 | 1126 | 16069 |
| LlamaIndex Hybrid RAG + finance concept_v2 rerank | `fb_mvp_001` | 1.000 | 0.333 | correct | 2483 | 1145 | 15819 |
| LlamaIndex Hybrid RAG + finance concept_v2 rerank | `fb_mvp_002` | 1.000 | 0.500 | correct | 2177 | 1189 | 15178 |
| LlamaIndex Hybrid RAG + finance concept_v2 rerank | `fb_mvp_003` | 1.000 | 0.333 | correct | 3213 | 1815 | 17787 |
| LlamaIndex Hybrid RAG + finance concept_v2 rerank | `fb_mvp_004` | 1.000 | 0.333 | correct | 2178 | 933 | 17092 |
| LlamaIndex Hybrid RAG + finance concept_v2 rerank | `fb_mvp_005` | 1.000 | 0.333 | correct | 2898 | 1407 | 17206 |
| LlamaIndex Hybrid RAG + finance concept_v2 rerank | `fb_mvp_006` | 1.000 | 0.333 | correct | 2402 | 1273 | 21243 |
| LlamaIndex Hybrid RAG + finance concept_v2 rerank | `fb_mvp_007` | 1.000 | 0.333 | correct | 2421 | 1084 | 17185 |
| LlamaIndex Hybrid RAG + finance concept_v2 rerank | `fb_mvp_008` | 1.000 | 0.333 | correct | 2505 | 1113 | 14995 |
| LlamaIndex Hybrid RAG + finance concept_v2 rerank | `fb_mvp_009` | 1.000 | 0.333 | correct | 2391 | 1179 | 14347 |
| LlamaIndex Hybrid RAG + finance concept_v2 rerank | `fb_mvp_010` | 1.000 | 0.333 | correct | 3007 | 1504 | 12389 |
| LlamaIndex Hybrid RAG + finance concept_v2 rerank | `fb_mvp_011` | 1.000 | 0.333 | correct | 2315 | 1274 | 18337 |
| LlamaIndex Hybrid RAG + finance concept_v2 rerank | `fb_mvp_012` | 1.000 | 0.333 | correct | 2348 | 1240 | 14148 |

## Interpretation

- This run should be treated as diagnostic evidence, not a final benchmark conclusion.
- Any issue rows above should be reviewed before promoting these candidates into the main comparison table.
- The larger subset is doing its job if it exposes answer, citation, or retrieval weaknesses that the 12-question MVP did not show.

## Artifacts

### LlamaIndex Vector RAG + finance concept_v2 rerank

- Results: `reports\llamaindex_vector_rag\qa_llm_expanded_25_concept_v2_r3`
- Manifest: `reports\llamaindex_vector_rag\qa_llm_expanded_25_concept_v2_r3_manifest.json`
- Evidence eval: `reports\llamaindex_vector_rag\evidence_eval_qa_llm_expanded_25_concept_v2_r3.json`
- Answer eval: `reports\llamaindex_vector_rag\answer_eval_qa_llm_expanded_25_concept_v2_r3.json`

### LlamaIndex Hybrid RAG + finance concept_v2 rerank

- Results: `reports\llamaindex_hybrid_rag\qa_llm_expanded_25_concept_v2_r3`
- Manifest: `reports\llamaindex_hybrid_rag\qa_llm_expanded_25_concept_v2_r3_manifest.json`
- Evidence eval: `reports\llamaindex_hybrid_rag\evidence_eval_qa_llm_expanded_25_concept_v2_r3.json`
- Answer eval: `reports\llamaindex_hybrid_rag\answer_eval_qa_llm_expanded_25_concept_v2_r3.json`
