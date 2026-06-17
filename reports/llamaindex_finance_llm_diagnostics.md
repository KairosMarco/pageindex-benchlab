# LlamaIndex Finance-aware LLM Diagnostics

Date: 2026-06-17

## Scope

This report is for candidate LlamaIndex baselines that use embedding retrieval plus a label-free finance-aware reranker.
It is separate from the main Stage 1 comparison table until answer generation, evidence evaluation, and answer judging are complete and reviewed.

## Summary

| Method | Status | Questions | Evidence recall | Citation precision | Answer accuracy | Avg total tokens | Avg latency ms | Failures |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| LlamaIndex Vector RAG + finance rerank | missing_artifacts | 0 | n/a | n/a | n/a | n/a | n/a | 0 |
| LlamaIndex Hybrid RAG + finance rerank | missing_artifacts | 0 | n/a | n/a | n/a | n/a | n/a | 0 |

## Promotion Gate

Do not promote these rows into the main Stage 1 table until both candidate methods have:

- 12 generated answer files.
- evidence eval and answer eval with zero evaluation failures.
- token usage and latency recorded for every question.
- reviewed failure cases if answer accuracy is below the existing Hybrid RAG baseline.

## Artifacts

### LlamaIndex Vector RAG + finance rerank

- Results: `reports\llamaindex_vector_rag\qa_llm_finance`
- Manifest: `reports\llamaindex_vector_rag\qa_llm_finance_manifest.json`
- Evidence eval: `reports\llamaindex_vector_rag\evidence_eval_llm_finance.json`
- Answer eval: `reports\llamaindex_vector_rag\answer_eval_llm_finance.json`

### LlamaIndex Hybrid RAG + finance rerank

- Results: `reports\llamaindex_hybrid_rag\qa_llm_finance`
- Manifest: `reports\llamaindex_hybrid_rag\qa_llm_finance_manifest.json`
- Evidence eval: `reports\llamaindex_hybrid_rag\evidence_eval_llm_finance.json`
- Answer eval: `reports\llamaindex_hybrid_rag\answer_eval_llm_finance.json`
