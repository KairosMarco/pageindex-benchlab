# LlamaIndex Hybrid RAG Baseline

Goal:

```text
PDF pages -> LlamaIndex BM25 + vector retrieval -> RRF fusion -> rerank -> answer
```

Current status:

- Adapter implemented in `pipelines/llamaindex_hybrid_rag/adapter.py`.
- Batch runner implemented in `scripts/run_llamaindex_hybrid_rag_mvp.py`.
- Diagnostics have been run with generic reranking, a generic cross-encoder reranker, and finance-aware reranking.
- This baseline is not yet promoted into the main Stage 1 comparison table because LLM answer generation and answer judging have not been run for the finance-aware version.

Current diagnostic results:

```text
Generic reranker on fb_mvp_001, no LLM:
top-3 citations: evidence recall 0.000
top-6 citations: evidence recall 1.000, citation precision 0.167
top-12 citations: evidence recall 1.000, citation precision 0.091
cross-encoder rerank top-3: evidence recall 0.000

Finance-aware reranker, no LLM, max_citations=3:
questions: 12
failures: 0
evidence recall: 1.000
citation precision: 0.333

Finance-aware reranker, LLM, rerank_top_k=12:
questions: 12
failures: 0
evidence recall: 1.000
answer accuracy: 1.000
average total tokens: 9,216

Finance-aware reranker, LLM, rerank_top_k=3:
questions: 12
failures: 0
evidence recall: 1.000
answer accuracy: 1.000
average total tokens: 2,520
```

Interpretation:

The hybrid retriever can place the gold evidence page in the wider candidate set, but the generic reranker and tested generic cross-encoder did not reliably promote the table evidence into the top three citations. The label-free finance-aware reranker fixes this retrieval issue on the 12-question FinanceBench MVP subset by boosting chunks that match the requested financial statement, year, and line item.

The `rerank_top_k=3` LLM validation preserved answer accuracy while reducing average total tokens by about 73% versus the original `rerank_top_k=12` diagnostic. This is the recommended MVP configuration for the next larger-subset test.

Next work:

- Run the `rerank_top_k=3` configuration on a larger FinanceBench subset.
- Re-check whether the finance-aware reranker generalizes beyond the 12-question MVP subset.
- Compare answer accuracy, token usage, and latency against the existing PageIndex, Long-context, Vector RAG, and Hybrid RAG Stage 1 results.
