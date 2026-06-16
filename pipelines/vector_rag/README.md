# Vector RAG + Reranker Baseline

Recommended source:

- https://github.com/run-llama/llama_index

Goal:

```text
document -> chunks -> embeddings -> vector retrieval -> reranker -> answer
```

First task:

- Implement a LlamaIndex `VectorStoreIndex` baseline.
- Add a sentence-transformers reranker.
- Return citations and retrieved chunks.

## MVP Adapter

Implemented:

```text
pipelines/vector_rag/adapter.py
scripts/run_vector_rag_mvp.py
```

Current MVP mode:

```text
tfidf_vector_search_plus_rerank + optional LLM answer generation
```

This MVP intentionally has no new runtime dependency beyond PyMuPDF and LiteLLM. It uses pure-Python TF-IDF sparse vectors for first-stage retrieval, then a lightweight financial/legal phrase reranker. The next implementation step can replace this retrieval layer with LlamaIndex embeddings and a dedicated reranker.

No-LLM retrieval run:

```powershell
python scripts\run_vector_rag_mvp.py --no-llm --output-dir reports\vector_rag\qa_smoke --manifest reports\vector_rag\qa_smoke_manifest.json --force --continue-on-error
python scripts\evaluate_evidence_mvp.py --results-dir reports\vector_rag\qa_smoke --output reports\vector_rag\evidence_eval_smoke.json --continue-on-error
```

Current no-LLM retrieval result:

```text
12 / 12 outputs generated
Average evidence recall: 1.000
Average citation precision: 0.333
```

LLM answer run:

```powershell
$env:DEEPSEEK_API_KEY="YOUR_KEY"
python scripts\run_vector_rag_mvp.py --model deepseek/deepseek-v4-pro --output-dir reports\vector_rag\qa_llm --manifest reports\vector_rag\qa_llm_manifest.json --force --continue-on-error
python scripts\evaluate_evidence_mvp.py --results-dir reports\vector_rag\qa_llm --output reports\vector_rag\evidence_eval_llm.json --continue-on-error
```

Current LLM result with `deepseek/deepseek-v4-pro`:

```text
12 / 12 outputs generated
Average evidence recall: 1.000
Average citation precision: 0.333
```
