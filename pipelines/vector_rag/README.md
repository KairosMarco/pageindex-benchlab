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

