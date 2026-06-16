# LlamaIndex Hybrid RAG Baseline

Goal:

```text
PDF pages -> LlamaIndex BM25 + vector retrieval -> RRF fusion -> rerank -> answer
```

Current status:

- Adapter implemented in `pipelines/llamaindex_hybrid_rag/adapter.py`.
- Batch runner implemented in `scripts/run_llamaindex_hybrid_rag_mvp.py`.
- Single-question diagnostics have been run for `fb_mvp_001`.
- This baseline is not yet promoted into the main Stage 1 comparison table.

Current diagnostic result on `fb_mvp_001`:

```text
top-3 citations: evidence recall 0.000
top-6 citations: evidence recall 1.000, citation precision 0.167
top-12 citations: evidence recall 1.000, citation precision 0.091
cross-encoder rerank top-3: evidence recall 0.000
```

Interpretation:

The hybrid retriever can place the gold evidence page in the wider candidate set, but the current reranker does not reliably rank the table evidence into the top three citations. The tested generic cross-encoder did not improve the first diagnostic case.

Next work:

- Add table-aware and financial-line-item-aware reranking.
- Test a finance-oriented embedding or reranker model.
- Run full 12-question no-LLM evaluation only after the single-question diagnostic improves.
