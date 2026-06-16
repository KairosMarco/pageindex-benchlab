# Stage 1 Retrieval Comparison

Date: 2026-06-16

## Current Comparable Results

| Method | Mode | Questions | Failures | Avg evidence recall | Avg citation precision | LLM-judge answer accuracy | Avg total tokens | Avg latency ms | Status |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| PageIndex | LLM answer generation, DeepSeek V4 Pro | 12 | 0 | 1.000 | 0.333 | 1.000 | 2,984 | 7,157 | Completed |
| Long-context | LLM answer generation, DeepSeek V4 Pro | 12 | 0 | 0.917 | 0.306 | 1.000 | 84,843 | 14,939 | Completed |
| Vector RAG + reranker | LLM answer generation, TF-IDF MVP + DeepSeek V4 Pro | 12 | 0 | 1.000 | 0.333 | 0.917 | 2,299 | 7,382 | Completed |
| Hybrid RAG | LLM answer generation, BM25 + TF-IDF RRF + DeepSeek V4 Pro | 12 | 0 | 1.000 | 0.333 | 1.000 | 2,413 | 10,131 | Completed |

Retrieval-only and smoke-test results are retained in method-specific report folders. The table above focuses on answer-generating LLM runs.

## Notes

- PageIndex, Vector RAG, and Hybrid RAG all hit every gold evidence page in the MVP subset.
- Long-context LLM reaches perfect judged answer accuracy but uses roughly 28x the average total tokens of PageIndex in this MVP run.
- The dependency-light Vector RAG MVP matches PageIndex on page-level evidence for this small subset after reranking, and uses the fewest tokens.
- Hybrid RAG matches PageIndex on page-level evidence and LLM-judge answer accuracy, with lower token usage than PageIndex but higher latency than PageIndex and Vector RAG in this run.
- LLM-judge answer accuracy separates the methods: PageIndex, Long-context, and Hybrid RAG were judged correct on all 12 questions; Vector RAG had one incorrect answer on `fb_mvp_006`.
- The Vector RAG miss is a useful failure case: it retrieved the correct legal-disclosure page, but the answer mixed the existence of lawsuits with Boeing's material-effect qualification.
- The next comparison needs a larger question set and stronger embedding-based Vector/Hybrid RAG implementations.

Detailed token and latency aggregation is available at:

```text
reports/stage1_metrics_summary.md
reports/stage1_metrics_summary.json
```

## Next Runs

```powershell
$env:DEEPSEEK_API_KEY="YOUR_KEY"

D:\pageindex-demo\PageIndex\.venv\Scripts\python.exe scripts\run_pageindex_qa_mvp.py --model deepseek/deepseek-v4-pro --output-dir reports\pageindex\qa_llm --manifest reports\pageindex\qa_llm_manifest.json --force --continue-on-error
D:\pageindex-demo\PageIndex\.venv\Scripts\python.exe scripts\evaluate_evidence_mvp.py --results-dir reports\pageindex\qa_llm --output reports\pageindex\evidence_eval_llm.json --continue-on-error

D:\pageindex-demo\PageIndex\.venv\Scripts\python.exe scripts\run_long_context_mvp.py --model deepseek/deepseek-v4-pro --output-dir reports\long_context\qa_llm --manifest reports\long_context\qa_llm_manifest.json --force --continue-on-error
D:\pageindex-demo\PageIndex\.venv\Scripts\python.exe scripts\evaluate_evidence_mvp.py --results-dir reports\long_context\qa_llm --output reports\long_context\evidence_eval_llm.json --continue-on-error

D:\pageindex-demo\PageIndex\.venv\Scripts\python.exe scripts\run_vector_rag_mvp.py --model deepseek/deepseek-v4-pro --output-dir reports\vector_rag\qa_llm --manifest reports\vector_rag\qa_llm_manifest.json --force --continue-on-error
D:\pageindex-demo\PageIndex\.venv\Scripts\python.exe scripts\evaluate_evidence_mvp.py --results-dir reports\vector_rag\qa_llm --output reports\vector_rag\evidence_eval_llm.json --continue-on-error

D:\pageindex-demo\PageIndex\.venv\Scripts\python.exe scripts\run_hybrid_rag_mvp.py --model deepseek/deepseek-v4-pro --output-dir reports\hybrid_rag\qa_llm --manifest reports\hybrid_rag\qa_llm_manifest.json --force --continue-on-error
D:\pageindex-demo\PageIndex\.venv\Scripts\python.exe scripts\evaluate_evidence_mvp.py --results-dir reports\hybrid_rag\qa_llm --output reports\hybrid_rag\evidence_eval_llm.json --continue-on-error

D:\pageindex-demo\PageIndex\.venv\Scripts\python.exe scripts\evaluate_answers_mvp.py --results-dir reports\pageindex\qa_llm --output reports\pageindex\answer_eval_llm.json --mode llm --model deepseek/deepseek-v4-pro --continue-on-error
D:\pageindex-demo\PageIndex\.venv\Scripts\python.exe scripts\evaluate_answers_mvp.py --results-dir reports\long_context\qa_llm --output reports\long_context\answer_eval_llm.json --mode llm --model deepseek/deepseek-v4-pro --continue-on-error
D:\pageindex-demo\PageIndex\.venv\Scripts\python.exe scripts\evaluate_answers_mvp.py --results-dir reports\vector_rag\qa_llm --output reports\vector_rag\answer_eval_llm.json --mode llm --model deepseek/deepseek-v4-pro --continue-on-error
D:\pageindex-demo\PageIndex\.venv\Scripts\python.exe scripts\evaluate_answers_mvp.py --results-dir reports\hybrid_rag\qa_llm --output reports\hybrid_rag\answer_eval_llm.json --mode llm --model deepseek/deepseek-v4-pro --continue-on-error
```
