# LlamaIndex Expanded Retrieval Diagnostics

Date: 2026-06-17

## Scope

This report runs retrieval-only LlamaIndex finance-aware candidates on the expanded FinanceBench subset. It does not evaluate LLM answer quality; it checks whether the low-context `rerank_top_k=3` setting still retrieves the gold evidence pages before spending answer-generation budget.

- Question file: `datasets\financebench\expanded_questions_25.jsonl`
- Variant suffix: default
- Chunking: `chunk_size=900`, `chunk_overlap=160`

## Results

| Method | rerank_top_k | Questions | Results | Coverage | Evidence recall | Citation precision | Avg context words | Manifest failures |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| LlamaIndex Vector RAG + finance rerank | 3 | 25 | 25 | 1.000 | 0.880 | 0.307 | 1126.560 | 0 |
| LlamaIndex Vector RAG + finance rerank | 6 | 25 | 25 | 1.000 | 0.880 | 0.293 | 2314.640 | 0 |
| LlamaIndex Vector RAG + finance rerank | 12 | 25 | 25 | 1.000 | 0.880 | 0.293 | 4565.600 | 0 |
| LlamaIndex Hybrid RAG + finance rerank | 3 | 25 | 25 | 1.000 | 0.840 | 0.293 | 1220.920 | 0 |
| LlamaIndex Hybrid RAG + finance rerank | 6 | 25 | 25 | 1.000 | 0.840 | 0.280 | 2515.360 | 0 |
| LlamaIndex Hybrid RAG + finance rerank | 12 | 25 | 25 | 1.000 | 0.840 | 0.280 | 5060.680 | 0 |

## Failure Cases

| Method | rerank_top_k | Question | Document | Gold pages | Predicted pages | Recall | Question type |
|---|---:|---|---|---|---|---:|---|
| LlamaIndex Vector RAG + finance rerank | 3 | `fb_exp_014` | `AMERICANEXPRESS_2022_10K` | 96 | 47, 54, 57 | 0.000 | domain-relevant |
| LlamaIndex Vector RAG + finance rerank | 3 | `fb_exp_020` | `CVSHEALTH_2022_10K` | 108, 110 | 81, 114, 70 | 0.000 | domain-relevant |
| LlamaIndex Vector RAG + finance rerank | 3 | `fb_exp_023` | `PFIZER_2021_10K` | 59 | 42, 64, 139 | 0.000 | novel-generated |
| LlamaIndex Vector RAG + finance rerank | 6 | `fb_exp_014` | `AMERICANEXPRESS_2022_10K` | 96 | 47, 54, 57 | 0.000 | domain-relevant |
| LlamaIndex Vector RAG + finance rerank | 6 | `fb_exp_020` | `CVSHEALTH_2022_10K` | 108, 110 | 81, 114, 70 | 0.000 | domain-relevant |
| LlamaIndex Vector RAG + finance rerank | 6 | `fb_exp_023` | `PFIZER_2021_10K` | 59 | 42, 64, 139 | 0.000 | novel-generated |
| LlamaIndex Vector RAG + finance rerank | 12 | `fb_exp_014` | `AMERICANEXPRESS_2022_10K` | 96 | 47, 54, 57 | 0.000 | domain-relevant |
| LlamaIndex Vector RAG + finance rerank | 12 | `fb_exp_020` | `CVSHEALTH_2022_10K` | 108, 110 | 81, 114, 70 | 0.000 | domain-relevant |
| LlamaIndex Vector RAG + finance rerank | 12 | `fb_exp_023` | `PFIZER_2021_10K` | 59 | 42, 64, 139 | 0.000 | novel-generated |
| LlamaIndex Hybrid RAG + finance rerank | 3 | `fb_exp_014` | `AMERICANEXPRESS_2022_10K` | 96 | 47, 147, 44 | 0.000 | domain-relevant |
| LlamaIndex Hybrid RAG + finance rerank | 3 | `fb_exp_017` | `CORNING_2022_10K` | 60 | 34, 61, 23 | 0.000 | domain-relevant |
| LlamaIndex Hybrid RAG + finance rerank | 3 | `fb_exp_020` | `CVSHEALTH_2022_10K` | 108, 110 | 70, 142, 4 | 0.000 | domain-relevant |
| LlamaIndex Hybrid RAG + finance rerank | 3 | `fb_exp_023` | `PFIZER_2021_10K` | 59 | 119, 41, 76 | 0.000 | novel-generated |
| LlamaIndex Hybrid RAG + finance rerank | 6 | `fb_exp_014` | `AMERICANEXPRESS_2022_10K` | 96 | 47, 147, 44 | 0.000 | domain-relevant |
| LlamaIndex Hybrid RAG + finance rerank | 6 | `fb_exp_017` | `CORNING_2022_10K` | 60 | 34, 61, 23 | 0.000 | domain-relevant |
| LlamaIndex Hybrid RAG + finance rerank | 6 | `fb_exp_020` | `CVSHEALTH_2022_10K` | 108, 110 | 70, 142, 4 | 0.000 | domain-relevant |
| LlamaIndex Hybrid RAG + finance rerank | 6 | `fb_exp_023` | `PFIZER_2021_10K` | 59 | 119, 41, 76 | 0.000 | novel-generated |
| LlamaIndex Hybrid RAG + finance rerank | 12 | `fb_exp_014` | `AMERICANEXPRESS_2022_10K` | 96 | 47, 147, 44 | 0.000 | domain-relevant |
| LlamaIndex Hybrid RAG + finance rerank | 12 | `fb_exp_017` | `CORNING_2022_10K` | 60 | 34, 61, 23 | 0.000 | domain-relevant |
| LlamaIndex Hybrid RAG + finance rerank | 12 | `fb_exp_020` | `CVSHEALTH_2022_10K` | 108, 110 | 70, 142, 4 | 0.000 | domain-relevant |
| LlamaIndex Hybrid RAG + finance rerank | 12 | `fb_exp_023` | `PFIZER_2021_10K` | 59 | 119, 41, 76 | 0.000 | novel-generated |

## Interpretation

- This is a generalization check for the 12-question MVP tuning result, not a final benchmark claim.
- A method should move to expanded LLM answer generation only if retrieval coverage is complete and evidence recall remains high enough to justify API cost.
- Failures in this report should be investigated per question before changing benchmark conclusions.
- The failed rows above show that this retrieval configuration is not ready for expanded LLM answer generation.

## Artifacts

### LlamaIndex Vector RAG + finance rerank

- rerank_top_k: `3`
- Results: `reports\llamaindex_vector_rag\expanded_questions_25_vector_r3_c900_o160`
- Manifest: `reports\llamaindex_vector_rag\expanded_questions_25_vector_r3_c900_o160_manifest.json`
- Evidence eval: `reports\llamaindex_vector_rag\evidence_eval_expanded_questions_25_vector_r3_c900_o160.json`

### LlamaIndex Vector RAG + finance rerank

- rerank_top_k: `6`
- Results: `reports\llamaindex_vector_rag\expanded_questions_25_vector_r6_c900_o160`
- Manifest: `reports\llamaindex_vector_rag\expanded_questions_25_vector_r6_c900_o160_manifest.json`
- Evidence eval: `reports\llamaindex_vector_rag\evidence_eval_expanded_questions_25_vector_r6_c900_o160.json`

### LlamaIndex Vector RAG + finance rerank

- rerank_top_k: `12`
- Results: `reports\llamaindex_vector_rag\expanded_questions_25_vector_r12_c900_o160`
- Manifest: `reports\llamaindex_vector_rag\expanded_questions_25_vector_r12_c900_o160_manifest.json`
- Evidence eval: `reports\llamaindex_vector_rag\evidence_eval_expanded_questions_25_vector_r12_c900_o160.json`

### LlamaIndex Hybrid RAG + finance rerank

- rerank_top_k: `3`
- Results: `reports\llamaindex_hybrid_rag\expanded_questions_25_hybrid_r3_c900_o160`
- Manifest: `reports\llamaindex_hybrid_rag\expanded_questions_25_hybrid_r3_c900_o160_manifest.json`
- Evidence eval: `reports\llamaindex_hybrid_rag\evidence_eval_expanded_questions_25_hybrid_r3_c900_o160.json`

### LlamaIndex Hybrid RAG + finance rerank

- rerank_top_k: `6`
- Results: `reports\llamaindex_hybrid_rag\expanded_questions_25_hybrid_r6_c900_o160`
- Manifest: `reports\llamaindex_hybrid_rag\expanded_questions_25_hybrid_r6_c900_o160_manifest.json`
- Evidence eval: `reports\llamaindex_hybrid_rag\evidence_eval_expanded_questions_25_hybrid_r6_c900_o160.json`

### LlamaIndex Hybrid RAG + finance rerank

- rerank_top_k: `12`
- Results: `reports\llamaindex_hybrid_rag\expanded_questions_25_hybrid_r12_c900_o160`
- Manifest: `reports\llamaindex_hybrid_rag\expanded_questions_25_hybrid_r12_c900_o160_manifest.json`
- Evidence eval: `reports\llamaindex_hybrid_rag\evidence_eval_expanded_questions_25_hybrid_r12_c900_o160.json`
