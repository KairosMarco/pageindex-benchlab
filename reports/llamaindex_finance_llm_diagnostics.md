# LlamaIndex Finance-aware LLM Diagnostics

Date: 2026-06-17

## Scope

This report is for candidate LlamaIndex baselines that use embedding retrieval plus a label-free finance-aware reranker.
It is separate from the main Stage 1 comparison table until answer generation, evidence evaluation, and answer judging are complete and reviewed.

## Summary

| Method | Status | Questions | Evidence recall | Citation precision | Answer accuracy | Avg total tokens | Avg latency ms | Failures |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| LlamaIndex Vector RAG + finance rerank | complete | 12 | 1.000 | 0.333 | 1.000 | 8963.583 | 16722.667 | 0 |
| LlamaIndex Hybrid RAG + finance rerank | complete | 12 | 1.000 | 0.333 | 1.000 | 9216.083 | 18595.500 | 0 |

## Comparison Context

The candidate rows below are compared against the existing committed Stage 1 answer-level rows. All rows use the same 12-question MVP subset and the same DeepSeek V4 Pro answer/judge protocol, but the LlamaIndex candidates use embedding retrieval plus the finance-aware reranker.

| Method | Group | Questions | Evidence recall | Citation precision | Answer accuracy | Avg total tokens | Avg latency ms |
|---|---|---:|---:|---:|---:|---:|---:|
| PageIndex | main_stage1 | 12 | 1.000 | 0.333 | 1.000 | 2984.250 | 7156.750 |
| Long-context | main_stage1 | 12 | 0.917 | 0.306 | 1.000 | 84843.083 | 14938.500 |
| Vector RAG + reranker | main_stage1 | 12 | 1.000 | 0.333 | 0.917 | 2298.750 | 7381.750 |
| Hybrid RAG | main_stage1 | 12 | 1.000 | 0.333 | 1.000 | 2412.500 | 10130.667 |
| LlamaIndex Vector RAG + finance rerank | candidate | 12 | 1.000 | 0.333 | 1.000 | 8963.583 | 16722.667 |
| LlamaIndex Hybrid RAG + finance rerank | candidate | 12 | 1.000 | 0.333 | 1.000 | 9216.083 | 18595.500 |

## Promotion Gate

Status: passed

Candidate rows should not be promoted into the main Stage 1 table until both methods have:

- 12 generated answer files.
- evidence eval and answer eval with zero evaluation failures.
- token usage and latency recorded for every question.
- reviewed failure cases if answer accuracy is below the existing Hybrid RAG baseline.

For this run, both candidate methods passed the mechanical promotion gate. The next decision is editorial: whether to add them to the main Stage 1 table now or keep them as stronger-baseline diagnostics until the larger FinanceBench subset is ready.

## Interpretation

- On this 12-question MVP subset, both finance-aware LlamaIndex candidates reached 1.000 evidence recall, 0.333 citation precision, and 1.000 LLM-judge answer accuracy.
- These results make the candidates materially stronger than the earlier generic LlamaIndex diagnostics.
- The candidates used substantially more average tokens than the current PageIndex, dependency-light Vector RAG, and dependency-light Hybrid RAG rows because the LlamaIndex runs pass more retrieved chunk text into answer generation.
- This still does not prove broad method superiority; the next larger subset must test whether the finance-aware reranker generalizes beyond the 12 MVP questions.

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
