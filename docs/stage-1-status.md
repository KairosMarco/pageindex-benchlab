# Stage 1 Status

Date: 2026-06-16

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

## Current Ownership

For this stage, the project owner is taking over all active work.

PH is on standby and will be assigned implementation tasks later when available.

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

Important page-indexing rule:

```text
FinanceBench evidence pages are zero-indexed.
PageIndex tree pages appear one-indexed.
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

LLM answer generation command, after setting a provider key:

```powershell
$env:DEEPSEEK_API_KEY="YOUR_KEY"
D:\pageindex-demo\PageIndex\.venv\Scripts\python.exe scripts\run_pageindex_qa_mvp.py --model deepseek/deepseek-v4-pro --output-dir reports\pageindex\qa_llm --manifest reports\pageindex\qa_llm_manifest.json --force --continue-on-error
D:\pageindex-demo\PageIndex\.venv\Scripts\python.exe scripts\evaluate_evidence_mvp.py --results-dir reports\pageindex\qa_llm --output reports\pageindex\evidence_eval_llm.json --continue-on-error
```

This command was not run in the latest local shell because no model provider API key was available in the process environment.

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
D:\pageindex-demo\PageIndex\.venv\Scripts\python.exe scripts\run_long_context_mvp.py --no-llm --force --continue-on-error
D:\pageindex-demo\PageIndex\.venv\Scripts\python.exe scripts\evaluate_evidence_mvp.py --results-dir reports\long_context\qa --output reports\long_context\evidence_eval.json --continue-on-error
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
reports/long_context/qa/
reports/long_context/qa_manifest.json
reports/long_context/evidence_eval.json
reports/long_context/long_context_smoke_report.md
```

The no-LLM long-context run validates PDF loading, output schema, and evidence evaluator compatibility. It is not the final long-context LLM baseline.

## Next Stage 1 Work

The next work should convert this setup into actual benchmark execution:

1. Set a provider API key in the local shell and run PageIndex LLM answer generation.
2. Run Long-context LLM answer generation on the same 12 questions.
3. Implement Vector RAG + reranker baseline.
4. Generate the first cross-method benchmark report.

## Stage 1 Exit Criteria

Stage 1 is complete when:

- 12 FinanceBench MVP questions can be run through PageIndex. Completed for retrieval-only mode.
- At least one baseline can run on the same questions. Completed for Long-context no-LLM smoke mode; LLM mode still requires an API key in the current shell.
- All methods produce `BenchmarkResult`.
- Evidence recall and citation precision are reported.
- A Markdown benchmark report is generated under `reports/`.

## Current Blocker

Model-backed PageIndex indexing and QA require a provider API key in the current shell, usable provider quota, and reliable JSON output.

The first 11 structures are now available. The JSON parsing patch made PageIndex resilient to model noise:

```text
Handled empty responses and noisy JSON output
```

Next, build the PageIndex QA retrieval step and then start the baseline comparisons.
