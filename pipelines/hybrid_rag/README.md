# Hybrid RAG Baseline

Recommended source:

- https://docs.llamaindex.ai/

Goal:

```text
BM25 keyword retrieval + vector retrieval + fusion/rerank -> answer
```

First task:

- Implement LlamaIndex BM25 + vector fusion.
- Compare against Vector RAG + reranker.

## MVP Adapter

Implemented:

```text
pipelines/hybrid_rag/adapter.py
scripts/run_hybrid_rag_mvp.py
```

Current MVP mode:

```text
bm25_tfidf_rrf_plus_rerank + optional LLM answer generation
```

This MVP intentionally has no new runtime dependency beyond PyMuPDF and LiteLLM. It combines BM25-style lexical retrieval and TF-IDF vector retrieval with reciprocal-rank fusion, then applies the same lightweight reranking style used by the Vector RAG MVP.

No-LLM retrieval run:

```powershell
python scripts\run_hybrid_rag_mvp.py --no-llm --output-dir reports\hybrid_rag\qa_smoke --manifest reports\hybrid_rag\qa_smoke_manifest.json --force --continue-on-error
python scripts\evaluate_evidence_mvp.py --results-dir reports\hybrid_rag\qa_smoke --output reports\hybrid_rag\evidence_eval_smoke.json --continue-on-error
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
python scripts\run_hybrid_rag_mvp.py --model deepseek/deepseek-v4-pro --output-dir reports\hybrid_rag\qa_llm --manifest reports\hybrid_rag\qa_llm_manifest.json --force --continue-on-error
python scripts\evaluate_evidence_mvp.py --results-dir reports\hybrid_rag\qa_llm --output reports\hybrid_rag\evidence_eval_llm.json --continue-on-error
python scripts\evaluate_answers_mvp.py --results-dir reports\hybrid_rag\qa_llm --output reports\hybrid_rag\answer_eval_llm.json --mode llm --model deepseek/deepseek-v4-pro --continue-on-error
```

Current LLM result with `deepseek/deepseek-v4-pro`:

```text
12 / 12 outputs generated
Average evidence recall: 1.000
Average citation precision: 0.333
LLM-judge answer accuracy: 1.000
```
