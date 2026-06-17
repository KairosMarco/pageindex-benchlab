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
```

Interpretation:

The generic embedding retriever often placed the gold page in a wider candidate set, but did not reliably rank the table evidence into the top three citations. The label-free finance-aware reranker improves top-three evidence retrieval on the 12-question FinanceBench MVP subset by boosting chunks that match the financial statement, year, and line item requested by the question.

This is still a retrieval-only diagnostic result. It should not be treated as a complete replacement for the dependency-light Vector RAG MVP until answer generation, evidence evaluation, and answer judging have been run under the same Stage 1 protocol.

Next work:

- Run LLM answer generation for `reports/llamaindex_vector_rag/qa_llm_finance/`.
- Run evidence evaluation and LLM answer judging for the generated answers.
- Promote this baseline into the main comparison only if the full answer-level report passes validation.
