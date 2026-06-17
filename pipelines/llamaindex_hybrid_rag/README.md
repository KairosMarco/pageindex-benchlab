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
```

Interpretation:

The hybrid retriever can place the gold evidence page in the wider candidate set, but the generic reranker and tested generic cross-encoder did not reliably promote the table evidence into the top three citations. The label-free finance-aware reranker fixes this retrieval issue on the 12-question FinanceBench MVP subset by boosting chunks that match the requested financial statement, year, and line item.

This is still a retrieval-only diagnostic result. It should not be treated as a complete answer-level baseline until the LLM answer generation and answer judging steps have been run.

Next work:

- Run LLM answer generation for `reports/llamaindex_hybrid_rag/qa_llm_finance/`.
- Run evidence evaluation and LLM answer judging for the generated answers.
- Compare answer accuracy, token usage, and latency against the existing PageIndex, Long-context, Vector RAG, and Hybrid RAG Stage 1 results.
