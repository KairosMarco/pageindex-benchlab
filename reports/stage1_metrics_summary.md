# Stage 1 Metrics Summary

Date: 2026-06-16

## Scope

This report aggregates evidence quality, answer accuracy, token usage, and latency for the current FinanceBench MVP LLM runs.

All rows use 12 MVP questions unless otherwise noted.

## Summary Table

| Method | Questions | Evidence recall | Citation precision | Answer accuracy | Avg input tokens | Avg total tokens | Total tokens | Avg latency ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| PageIndex | 12 | 1.000 | 0.333 | 1.000 | 2611.333 | 2984.250 | 35811 | 7156.750 |
| Long-context | 12 | 0.917 | 0.306 | 1.000 | 84449.833 | 84843.083 | 1018117 | 14938.500 |
| Vector RAG + reranker | 12 | 1.000 | 0.333 | 0.917 | 1973.750 | 2298.750 | 27585 | 7381.750 |
| Hybrid RAG | 12 | 1.000 | 0.333 | 1.000 | 1958.667 | 2412.500 | 28950 | 10130.667 |

## Notes

- PageIndex, Vector RAG, and Hybrid RAG hit every gold evidence page in this 12-question MVP subset.
- Long-context used far more input tokens because it sends full document text to the model.
- Vector RAG matched PageIndex on page-level evidence but had one LLM-judge answer miss on `fb_mvp_006`.
- Hybrid RAG matched PageIndex on page-level evidence and LLM-judge answer accuracy in this MVP subset.
- This report does not estimate monetary cost because provider pricing can vary by account and date.

## Artifact Paths

### PageIndex

- Results: `reports\pageindex\qa_llm`
- Evidence eval: `reports\pageindex\evidence_eval_llm.json`
- Answer eval: `reports\pageindex\answer_eval_llm.json`

### Long-context

- Results: `reports\long_context\qa_llm`
- Evidence eval: `reports\long_context\evidence_eval_llm.json`
- Answer eval: `reports\long_context\answer_eval_llm.json`

### Vector RAG + reranker

- Results: `reports\vector_rag\qa_llm`
- Evidence eval: `reports\vector_rag\evidence_eval_llm.json`
- Answer eval: `reports\vector_rag\answer_eval_llm.json`

### Hybrid RAG

- Results: `reports\hybrid_rag\qa_llm`
- Evidence eval: `reports\hybrid_rag\evidence_eval_llm.json`
- Answer eval: `reports\hybrid_rag\answer_eval_llm.json`
