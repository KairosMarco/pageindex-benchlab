# Baseline Diagnostics Summary

Date: 2026-06-22

## Purpose

This document replaces the earlier baseline planning notes with the current state of completed baseline diagnostics.

## Completed Baselines

| Baseline | Status | Notes |
|---|---|---|
| Long-context LLM | Complete on 25-question expanded subset | Matched `0.920` answer accuracy but had lower evidence recall and much higher token use |
| LlamaIndex Vector RAG | Complete on 25-question expanded subset | Reached `1.000` evidence recall and `0.920` answer accuracy with finance-aware reranking |
| LlamaIndex Hybrid RAG | Complete on 25-question expanded subset | Reached `1.000` evidence recall and `0.880` answer accuracy |
| PageIndex | Complete on 25-question expanded subset | Reached `1.000` evidence recall and `0.920` answer accuracy |

## Current Result

| Method | Evidence recall | Citation precision | Answer accuracy | Avg tokens |
|---|---:|---:|---:|---:|
| PageIndex | `1.000` | `0.347` | `0.920` | `2,882` |
| LlamaIndex Vector RAG | `1.000` | `0.360` | `0.920` | `2,543` |
| LlamaIndex Hybrid RAG | `1.000` | `0.360` | `0.880` | `2,553` |
| Long-context LLM | `0.800` | `0.267` | `0.920` | `92,500` |

Primary source:

```text
reports/expanded_cost_quality_summary.md
```

## Interpretation

- The expanded subset is useful for contribution diagnostics, but still too small for broad claims.
- Long-context did not solve citation grounding despite using far more tokens.
- Vector and PageIndex both reached the top answer accuracy in the current comparison.
- Remaining hard cases are mostly answer reasoning, rounding, or finance-definition issues.

## Next Baseline Work

Do not expand baselines just to add surface area. Next work should support a specific contribution or report:

1. Add GraphRAG only if a clear graph-specific question set is defined.
2. Add HyperGraphRAG only if n-ary relationship questions are defined.
3. Expand beyond finance only after the PageIndex upstream PRs receive review or merge.
