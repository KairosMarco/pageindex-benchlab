# Stage 1 Status

Date: 2026-06-18

## Current Stage

The project has moved from **Stage 0.5: project startup** to **Stage 1: MVP Benchmark Setup**.

Stage 1 means the repository now has enough structure to start running repeatable benchmark experiments:

- Shared benchmark result schema exists.
- FinanceBench MVP question subset exists.
- PageIndex local demo result is preserved.
- PageIndex tree output can be converted into the shared schema.
- PageIndex MVP question retrieval can run in batch.
- Evidence page evaluation logic exists.
- Upstream PageIndex dependency issue draft exists.
- FinanceBench MVP PDFs have a reproducible download script and local manifest.
- PageIndex, Long-context, Vector RAG, and Hybrid RAG baselines can run on the same MVP questions.

## Current Ownership

This stage has been executed independently by `KairosMarco`.

The previous collaboration split is no longer part of the active project plan.

## Contributor Outcome Status

The first PageIndex upstream PR candidate has moved from patch draft to a local PR-ready branch.

Local upstream workspace:

```text
D:\pageindex-upstream-pr
```

Branch and commit:

```text
fix/json-response-resilience
1cf28e5 Improve JSON extraction and TOC fallback handling
```

Validation:

```text
7 unittest tests passed
py_compile passed for touched PageIndex files
```

The PR has been opened upstream:

```text
https://github.com/VectifyAI/PageIndex/pull/333
```

The next step is monitoring maintainer feedback and responding quickly.

Exact commands are documented in:

```text
docs/pageindex-upstream-pr-handoff.md
```

A second documentation-only PageIndex PR candidate is also prepared:

```text
Workspace: D:\pageindex-upstream-pr
Branch: docs/windows-provider-quickstart
Commit: f650b6c Document Windows and LiteLLM provider setup
Validation: git diff --check passed
Handoff: docs/pageindex-docs-pr-handoff.md
PR: https://github.com/VectifyAI/PageIndex/pull/334
```

## Completed

### Unified Output Schema

Implemented in:

```text
benchlab/schemas.py
```

Core models:

- `BenchmarkQuestion`
- `BenchmarkResult`
- `Citation`
- `RetrievalTraceStep`
- `TokenUsage`
- `GoldEvidence`
- `EvidenceEvalResult`
- `AnswerEvalResult`

### FinanceBench MVP Subset

Implemented in:

```text
datasets/financebench/mvp_questions.jsonl
datasets/financebench/build_mvp_subset.py
```

The MVP subset contains 12 selected FinanceBench questions covering:

- information extraction
- numerical reasoning
- logical reasoning
- novel-generated questions

### PageIndex Adapter

Implemented in:

```text
pipelines/pageindex/adapter.py
```

Current adapter mode:

```text
index_only
```

The adapter converts PageIndex tree JSON into the shared benchmark result schema. It does not yet perform question answering.

Example command:

```powershell
python -m pipelines.pageindex.adapter examples\pageindex-demo\q1-fy25-earnings_structure.json --output reports\pageindex-demo-result.json
```

### Evidence Evaluator

Implemented in:

```text
evaluators/evidence.py
```

Current metrics:

- evidence recall
- citation precision
- answer accuracy

Important page-indexing rule:

```text
FinanceBench evidence pages are zero-indexed.
PageIndex tree pages appear one-indexed.
```

Answer accuracy is implemented in:

```text
evaluators/answer.py
scripts/evaluate_answers_mvp.py
```

Current answer evaluation modes:

```text
heuristic
llm judge
```

### Upstream PageIndex Issue Draft

Prepared in:

```text
docs/upstream-pageindex-dependency-issue.md
```

Issue topic:

```text
requirements.txt dependency conflict: litellm==1.83.7 vs python-dotenv==1.2.2
```

### MVP PDF Download

Implemented in:

```text
scripts/download_mvp_pdfs.py
```

Local PDFs are downloaded to:

```text
datasets/raw/financebench/pdfs/
```

This directory is ignored by git. A manifest is committed at:

```text
reports/mvp_pdf_manifest.json
```

Current MVP set:

```text
12 questions
11 unique PDFs
```

### PageIndex Batch Indexing Script

Implemented in:

```text
scripts/run_pageindex_mvp.py
```

The script is ready, but full indexing requires a local model provider key such as:

```text
DASHSCOPE_API_KEY
OPENAI_API_KEY
```

Dry-run command:

```powershell
python scripts\run_pageindex_mvp.py --dry-run --limit 3
```

Full command after setting a key:

```powershell
python scripts\run_pageindex_mvp.py
```

Current indexing status:

```text
11 / 11 unique MVP PDFs have PageIndex structure outputs.
```

Generated structures:

```text
reports/pageindex/structures/3M_2018_10K_structure.json
reports/pageindex/structures/AMAZON_2017_10K_structure.json
reports/pageindex/structures/AMCOR_2023Q4_EARNINGS_structure.json
reports/pageindex/structures/AMD_2022_10K_structure.json
reports/pageindex/structures/BESTBUY_2023_10K_structure.json
reports/pageindex/structures/BOEING_2022_10K_structure.json
reports/pageindex/structures/JOHNSON_JOHNSON_2023_8K_dated-2023-08-30_structure.json
reports/pageindex/structures/COSTCO_2021_10K_structure.json
reports/pageindex/structures/JPMORGAN_2023Q2_10Q_structure.json
reports/pageindex/structures/MICROSOFT_2016_10K_structure.json
reports/pageindex/structures/NIKE_2023_10K_structure.json
```

The current manifest is:

```text
reports/pageindex/indexing_manifest.json
```

Latest indexing run:

```text
Model: deepseek/deepseek-v4-pro
Generated: COSTCO_2021_10K, JPMORGAN_2023Q2_10Q, NIKE_2023_10K
Patch: strengthened JSON extraction and safe-fallback handling
```

Failure notes:

```text
The new JSON fallback logic allowed PageIndex to keep running even when DeepSeek returned empty or noisy responses.
```

### PageIndex QA Adapter

Implemented in:

```text
pipelines/pageindex/qa_adapter.py
```

Current mode:

```text
tree_page_scoring + optional LLM answer generation
```

The adapter can select candidate PageIndex tree nodes for a question and either output selected citations with `--no-llm` or call an LLM through LiteLLM when a model and provider key are available.

### PageIndex MVP QA Batch Run

Implemented in:

```text
scripts/run_pageindex_qa_mvp.py
scripts/evaluate_evidence_mvp.py
```

Latest retrieval-only command:

```powershell
D:\pageindex-demo\PageIndex\.venv\Scripts\python.exe scripts\run_pageindex_qa_mvp.py --no-llm --force --continue-on-error
D:\pageindex-demo\PageIndex\.venv\Scripts\python.exe scripts\evaluate_evidence_mvp.py --continue-on-error
```

Current no-LLM PageIndex retrieval status:

```text
12 / 12 MVP questions generated QA outputs.
0 failures.
Average evidence recall: 1.000
Average citation precision: 0.333
```

Generated artifacts:

```text
reports/pageindex/qa/
reports/pageindex/qa_manifest.json
reports/pageindex/evidence_eval.json
reports/pageindex/pageindex_qa_mvp_report.md
```

Current PageIndex LLM answer status:

```text
Model: deepseek/deepseek-v4-pro
12 / 12 MVP questions generated LLM answers.
0 failures.
Average evidence recall: 1.000
Average citation precision: 0.333
```

Generated LLM artifacts:

```text
reports/pageindex/qa_llm/
reports/pageindex/qa_llm_manifest.json
reports/pageindex/evidence_eval_llm.json
```

LLM answer generation command, after setting a provider key:

```powershell
$env:DEEPSEEK_API_KEY="YOUR_KEY"
D:\pageindex-demo\PageIndex\.venv\Scripts\python.exe scripts\run_pageindex_qa_mvp.py --model deepseek/deepseek-v4-pro --output-dir reports\pageindex\qa_llm --manifest reports\pageindex\qa_llm_manifest.json --force --continue-on-error
D:\pageindex-demo\PageIndex\.venv\Scripts\python.exe scripts\evaluate_evidence_mvp.py --results-dir reports\pageindex\qa_llm --output reports\pageindex\evidence_eval_llm.json --continue-on-error
```

### Long-context Baseline

Implemented in:

```text
pipelines/long_context/adapter.py
scripts/run_long_context_mvp.py
```

Current mode:

```text
full_document_context + optional LLM answer generation
```

No-LLM smoke test command:

```powershell
D:\pageindex-demo\PageIndex\.venv\Scripts\python.exe scripts\run_long_context_mvp.py --no-llm --output-dir reports\long_context\qa_smoke --manifest reports\long_context\qa_smoke_manifest.json --force --continue-on-error
D:\pageindex-demo\PageIndex\.venv\Scripts\python.exe scripts\evaluate_evidence_mvp.py --results-dir reports\long_context\qa_smoke --output reports\long_context\evidence_eval_smoke.json --continue-on-error
```

Current no-LLM smoke status:

```text
12 / 12 MVP questions generated outputs.
0 failures.
Average evidence recall: 0.583
Average citation precision: 0.194
```

Generated artifacts:

```text
reports/long_context/qa_smoke/
reports/long_context/qa_smoke_manifest.json
reports/long_context/evidence_eval_smoke.json
reports/long_context/long_context_smoke_report.md
```

The no-LLM long-context run validates PDF loading, output schema, and evidence evaluator compatibility. It is not the final long-context LLM baseline.

Current Long-context LLM status:

```text
Model: deepseek/deepseek-v4-pro
12 / 12 MVP questions generated LLM answers.
0 failures.
Average evidence recall: 0.917
Average citation precision: 0.306
```

Generated LLM artifacts:

```text
reports/long_context/qa_llm/
reports/long_context/qa_llm_manifest.json
reports/long_context/evidence_eval_llm.json
```

### Vector RAG + Reranker Baseline

Implemented in:

```text
pipelines/vector_rag/adapter.py
scripts/run_vector_rag_mvp.py
```

Current MVP mode:

```text
tfidf_vector_search_plus_rerank + optional LLM answer generation
```

This is a dependency-light baseline that uses pure-Python TF-IDF sparse vectors for retrieval and a lightweight reranker. It establishes the benchmark wiring before replacing the retrieval backend with LlamaIndex embeddings and a stronger reranker.

No-LLM retrieval command:

```powershell
D:\pageindex-demo\PageIndex\.venv\Scripts\python.exe scripts\run_vector_rag_mvp.py --no-llm --output-dir reports\vector_rag\qa_smoke --manifest reports\vector_rag\qa_smoke_manifest.json --force --continue-on-error
D:\pageindex-demo\PageIndex\.venv\Scripts\python.exe scripts\evaluate_evidence_mvp.py --results-dir reports\vector_rag\qa_smoke --output reports\vector_rag\evidence_eval_smoke.json --continue-on-error
```

Current no-LLM retrieval status:

```text
12 / 12 MVP questions generated outputs.
0 failures.
Average evidence recall: 1.000
Average citation precision: 0.333
```

LLM answer command:

```powershell
$env:DEEPSEEK_API_KEY="YOUR_KEY"
D:\pageindex-demo\PageIndex\.venv\Scripts\python.exe scripts\run_vector_rag_mvp.py --model deepseek/deepseek-v4-pro --output-dir reports\vector_rag\qa_llm --manifest reports\vector_rag\qa_llm_manifest.json --force --continue-on-error
D:\pageindex-demo\PageIndex\.venv\Scripts\python.exe scripts\evaluate_evidence_mvp.py --results-dir reports\vector_rag\qa_llm --output reports\vector_rag\evidence_eval_llm.json --continue-on-error
```

Current Vector RAG LLM status:

```text
Model: deepseek/deepseek-v4-pro
12 / 12 MVP questions generated LLM answers.
0 failures.
Average evidence recall: 1.000
Average citation precision: 0.333
```

### Hybrid RAG Baseline

Implemented in:

```text
pipelines/hybrid_rag/adapter.py
scripts/run_hybrid_rag_mvp.py
```

Current MVP mode:

```text
bm25_tfidf_rrf_plus_rerank + optional LLM answer generation
```

This is a dependency-light Hybrid RAG baseline. It combines BM25-style lexical retrieval and TF-IDF vector retrieval with reciprocal-rank fusion, then applies lightweight reranking. It establishes the benchmark wiring before replacing the retrieval backend with LlamaIndex embeddings and stronger rerankers.

No-LLM retrieval command:

```powershell
D:\pageindex-demo\PageIndex\.venv\Scripts\python.exe scripts\run_hybrid_rag_mvp.py --no-llm --output-dir reports\hybrid_rag\qa_smoke --manifest reports\hybrid_rag\qa_smoke_manifest.json --force --continue-on-error
D:\pageindex-demo\PageIndex\.venv\Scripts\python.exe scripts\evaluate_evidence_mvp.py --results-dir reports\hybrid_rag\qa_smoke --output reports\hybrid_rag\evidence_eval_smoke.json --continue-on-error
```

Current no-LLM retrieval status:

```text
12 / 12 MVP questions generated outputs.
0 failures.
Average evidence recall: 1.000
Average citation precision: 0.333
```

LLM answer command:

```powershell
$env:DEEPSEEK_API_KEY="YOUR_KEY"
D:\pageindex-demo\PageIndex\.venv\Scripts\python.exe scripts\run_hybrid_rag_mvp.py --model deepseek/deepseek-v4-pro --output-dir reports\hybrid_rag\qa_llm --manifest reports\hybrid_rag\qa_llm_manifest.json --force --continue-on-error
D:\pageindex-demo\PageIndex\.venv\Scripts\python.exe scripts\evaluate_evidence_mvp.py --results-dir reports\hybrid_rag\qa_llm --output reports\hybrid_rag\evidence_eval_llm.json --continue-on-error
```

Current Hybrid RAG LLM status:

```text
Model: deepseek/deepseek-v4-pro
12 / 12 MVP questions generated LLM answers.
0 failures.
Average evidence recall: 1.000
Average citation precision: 0.333
```

Current LLM-judge answer accuracy:

```text
PageIndex LLM: 12 / 12 correct, accuracy 1.000
Long-context LLM: 12 / 12 correct, accuracy 1.000
Vector RAG LLM: 11 / 12 correct, accuracy 0.917
Hybrid RAG LLM: 12 / 12 correct, accuracy 1.000
```

Current token and latency summary:

```text
PageIndex LLM: average total tokens 2,984; average latency 7,157 ms
Long-context LLM: average total tokens 84,843; average latency 14,939 ms
Vector RAG LLM: average total tokens 2,299; average latency 7,382 ms
Hybrid RAG LLM: average total tokens 2,413; average latency 10,131 ms
```

Generated aggregate reports:

```text
reports/stage1_metrics_summary.md
reports/stage1_metrics_summary.json
reports/stage1_detailed_evidence_report.md
reports/stage1_detailed_evidence_report.json
reports/stage1_per_question_results.csv
reports/stage1_validation_report.json
```

Current artifact validation:

```text
scripts/validate_stage1_artifacts.py
39 checks passed
0 failed checks
```

Generated Vector/Hybrid artifacts:

```text
reports/vector_rag/qa_smoke/
reports/vector_rag/qa_smoke_manifest.json
reports/vector_rag/evidence_eval_smoke.json
reports/vector_rag/qa_llm/
reports/vector_rag/qa_llm_manifest.json
reports/vector_rag/evidence_eval_llm.json
reports/hybrid_rag/qa_smoke/
reports/hybrid_rag/qa_smoke_manifest.json
reports/hybrid_rag/evidence_eval_smoke.json
reports/hybrid_rag/qa_llm/
reports/hybrid_rag/qa_llm_manifest.json
reports/hybrid_rag/evidence_eval_llm.json
```

### LlamaIndex Finance-aware Diagnostic Baselines

Implemented in:

```text
pipelines/llamaindex_vector_rag/adapter.py
pipelines/llamaindex_hybrid_rag/adapter.py
pipelines/finance_rerank.py
scripts/run_llamaindex_finance_llm_diagnostics.py
```

Current diagnostic mode:

```text
LlamaIndex embedding retrieval + label-free finance-aware reranking
```

The finance-aware reranker uses only the question text and candidate chunk text. It does not read FinanceBench gold evidence pages, so the retrieval diagnostic does not leak labels into ranking.

Current no-LLM retrieval diagnostics:

```text
LlamaIndex Vector RAG + finance rerank:
12 / 12 MVP questions generated outputs.
0 failures.
Average evidence recall: 1.000
Average citation precision: 0.333

LlamaIndex Hybrid RAG + finance rerank:
12 / 12 MVP questions generated outputs.
0 failures.
Average evidence recall: 1.000
Average citation precision: 0.333
```

Generated diagnostic artifacts:

```text
reports/llamaindex_vector_rag/qa_smoke_finance/
reports/llamaindex_vector_rag/qa_smoke_finance_manifest.json
reports/llamaindex_vector_rag/evidence_eval_smoke_finance.json
reports/llamaindex_hybrid_rag/qa_smoke_finance/
reports/llamaindex_hybrid_rag/qa_smoke_finance_manifest.json
reports/llamaindex_hybrid_rag/evidence_eval_smoke_finance.json
```

Current finance-aware LLM diagnostic status:

```text
Model: deepseek/deepseek-v4-pro

LlamaIndex Vector RAG + finance rerank:
12 / 12 MVP questions generated LLM answers.
0 generation or evaluation failures.
Average evidence recall: 1.000
Average citation precision: 0.333
LLM-judge answer accuracy: 1.000
Average total tokens: 8,964
Average latency: 16,723 ms

LlamaIndex Hybrid RAG + finance rerank:
12 / 12 MVP questions generated LLM answers.
0 generation or evaluation failures.
Average evidence recall: 1.000
Average citation precision: 0.333
LLM-judge answer accuracy: 1.000
Average total tokens: 9,216
Average latency: 18,596 ms
```

Current low-context tuning result:

```text
LlamaIndex Vector RAG + finance rerank, rerank_top_k=3:
12 / 12 MVP questions generated LLM answers.
0 generation or evaluation failures.
Average evidence recall: 1.000
LLM-judge answer accuracy: 1.000
Average total tokens: 2,424
Token reduction vs rerank_top_k=12: 73.0%

LlamaIndex Hybrid RAG + finance rerank, rerank_top_k=3:
12 / 12 MVP questions generated LLM answers.
0 generation or evaluation failures.
Average evidence recall: 1.000
LLM-judge answer accuracy: 1.000
Average total tokens: 2,520
Token reduction vs rerank_top_k=12: 72.7%
```

Generated LLM diagnostic artifacts:

```text
reports/llamaindex_finance_llm_diagnostics.md
reports/llamaindex_finance_llm_diagnostics.json
reports/llamaindex_vector_rag/qa_llm_finance/
reports/llamaindex_vector_rag/qa_llm_finance_manifest.json
reports/llamaindex_vector_rag/evidence_eval_llm_finance.json
reports/llamaindex_vector_rag/answer_eval_llm_finance.json
reports/llamaindex_hybrid_rag/qa_llm_finance/
reports/llamaindex_hybrid_rag/qa_llm_finance_manifest.json
reports/llamaindex_hybrid_rag/evidence_eval_llm_finance.json
reports/llamaindex_hybrid_rag/answer_eval_llm_finance.json
reports/llamaindex_context_tuning.md
reports/llamaindex_context_tuning.json
reports/llamaindex_vector_rag/qa_llm_finance_r3/
reports/llamaindex_vector_rag/qa_llm_finance_r3_manifest.json
reports/llamaindex_vector_rag/evidence_eval_llm_finance_r3.json
reports/llamaindex_vector_rag/answer_eval_llm_finance_r3.json
reports/llamaindex_hybrid_rag/qa_llm_finance_r3/
reports/llamaindex_hybrid_rag/qa_llm_finance_r3_manifest.json
reports/llamaindex_hybrid_rag/evidence_eval_llm_finance_r3.json
reports/llamaindex_hybrid_rag/answer_eval_llm_finance_r3.json
```

LLM diagnostic command, after setting a provider key:

```powershell
$env:DEEPSEEK_API_KEY="YOUR_KEY"
D:\pageindex-demo\PageIndex\.venv\Scripts\python.exe scripts\run_llamaindex_finance_llm_diagnostics.py --force --continue-on-error
```

These LlamaIndex finance-aware rows pass the mechanical promotion gate on the 12-question MVP subset. They remain documented as stronger-baseline diagnostics until expanded answer generation is run on the 25-question subset.

### Expanded FinanceBench Retrieval Diagnostics

The expanded retrieval set is:

```text
datasets/financebench/expanded_questions_25.jsonl
```

It contains 25 questions, preserving the original 12 MVP questions and adding 13 deterministic balanced FinanceBench selections.

PDF manifest:

```text
reports/expanded_25_pdf_manifest.json
```

Validation:

```text
reports/expanded_retrieval_validation_report.json
status: pass
checks: 22
failed: 0
```

Default expanded retrieval result, before concept-signal improvement:

```text
LlamaIndex Vector RAG + finance rerank:
questions: 25
failures: 0 generation failures
evidence recall: 0.880
failure cases: fb_exp_014, fb_exp_020, fb_exp_023

LlamaIndex Hybrid RAG + finance rerank:
questions: 25
failures: 0 generation failures
evidence recall: 0.840
failure cases: fb_exp_014, fb_exp_017, fb_exp_020, fb_exp_023
```

The default failures are documented in:

```text
reports/llamaindex_expanded_retrieval.md
reports/llamaindex_expanded_retrieval.json
```

`concept_v2` expanded retrieval result:

```text
LlamaIndex Vector RAG + finance rerank, rerank_top_k=3:
questions: 25
failures: 0
evidence recall: 1.000
citation precision: 0.360
average context words: 1,138

LlamaIndex Hybrid RAG + finance rerank, rerank_top_k=3:
questions: 25
failures: 0
evidence recall: 1.000
citation precision: 0.360
average context words: 1,160
```

The `concept_v2` results are documented in:

```text
reports/llamaindex_expanded_retrieval_concept_v2.md
reports/llamaindex_expanded_retrieval_concept_v2.json
```

Interpretation:

- The 12-question MVP result did not fully generalize to 25 questions.
- The failures were mostly concept-heavy finance questions: financial-services gross margin, working capital, capital intensity, and PPNE growth.
- The improved reranker still uses only question text and candidate chunk text. It does not inspect FinanceBench gold evidence pages during retrieval.
- Expanded LLM answer generation should use `concept_v2` with `rerank_top_k=3`, because it preserved retrieval recall with the smallest context.

### Expanded LlamaIndex LLM Diagnostics

Expanded answer generation has now been run for the validated `concept_v2`, `rerank_top_k=3` LlamaIndex candidates on:

```text
datasets/financebench/expanded_questions_25.jsonl
```

Model:

```text
deepseek/deepseek-v4-pro
```

Aggregate report:

```text
reports/llamaindex_expanded_llm_diagnostics.md
reports/llamaindex_expanded_llm_diagnostics.json
```

Validation:

```text
reports/expanded_llm_validation_report.json
status: pass
checks: 37
failed: 0
```

Expanded LLM results:

```text
LlamaIndex Vector RAG + finance concept_v2 rerank:
questions: 25
generation failures: 0
evaluation failures: 0
evidence recall: 1.000
citation precision: 0.360
LLM-judge answer accuracy: 0.920
verdicts: 23 correct, 1 partial, 1 incorrect
average total tokens: 2,543
average context words: 1,138
average latency: 16,497 ms

LlamaIndex Hybrid RAG + finance concept_v2 rerank:
questions: 25
generation failures: 0
evaluation failures: 0
evidence recall: 1.000
citation precision: 0.360
LLM-judge answer accuracy: 0.880
verdicts: 22 correct, 2 partial, 1 incorrect
average total tokens: 2,553
average context words: 1,160
average latency: 16,846 ms
```

Generated artifacts:

```text
reports/llamaindex_vector_rag/qa_llm_expanded_25_concept_v2_r3/
reports/llamaindex_vector_rag/qa_llm_expanded_25_concept_v2_r3_manifest.json
reports/llamaindex_vector_rag/evidence_eval_qa_llm_expanded_25_concept_v2_r3.json
reports/llamaindex_vector_rag/answer_eval_qa_llm_expanded_25_concept_v2_r3.json
reports/llamaindex_hybrid_rag/qa_llm_expanded_25_concept_v2_r3/
reports/llamaindex_hybrid_rag/qa_llm_expanded_25_concept_v2_r3_manifest.json
reports/llamaindex_hybrid_rag/evidence_eval_qa_llm_expanded_25_concept_v2_r3.json
reports/llamaindex_hybrid_rag/answer_eval_qa_llm_expanded_25_concept_v2_r3.json
```

Interpretation:

- The expanded LLM run passed the mechanical artifact gate for both candidates.
- Retrieval was not the limiting factor in the observed answer failures: both methods kept `1.000` page-level evidence recall.
- The remaining failures are answer-generation or judge-strictness issues after successful evidence retrieval:
  - `fb_exp_017`: Corning working capital. Both methods answered the direction correctly but used total current assets minus total current liabilities instead of the gold answer's operating-current-assets/liabilities definition.
  - `fb_exp_019`: American Water Works dividends. Hybrid answered `$0.389 billion`; the judge marked this partial against the rounded gold answer `$0.40`.
  - `fb_exp_020`: CVS capital intensity. Both methods retrieved the gold pages but concluded `No` by focusing on fixed assets / total assets, while the gold answer says `Yes` based on low ROA and the broader asset base including goodwill.
- This strengthens the LlamaIndex baseline relative to the 12-question MVP, but it does not support broad PageIndex superiority claims.

### Expanded Long-context LLM Diagnostics

The Long-context baseline has now been run on the same 25-question expanded set:

```text
datasets/financebench/expanded_questions_25.jsonl
```

Model:

```text
deepseek/deepseek-v4-pro
```

Aggregate report:

```text
reports/long_context_expanded_llm_diagnostics.md
reports/long_context_expanded_llm_diagnostics.json
```

Validation:

```text
reports/expanded_long_context_validation_report.json
status: pass
checks: 21
failed: 0
```

Expanded Long-context result:

```text
Long-context LLM:
questions: 25
generation failures: 0
evaluation failures: 0
evidence recall: 0.800
citation precision: 0.267
LLM-judge answer accuracy: 0.920
verdicts: 23 correct, 1 partial, 1 incorrect
average total tokens: 92,500
average context chars: 397,913
average context pages: 113
average latency: 12,772 ms
```

Generated artifacts:

```text
reports/long_context/qa_llm_expanded_25/
reports/long_context/qa_llm_expanded_25_manifest.json
reports/long_context/evidence_eval_qa_llm_expanded_25.json
reports/long_context/answer_eval_qa_llm_expanded_25.json
```

Interpretation:

- Long-context matched LlamaIndex Vector's expanded answer accuracy (`0.920`) but used about `36x` more average total tokens.
- Long-context evidence recall was materially lower (`0.800`) because answer generation and citation selection did not consistently cite the FinanceBench gold pages.
- Long-context correctly answered several questions even when cited pages did not match gold evidence, which separates answer quality from citation quality.
- The shared hard failure remains `fb_exp_020`: CVS capital intensity. Long-context also concluded `No` by focusing on capex/revenue and leased stores, while the gold answer says `Yes` based on low ROA and the broader asset base including goodwill.

### Expanded Cost And Quality Summary

Cross-method expanded summary:

```text
reports/expanded_cost_quality_summary.md
reports/expanded_cost_quality_summary.json
```

Summary:

```text
LlamaIndex Vector concept_v2 r3:
answer accuracy: 0.920
evidence recall: 1.000
average total tokens: 2,543
token multiplier: 1.000x

LlamaIndex Hybrid concept_v2 r3:
answer accuracy: 0.880
evidence recall: 1.000
average total tokens: 2,553
token multiplier: 1.004x

Long-context LLM:
answer accuracy: 0.920
evidence recall: 0.800
average total tokens: 92,500
token multiplier: 36.371x
```

Shared answer issue:

```text
fb_exp_020
```

Interpretation:

- On this expanded 25-question subset, Long-context did not improve answer accuracy over LlamaIndex Vector.
- Long-context was far more token-expensive and had weaker citation grounding.
- The shared `fb_exp_020` failure should be used as a targeted reasoning-prompt or benchmark-analysis case before making claims about method superiority.

### Finance Prompt Variant Ablation

The LlamaIndex Vector answer-generation prompt now supports explicit prompt modes. The default prompt remains the main cross-method baseline. The finance prompts are an answer-generation ablation intended to test whether stricter financial reasoning instructions fix failures after evidence retrieval has already succeeded.

Summary report:

```text
reports/finance_prompt_variant_summary.md
reports/finance_prompt_variant_summary.json
```

Validated prompt-variant artifacts:

```text
reports/expanded_llm_validation_report_finance_reasoning_v2.json
reports/expanded_llm_validation_report_finance_reasoning_v3.json
```

Full-run Vector results:

```text
Default prompt:
questions: 25
evidence recall: 1.000
answer accuracy: 0.920
verdicts: 23 correct, 1 partial, 1 incorrect
average total tokens: 2,543

finance_reasoning_v2:
questions: 25
evidence recall: 1.000
answer accuracy: 0.960
verdicts: 24 correct, 0 partial, 1 incorrect
average total tokens: 2,885

finance_reasoning_v3:
questions: 25
evidence recall: 1.000
answer accuracy: 0.920
verdicts: 23 correct, 2 partial, 0 incorrect
average total tokens: 2,978
```

Targeted probes:

```text
finance_reasoning_v1 probe on fb_exp_020:
answer accuracy: 0.000

finance_reasoning_v2 probe on fb_exp_020:
answer accuracy: 1.000

finance_reasoning_v3 probe on fb_exp_019 and fb_exp_020:
answer accuracy: 1.000
```

Interpretation:

- `finance_reasoning_v2` fixed `fb_exp_020` capital-intensity reasoning and improved correct-only answer accuracy to `0.960`, but it introduced a rounding-format failure on `fb_exp_019`.
- `finance_reasoning_v3` fixed both targeted probe questions, but the full run still had two partial answers: `fb_exp_017` working-capital definition and `fb_mvp_006` extra legal-scope detail.
- Stronger prompts can trade one answer failure mode for another. This should be reported as a prompt ablation, not as a replacement for the default cross-method comparison.

## PageIndex Expanded Readiness

The expanded PageIndex run is now mechanically complete for the 25-question subset.

Readiness artifacts:

```text
reports/pageindex/expanded_readiness.md
reports/pageindex/expanded_readiness.json
```

Current coverage:

```text
Questions: 25
Unique source documents: 24
Documents with PageIndex structures and PDFs: 24
Runnable questions with current structures: 25
Missing PageIndex structures: 0
Missing PDFs: 0
Full expanded PageIndex QA ready: true
```

Expanded PageIndex retrieval-only QA has been run for the full set:

```text
Generated QA outputs: 25
Failed QA outputs: 0
Average evidence recall: 1.000
Average citation precision: 0.347
```

Artifacts:

```text
reports/pageindex/expanded_indexing_notes.md
reports/pageindex/expanded_partial_summary.md
reports/pageindex/expanded_partial_summary.json
reports/pageindex/qa_expanded_25_manifest.json
reports/pageindex/evidence_eval_qa_expanded_25.json
reports/pageindex/pageindex_ranking_diagnostics.md
reports/pageindex/pageindex_ranking_diagnostics.json
```

Expanded PageIndex LLM answer generation has also been run:

```text
Model: deepseek/deepseek-v4-pro
Generated answers: 25 / 25
Generation failures: 0
Evaluation failures: 0
Evidence recall: 1.000
Citation precision: 0.347
Answer accuracy: 0.920
Verdicts: 23 correct, 0 partial, 2 incorrect
Average total tokens: 2,882
Average latency: 4,840 ms
Validation: pass, 20 checks, 0 failed
```

Artifacts:

```text
reports/pageindex_expanded_llm_diagnostics.md
reports/pageindex_expanded_llm_diagnostics.json
reports/expanded_pageindex_llm_validation_report.json
reports/pageindex/qa_llm_expanded_25/
reports/pageindex/qa_llm_expanded_25_manifest.json
reports/pageindex/evidence_eval_qa_llm_expanded_25.json
reports/pageindex/answer_eval_qa_llm_expanded_25.json
```

Observed indexing robustness issues fixed locally:

- `PFIZER_2021_10K` failed because PageIndex attempted to add an integer page number to a missing page-offset value.
- `CVSHEALTH_2022_10K` needed a low-confidence no-TOC fallback rather than a hard `Processing failed` exception.
- `COCACOLA_2021_10K` needed defensive handling when `add_page_number_to_toc()` returned JSON without `physical_index`.
- `AMERICANWATERWORKS_2020_10K` succeeded when run as a single-document indexing job.

Interpretation:

- The initial PageIndex expanded scorer did not generalize to the 25-question set, but the current label-free finance line-item boost restores top-three evidence recall to `1.000`.
- PageIndex used a compact three-page answer context. The remaining answer issues are `fb_exp_019` and `fb_exp_020`, both after successful evidence retrieval.
- The ranking diagnostics now provide a before/after contribution artifact: legacy scorer recall `0.760`, current scorer recall `1.000`, with no candidate regressions.
- The answer issue analysis separates `fb_exp_019` as a rounding or judge-policy case from `fb_exp_020` as a capital-intensity reasoning case.

Answer issue artifacts:

```text
reports/pageindex/pageindex_answer_issue_analysis.md
reports/pageindex/pageindex_answer_issue_analysis.json
```

### PageIndex Answer Prompt Ablation

The PageIndex QA adapter now supports the same answer-prompt modes used by the LlamaIndex prompt diagnostics:

```text
default
finance_reasoning_v1
finance_reasoning_v2
finance_reasoning_v3
```

The default prompt remains the committed cross-method PageIndex baseline. The finance prompts are diagnostic answer-generation ablations.

Targeted probes were run for the two remaining PageIndex expanded answer issues:

```text
Target questions: fb_exp_019, fb_exp_020
Model: deepseek/deepseek-v4-pro
```

Results:

```text
Default prompt, full 25-question baseline:
evidence recall: 1.000
answer accuracy: 0.920
target outcomes: fb_exp_019 incorrect, fb_exp_020 incorrect

finance_reasoning_v2 probe:
questions: 2
evidence recall: 1.000
answer accuracy: 0.500
verdicts: 1 correct, 0 partial, 1 incorrect
target outcomes: fb_exp_019 incorrect, fb_exp_020 correct

finance_reasoning_v3 probe:
questions: 2
evidence recall: 1.000
answer accuracy: 1.000
verdicts: 2 correct, 0 partial, 0 incorrect
target outcomes: fb_exp_019 correct, fb_exp_020 correct
```

Generated artifacts:

```text
reports/pageindex/pageindex_prompt_variant_summary.md
reports/pageindex/pageindex_prompt_variant_summary.json
reports/pageindex/qa_llm_expanded_25_finance_reasoning_v2_probe/
reports/pageindex/qa_llm_expanded_25_finance_reasoning_v2_probe_manifest.json
reports/pageindex/evidence_eval_qa_llm_expanded_25_finance_reasoning_v2_probe.json
reports/pageindex/answer_eval_qa_llm_expanded_25_finance_reasoning_v2_probe.json
reports/pageindex/qa_llm_expanded_25_finance_reasoning_v3_probe/
reports/pageindex/qa_llm_expanded_25_finance_reasoning_v3_probe_manifest.json
reports/pageindex/evidence_eval_qa_llm_expanded_25_finance_reasoning_v3_probe.json
reports/pageindex/answer_eval_qa_llm_expanded_25_finance_reasoning_v3_probe.json
```

Interpretation:

- `fb_exp_019` is still primarily a rounding or judge-policy case. The v3 prompt fixed it by returning `$0.40 billion ($389 million)`.
- `fb_exp_020` is a finance concept-definition case. The v2 and v3 prompts fixed it by applying a broad asset-intensity definition with ROA and total asset-base evidence.
- This does not replace the default 25-question PageIndex baseline. A full 25-question prompt-variant run is required before using v3 as a cross-method comparison row.

## Upstream Contribution Drafts

Two PageIndex contribution drafts are ready for review and community use:

```text
docs/upstream-pageindex-benchmark-issue.md
docs/upstream-pageindex-ranking-diagnostics-note.md
docs/upstream-patches/pageindex-json-resilience-pr.md
```

The issue draft presents the benchmark plan conservatively: PageIndex has strong MVP evidence recall and a current expanded result that is competitive on this small finance subset after ranking diagnostics. The PR draft focuses on robust JSON extraction and conservative fallbacks for noisy model responses.

The first contributor-oriented PageIndex PR candidate is now prepared as a direct patch:

```text
docs/upstream-patches/pageindex-json-resilience.patch
docs/upstream-patches/pageindex-json-resilience-pr-ready.md
```

Patch scope:

- robust `extract_json()` handling for fenced, embedded, array, trailing-text, and Python-literal JSON responses;
- safe defaults for missing TOC detector and completion fields;
- normalization of model-produced TOC JSON before list operations;
- conservative fallback when page offsets or `physical_index` values are missing;
- focused `unittest` coverage.

Patch validation:

```text
D:\pageindex-demo\PageIndex\.venv\Scripts\python.exe -m unittest discover -s tests
Ran 7 tests
OK

D:\pageindex-demo\PageIndex\.venv\Scripts\python.exe -m py_compile pageindex\utils.py pageindex\page_index.py tests\test_json_resilience.py
passed
```

This is the current highest-priority contributor action because it can become a concrete upstream PR. Benchmark discussion should be opened separately after this PR is in flight.

## Next Stage 1 Work

The next work should strengthen the benchmark beyond the dependency-light MVP baselines:

1. Fork PageIndex and open the JSON response resilience PR using `docs/upstream-patches/pageindex-json-resilience-pr-ready.md`.
2. Respond to maintainer review quickly; split the patch if requested.
3. Turn the PageIndex ranking diagnostics note into a small upstream benchmark/retrieval discussion after the code PR is open.
4. Decide whether to run a full 25-question PageIndex `finance_reasoning_v3` prompt-variant ablation or keep it as a targeted diagnostic only.
5. Consider evaluator refinements for rounding tolerance and capital-intensity reasoning before broader prompt tuning.
6. Add GraphRAG and HyperGraphRAG after the expanded baselines are stable.

## Stage 1 Exit Criteria

Stage 1 is complete when:

- 12 FinanceBench MVP questions can be run through PageIndex. Completed for retrieval-only mode.
- At least one baseline can run on the same questions. Completed for Long-context LLM mode.
- All methods produce `BenchmarkResult`. Completed for PageIndex, Long-context, Vector RAG, and Hybrid RAG.
- Evidence recall, citation precision, and answer accuracy are reported. Completed for PageIndex, Long-context, Vector RAG, and Hybrid RAG.
- A Markdown benchmark report is generated under `reports/`. Completed for current evidence-focused report.

## Current Blocker

There is no mechanical blocker for PageIndex expanded QA now. The remaining blocker is methodological: the 25-question finance subset is still too small to support broad PageIndex superiority claims, and the two remaining PageIndex answer issues need reasoning or evaluator analysis.
