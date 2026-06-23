# RAG Method Sources

This document records the comparison methods used or planned in PageIndex BenchLab. It is a source map, not a benchmark result.

## Active Methods

| Method | Status | Role | Primary source |
|---|---|---|---|
| PageIndex | Active | Main method under evaluation | https://github.com/VectifyAI/PageIndex |
| Long-context LLM | Active | Full-document context baseline | https://platform.openai.com/docs/api-reference/responses/create |
| LlamaIndex Vector RAG | Active | Semantic retrieval baseline | https://github.com/run-llama/llama_index |
| LlamaIndex Hybrid RAG | Active | BM25 + vector retrieval baseline | https://docs.llamaindex.ai/ |
| BookRAG | Adapter preparation | Structural graph-tree baseline for complex documents | https://github.com/sam234990/BookRAG |
| Structured Tree-Graph RAG | Active local baseline | Independent minimal tree + entity graph retrieval baseline | `pipelines/structured_rag/` |

## Planned Methods

| Method | Status | Role | Primary source |
|---|---|---|---|
| GraphRAG | Planned | Entity and relationship graph baseline | https://github.com/microsoft/graphrag |
| HyperGraphRAG | Planned | Hypergraph baseline for n-ary relations | https://github.com/LHRLAB/HyperGraphRAG |

## Structural Graph-Tree Baseline

BookRAG is tracked separately from GraphRAG because it combines document hierarchy with entity relations and tree-graph mappings. In this benchmark, it should answer a specific comparison question:

> Does a heavier graph-tree index improve long-document QA enough to justify its setup and runtime cost compared with PageIndex's tree-only approach?

Primary sources:

- https://github.com/sam234990/BookRAG
- https://arxiv.org/abs/2512.03413
- https://arxiv.org/pdf/2512.03413
- https://www.51cto.com/aigc/11012.html

Integration notes:

- Keep BookRAG as an external checkout.
- Do not add BookRAG's heavy dependencies to the main BenchLab `requirements.txt`.
- Use `scripts/check_bookrag_readiness.py` before adapter work.
- Treat BookRAG result rows as excluded from the measured result table until at least one schema-valid output is produced and evaluated.
- Current adapter preparation includes dataset conversion, sidecar mapping, YAML config templates, and BookRAG config-load smoke checks.
- Use `pipelines/structured_rag/` as the independent local structural baseline while BookRAG runtime work continues.

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
