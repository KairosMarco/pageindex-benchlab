# LlamaIndex Expanded Retrieval Diagnostics

Date: 2026-06-17

## Scope

This report runs retrieval-only LlamaIndex finance-aware candidates on the expanded FinanceBench subset. It does not evaluate LLM answer quality; it checks whether the low-context `rerank_top_k=3` setting still retrieves the gold evidence pages before spending answer-generation budget.

- Question file: `datasets\financebench\expanded_questions_25.jsonl`
- Variant suffix: `concept_v2`
- Chunking: `chunk_size=900`, `chunk_overlap=160`

## Results

| Method | rerank_top_k | Questions | Results | Coverage | Evidence recall | Citation precision | Avg context words | Manifest failures |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| LlamaIndex Vector RAG + finance rerank | 3 | 25 | 25 | 1.000 | 1.000 | 0.360 | 1138.200 | 0 |
| LlamaIndex Vector RAG + finance rerank | 6 | 25 | 25 | 1.000 | 1.000 | 0.347 | 2338.280 | 0 |
| LlamaIndex Vector RAG + finance rerank | 12 | 25 | 25 | 1.000 | 1.000 | 0.347 | 4570.520 | 0 |
| LlamaIndex Hybrid RAG + finance rerank | 3 | 25 | 25 | 1.000 | 1.000 | 0.360 | 1160.440 | 0 |
| LlamaIndex Hybrid RAG + finance rerank | 6 | 25 | 25 | 1.000 | 1.000 | 0.347 | 2500.720 | 0 |
| LlamaIndex Hybrid RAG + finance rerank | 12 | 25 | 25 | 1.000 | 1.000 | 0.347 | 5003.000 | 0 |

## Interpretation

- This is a generalization check for the 12-question MVP tuning result, not a final benchmark claim.
- A method should move to expanded LLM answer generation only if retrieval coverage is complete and evidence recall remains high enough to justify API cost.
- Failures in this report should be investigated per question before changing benchmark conclusions.
- No evidence failures were observed; `rerank_top_k=3` gives the smallest answer context among the passing variants.

## Artifacts

### LlamaIndex Vector RAG + finance rerank

- rerank_top_k: `3`
- Results: `reports\llamaindex_vector_rag\expanded_questions_25_vector_r3_c900_o160_concept_v2`
- Manifest: `reports\llamaindex_vector_rag\expanded_questions_25_vector_r3_c900_o160_concept_v2_manifest.json`
- Evidence eval: `reports\llamaindex_vector_rag\evidence_eval_expanded_questions_25_vector_r3_c900_o160_concept_v2.json`

### LlamaIndex Vector RAG + finance rerank

- rerank_top_k: `6`
- Results: `reports\llamaindex_vector_rag\expanded_questions_25_vector_r6_c900_o160_concept_v2`
- Manifest: `reports\llamaindex_vector_rag\expanded_questions_25_vector_r6_c900_o160_concept_v2_manifest.json`
- Evidence eval: `reports\llamaindex_vector_rag\evidence_eval_expanded_questions_25_vector_r6_c900_o160_concept_v2.json`

### LlamaIndex Vector RAG + finance rerank

- rerank_top_k: `12`
- Results: `reports\llamaindex_vector_rag\expanded_questions_25_vector_r12_c900_o160_concept_v2`
- Manifest: `reports\llamaindex_vector_rag\expanded_questions_25_vector_r12_c900_o160_concept_v2_manifest.json`
- Evidence eval: `reports\llamaindex_vector_rag\evidence_eval_expanded_questions_25_vector_r12_c900_o160_concept_v2.json`

### LlamaIndex Hybrid RAG + finance rerank

- rerank_top_k: `3`
- Results: `reports\llamaindex_hybrid_rag\expanded_questions_25_hybrid_r3_c900_o160_concept_v2`
- Manifest: `reports\llamaindex_hybrid_rag\expanded_questions_25_hybrid_r3_c900_o160_concept_v2_manifest.json`
- Evidence eval: `reports\llamaindex_hybrid_rag\evidence_eval_expanded_questions_25_hybrid_r3_c900_o160_concept_v2.json`

### LlamaIndex Hybrid RAG + finance rerank

- rerank_top_k: `6`
- Results: `reports\llamaindex_hybrid_rag\expanded_questions_25_hybrid_r6_c900_o160_concept_v2`
- Manifest: `reports\llamaindex_hybrid_rag\expanded_questions_25_hybrid_r6_c900_o160_concept_v2_manifest.json`
- Evidence eval: `reports\llamaindex_hybrid_rag\evidence_eval_expanded_questions_25_hybrid_r6_c900_o160_concept_v2.json`

### LlamaIndex Hybrid RAG + finance rerank

- rerank_top_k: `12`
- Results: `reports\llamaindex_hybrid_rag\expanded_questions_25_hybrid_r12_c900_o160_concept_v2`
- Manifest: `reports\llamaindex_hybrid_rag\expanded_questions_25_hybrid_r12_c900_o160_concept_v2_manifest.json`
- Evidence eval: `reports\llamaindex_hybrid_rag\evidence_eval_expanded_questions_25_hybrid_r12_c900_o160_concept_v2.json`
