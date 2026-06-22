# RAG Method Sources

This document records the comparison methods used or planned in PageIndex BenchLab. It is a source map, not a benchmark result.

## Active Methods

| Method | Status | Role | Primary source |
|---|---|---|---|
| PageIndex | Active | Main method under evaluation | https://github.com/VectifyAI/PageIndex |
| Long-context LLM | Active | Full-document context baseline | https://platform.openai.com/docs/api-reference/responses/create |
| LlamaIndex Vector RAG | Active | Semantic retrieval baseline | https://github.com/run-llama/llama_index |
| LlamaIndex Hybrid RAG | Active | BM25 + vector retrieval baseline | https://docs.llamaindex.ai/ |

## Planned Methods

| Method | Status | Role | Primary source |
|---|---|---|---|
| GraphRAG | Planned | Entity and relationship graph baseline | https://github.com/microsoft/graphrag |
| HyperGraphRAG | Planned | Hypergraph baseline for n-ary relations | https://github.com/LHRLAB/HyperGraphRAG |

## Evaluation Discipline

The benchmark should compare methods under the same:

- question set;
- source PDFs;
- citation-page budget;
- answer model;
- answer judge;
- evidence evaluator;
- token and latency accounting.

Avoid broad claims such as "PageIndex is better than RAG." The current evidence supports only scoped statements about the tested FinanceBench subset.

## Current Source Of Truth

Use these files for current results:

```text
README.md
docs/stage-1-status.md
reports/expanded_cost_quality_summary.md
```

Use these files for PageIndex contribution tracking:

```text
docs/upstream-pr-overview.md
docs/contributor-action-plan.md
```
