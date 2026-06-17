# LlamaIndex Vector RAG Baseline

Goal:

```text
PDF pages -> LlamaIndex vector index -> retrieval -> lightweight rerank -> answer
```

Current status:

- Adapter implemented in `pipelines/llamaindex_vector_rag/adapter.py`.
- Batch runner implemented in `scripts/run_llamaindex_vector_rag_mvp.py`.
- Environment is ready according to `reports/stage1_environment_report.json`.
- No-LLM smoke runs have been executed with generic reranking and finance-aware reranking.
- This baseline is not yet promoted into the main Stage 1 comparison table because LLM answer generation and answer judging have not been run for the finance-aware version.

Current diagnostic results:

```text
Generic reranker, no LLM:
max_citations=3:  evidence recall 0.667, citation precision 0.222
max_citations=6:  evidence recall 0.833, citation precision 0.139
max_citations=12: evidence recall 0.917, citation precision 0.083

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
average total tokens: 8,964

Finance-aware reranker, LLM, rerank_top_k=3:
questions: 12
failures: 0
evidence recall: 1.000
answer accuracy: 1.000
average total tokens: 2,424

Expanded retrieval, concept_v2, no LLM, rerank_top_k=3:
questions: 25
failures: 0
evidence recall: 1.000
citation precision: 0.360
average context words: 1,138
```

Interpretation:

The generic embedding retriever often placed the gold page in a wider candidate set, but did not reliably rank the table evidence into the top three citations. The label-free finance-aware reranker improves top-three evidence retrieval on the 12-question FinanceBench MVP subset by boosting chunks that match the financial statement, year, and line item requested by the question.

The `rerank_top_k=3` LLM validation preserved answer accuracy while reducing average total tokens by about 73% versus the original `rerank_top_k=12` diagnostic. On the 25-question expanded retrieval set, the first finance-aware reranker failed several concept questions; the `concept_v2` label-free signals restored 1.000 page-level evidence recall in retrieval-only mode.

Next work:

- Run expanded LLM answer generation only for the `concept_v2`, `rerank_top_k=3` candidate.
- Compare answer accuracy, token usage, and latency against PageIndex and long-context baselines on the same 25 questions.
- Promote this baseline into the main comparison only after expanded answer evaluation passes validation.
