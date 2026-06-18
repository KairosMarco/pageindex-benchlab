# Expanded Cost and Quality Summary

Date: 2026-06-18

## Scope

This report compares committed expanded 25-question LLM artifacts. It does not run new model calls.

## Summary Table

| Method | Questions | Evidence recall | Citation precision | Answer accuracy | Avg tokens | Token x | Avg latency ms | Latency x | Answer issues | Evidence issues |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| LlamaIndex Vector RAG + finance concept_v2 rerank | 25 | 1.000 | 0.360 | 0.920 | 2543.200 | 1.000 | 16497.160 | 2.851 | fb_exp_017, fb_exp_020 | none |
| LlamaIndex Hybrid RAG + finance concept_v2 rerank | 25 | 1.000 | 0.360 | 0.880 | 2553.440 | 1.004 | 16846.440 | 2.911 | fb_exp_017, fb_exp_019, fb_exp_020 | none |
| PageIndex tree QA | 25 | 0.760 | 0.253 | 0.760 | 3045.680 | 1.198 | 5786.600 | 1.000 | fb_exp_017, fb_exp_019, fb_exp_020, fb_exp_022, fb_exp_023, fb_exp_025 | fb_exp_014, fb_exp_017, fb_exp_020, fb_exp_022, fb_exp_023, fb_exp_025 |
| Long-context LLM | 25 | 0.800 | 0.267 | 0.920 | 92499.560 | 36.371 | 12772.160 | 2.207 | fb_exp_020, fb_mvp_003 | fb_exp_014, fb_exp_017, fb_exp_020, fb_exp_023, fb_mvp_005 |

## Issue Overlap

- Answer issue union: `fb_exp_017, fb_exp_019, fb_exp_020, fb_exp_022, fb_exp_023, fb_exp_025, fb_mvp_003`
- Answer issue intersection: `fb_exp_020`
- Evidence issue union: `fb_exp_014, fb_exp_017, fb_exp_020, fb_exp_022, fb_exp_023, fb_exp_025, fb_mvp_005`
- Evidence issue intersection: `none`

## Interpretation

- LlamaIndex Vector and Long-context both reached `0.920` answer accuracy on the expanded subset.
- LlamaIndex Vector used the fewest average tokens and preserved `1.000` evidence recall.
- PageIndex used a small three-page context and modest tokens, but its expanded retrieval misses reduced answer accuracy to `0.760`.
- Long-context used far more average tokens than the lowest-token candidate while producing lower citation evidence recall than LlamaIndex Vector.
- `fb_exp_020` is the shared answer failure across all compared methods and should be treated as a high-value reasoning prompt or benchmark-analysis case.
- These results do not support broad PageIndex superiority claims yet; they identify PageIndex ranking robustness as the next contribution target.

## Source Reports

- LlamaIndex Vector RAG + finance concept_v2 rerank: `reports\llamaindex_expanded_llm_diagnostics.json`
- LlamaIndex Hybrid RAG + finance concept_v2 rerank: `reports\llamaindex_expanded_llm_diagnostics.json`
- PageIndex tree QA: `reports\pageindex_expanded_llm_diagnostics.json`
- Long-context LLM: `reports\long_context_expanded_llm_diagnostics.json`
