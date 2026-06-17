# LlamaIndex Context Tuning Diagnostics

Date: 2026-06-17

## Scope

This retrieval-only tuning report tests whether finance-aware LlamaIndex candidates can preserve page-level evidence recall while sending fewer chunks into answer generation.

## Results

| Method | rerank_top_k | chunk size | overlap | Evidence recall | Citation precision | Avg context words | Avg latency ms |
|---|---:|---:|---:|---:|---:|---:|---:|
| LlamaIndex Vector RAG + finance rerank | 3 | 900 | 160 | 1.000 | 0.333 | 1218.917 | 10751.750 |
| LlamaIndex Vector RAG + finance rerank | 6 | 900 | 160 | 1.000 | 0.333 | 2612.583 | 11928.250 |
| LlamaIndex Vector RAG + finance rerank | 9 | 900 | 160 | 1.000 | 0.333 | 3912.583 | 10254.417 |
| LlamaIndex Vector RAG + finance rerank | 12 | 900 | 160 | 1.000 | 0.333 | 5097.750 | 11926.750 |
| LlamaIndex Hybrid RAG + finance rerank | 3 | 900 | 160 | 1.000 | 0.347 | 1254.083 | 11068.333 |
| LlamaIndex Hybrid RAG + finance rerank | 6 | 900 | 160 | 1.000 | 0.333 | 2691.250 | 12328.583 |
| LlamaIndex Hybrid RAG + finance rerank | 9 | 900 | 160 | 1.000 | 0.333 | 4217.083 | 10883.500 |
| LlamaIndex Hybrid RAG + finance rerank | 12 | 900 | 160 | 1.000 | 0.333 | 5545.250 | 13379.667 |

## Lowest-context Passing Variants

| Method | rerank_top_k | chunk size | overlap | Avg context words | Evidence recall |
|---|---:|---:|---:|---:|---:|
| LlamaIndex Vector RAG + finance rerank | 3 | 900 | 160 | 1218.917 | 1.000 |
| LlamaIndex Hybrid RAG + finance rerank | 3 | 900 | 160 | 1254.083 | 1.000 |
| LlamaIndex Vector RAG + finance rerank | 6 | 900 | 160 | 2612.583 | 1.000 |
| LlamaIndex Hybrid RAG + finance rerank | 6 | 900 | 160 | 2691.250 | 1.000 |

## LLM Validation

The lowest-context passing variant, `rerank_top_k=3`, was then run with the same DeepSeek V4 Pro answer and judge protocol used by Stage 1.

| Method | rerank_top_k | Questions | Evidence recall | Citation precision | Answer accuracy | Avg total tokens | Avg latency ms |
|---|---:|---:|---:|---:|---:|---:|---:|
| LlamaIndex Vector RAG + finance rerank | 12 | 12 | 1.000 | 0.333 | 1.000 | 8963.583 | 16722.667 |
| LlamaIndex Vector RAG + finance rerank | 3 | 12 | 1.000 | 0.333 | 1.000 | 2423.833 | 17524.750 |
| LlamaIndex Hybrid RAG + finance rerank | 12 | 12 | 1.000 | 0.333 | 1.000 | 9216.083 | 18595.500 |
| LlamaIndex Hybrid RAG + finance rerank | 3 | 12 | 1.000 | 0.347 | 1.000 | 2520.417 | 18389.667 |

## Token Reduction

| Method | Baseline rerank_top_k | Tuned rerank_top_k | Avg tokens before | Avg tokens after | Reduction | Reduction % | Answer accuracy after |
|---|---:|---:|---:|---:|---:|---:|---:|
| LlamaIndex Vector RAG + finance rerank | 12 | 3 | 8963.583 | 2423.833 | 6539.750 | 72.959 | 1.000 |
| LlamaIndex Hybrid RAG + finance rerank | 12 | 3 | 9216.083 | 2520.417 | 6695.666 | 72.652 | 1.000 |

## Interpretation

- The retrieval-only grid shows that `rerank_top_k=3` preserves page-level evidence recall while reducing answer context from 12 chunks to 3 chunks.
- The LLM validation confirms that `rerank_top_k=3` preserved 1.000 LLM-judge answer accuracy on the 12-question MVP subset.
- This supports using `rerank_top_k=3` as the next LlamaIndex finance-aware default for the MVP subset, while still requiring a larger subset before making broad claims.

## Artifacts

### LlamaIndex Vector RAG + finance rerank r3 c900 o160

- Results: `reports\llamaindex_vector_rag\context_tuning_vector_r3_c900_o160`
- Manifest: `reports\llamaindex_vector_rag\context_tuning_vector_r3_c900_o160_manifest.json`
- Evidence eval: `reports\llamaindex_vector_rag\evidence_eval_context_tuning_vector_r3_c900_o160.json`

### LlamaIndex Vector RAG + finance rerank r6 c900 o160

- Results: `reports\llamaindex_vector_rag\context_tuning_vector_r6_c900_o160`
- Manifest: `reports\llamaindex_vector_rag\context_tuning_vector_r6_c900_o160_manifest.json`
- Evidence eval: `reports\llamaindex_vector_rag\evidence_eval_context_tuning_vector_r6_c900_o160.json`

### LlamaIndex Vector RAG + finance rerank r9 c900 o160

- Results: `reports\llamaindex_vector_rag\context_tuning_vector_r9_c900_o160`
- Manifest: `reports\llamaindex_vector_rag\context_tuning_vector_r9_c900_o160_manifest.json`
- Evidence eval: `reports\llamaindex_vector_rag\evidence_eval_context_tuning_vector_r9_c900_o160.json`

### LlamaIndex Vector RAG + finance rerank r12 c900 o160

- Results: `reports\llamaindex_vector_rag\context_tuning_vector_r12_c900_o160`
- Manifest: `reports\llamaindex_vector_rag\context_tuning_vector_r12_c900_o160_manifest.json`
- Evidence eval: `reports\llamaindex_vector_rag\evidence_eval_context_tuning_vector_r12_c900_o160.json`

### LlamaIndex Hybrid RAG + finance rerank r3 c900 o160

- Results: `reports\llamaindex_hybrid_rag\context_tuning_hybrid_r3_c900_o160`
- Manifest: `reports\llamaindex_hybrid_rag\context_tuning_hybrid_r3_c900_o160_manifest.json`
- Evidence eval: `reports\llamaindex_hybrid_rag\evidence_eval_context_tuning_hybrid_r3_c900_o160.json`

### LlamaIndex Hybrid RAG + finance rerank r6 c900 o160

- Results: `reports\llamaindex_hybrid_rag\context_tuning_hybrid_r6_c900_o160`
- Manifest: `reports\llamaindex_hybrid_rag\context_tuning_hybrid_r6_c900_o160_manifest.json`
- Evidence eval: `reports\llamaindex_hybrid_rag\evidence_eval_context_tuning_hybrid_r6_c900_o160.json`

### LlamaIndex Hybrid RAG + finance rerank r9 c900 o160

- Results: `reports\llamaindex_hybrid_rag\context_tuning_hybrid_r9_c900_o160`
- Manifest: `reports\llamaindex_hybrid_rag\context_tuning_hybrid_r9_c900_o160_manifest.json`
- Evidence eval: `reports\llamaindex_hybrid_rag\evidence_eval_context_tuning_hybrid_r9_c900_o160.json`

### LlamaIndex Hybrid RAG + finance rerank r12 c900 o160

- Results: `reports\llamaindex_hybrid_rag\context_tuning_hybrid_r12_c900_o160`
- Manifest: `reports\llamaindex_hybrid_rag\context_tuning_hybrid_r12_c900_o160_manifest.json`
- Evidence eval: `reports\llamaindex_hybrid_rag\evidence_eval_context_tuning_hybrid_r12_c900_o160.json`
