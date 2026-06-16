# LlamaIndex Vector RAG Baseline

Goal:

```text
PDF pages -> LlamaIndex vector index -> retrieval -> lightweight rerank -> answer
```

Current status:

- Adapter implemented in `pipelines/llamaindex_vector_rag/adapter.py`.
- Batch runner implemented in `scripts/run_llamaindex_vector_rag_mvp.py`.
- Environment is ready according to `reports/stage1_environment_report.json`.
- No-LLM smoke runs have been executed, but this baseline is not yet promoted into the main Stage 1 comparison table.

Current diagnostic results:

```text
max_citations=3:  evidence recall 0.667, citation precision 0.222
max_citations=6:  evidence recall 0.833, citation precision 0.139
max_citations=12: evidence recall 0.917, citation precision 0.083
```

Interpretation:

The embedding retriever often has the gold page in a wider candidate set, but the current lightweight reranker and top citation selection are not strong enough. This baseline should not yet be treated as a stronger replacement for the dependency-light Vector RAG MVP.

Next work:

- Add a stronger reranker or cross-encoder reranker.
- Add a LlamaIndex Hybrid RAG variant with BM25 + vector retrieval + fusion.
- Re-run LLM answer generation only after retrieval quality is acceptable.
