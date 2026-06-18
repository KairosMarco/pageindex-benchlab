# Expanded Cost and Quality Summary

Date: 2026-06-18

## Scope

This report compares committed expanded 25-question LLM artifacts. It does not run new model calls.

## Summary Table

| Method | Questions | Evidence recall | Citation precision | Answer accuracy | Avg tokens | Token x | Avg latency ms | Latency x | Answer issues | Evidence issues |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| LlamaIndex Vector RAG + finance concept_v2 rerank | 25 | 1.000 | 0.360 | 0.920 | 2543.200 | 1.000 | 16497.160 | 3.409 | fb_exp_017, fb_exp_020 | none |
| LlamaIndex Hybrid RAG + finance concept_v2 rerank | 25 | 1.000 | 0.360 | 0.880 | 2553.440 | 1.004 | 16846.440 | 3.481 | fb_exp_017, fb_exp_019, fb_exp_020 | none |
| PageIndex tree QA | 25 | 1.000 | 0.347 | 0.920 | 2882.160 | 1.133 | 4839.600 | 1.000 | fb_exp_019, fb_exp_020 | none |
| Long-context LLM | 25 | 0.800 | 0.267 | 0.920 | 92499.560 | 36.371 | 12772.160 | 2.639 | fb_exp_020, fb_mvp_003 | fb_exp_014, fb_exp_017, fb_exp_020, fb_exp_023, fb_mvp_005 |

## Issue Overlap

- Answer issue union: `fb_exp_017, fb_exp_019, fb_exp_020, fb_mvp_003`
- Answer issue intersection: `fb_exp_020`
- Evidence issue union: `fb_exp_014, fb_exp_017, fb_exp_020, fb_exp_023, fb_mvp_005`
- Evidence issue intersection: `none`

## Interpretation

- The top answer accuracy in this committed comparison is `0.920`.
- The lowest average-token method is `LlamaIndex Vector RAG + finance concept_v2 rerank` at `2543.200` tokens.
- PageIndex now preserves `1.000` evidence recall with a compact three-page answer context and reaches `0.920` answer accuracy.
- Long-context uses far more average tokens than the lowest-token candidate while producing lower citation evidence recall than the strongest retrieval candidates.
- `fb_exp_020` is the shared answer failure across all compared methods and should be treated as a high-value reasoning prompt or benchmark-analysis case.
- These results still do not support broad PageIndex superiority claims; they support a narrower finding that PageIndex can be competitive on this small expanded finance subset after ranking diagnostics and finance line-item scoring.

## Source Reports

- LlamaIndex Vector RAG + finance concept_v2 rerank: `reports\llamaindex_expanded_llm_diagnostics.json`
- LlamaIndex Hybrid RAG + finance concept_v2 rerank: `reports\llamaindex_expanded_llm_diagnostics.json`
- PageIndex tree QA: `reports\pageindex_expanded_llm_diagnostics.json`
- Long-context LLM: `reports\long_context_expanded_llm_diagnostics.json`
