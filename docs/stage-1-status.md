# Stage 1 Status

Date: 2026-06-15

## Current Stage

The project has moved from **Stage 0.5: project startup** to **Stage 1: MVP Benchmark Setup**.

Stage 1 means the repository now has enough structure to start running repeatable benchmark experiments:

- Shared benchmark result schema exists.
- FinanceBench MVP question subset exists.
- PageIndex local demo result is preserved.
- PageIndex tree output can be converted into the shared schema.
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
8 / 11 unique MVP PDFs have PageIndex structure outputs.
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
reports/pageindex/structures/MICROSOFT_2016_10K_structure.json
```

The current manifest is:

```text
reports/pageindex/indexing_manifest.json
```

Latest indexing run:

```text
Model: deepseek/deepseek-v4-pro
Generated: MICROSOFT_2016_10K
Failed: COSTCO_2021_10K, JPMORGAN_2023Q2_10Q, NIKE_2023_10K
```

Failure notes:

```text
DeepSeek V4 Pro is reachable and generated MICROSOFT_2016_10K.
COSTCO, JPMORGAN, and NIKE failed because PageIndex expected JSON fields that were missing from model output during table-of-contents detection.
```

### PageIndex QA Adapter

Implemented in:

```text
pipelines/pageindex/qa_adapter.py
```

Current mode:

```text
tree_node_selection + optional LLM answer generation
```

The adapter can select candidate PageIndex tree nodes for a question and either output selected citations with `--no-llm` or call an LLM through LiteLLM when a model and provider key are available.

## Next Stage 1 Work

The next work should convert this setup into actual benchmark execution:

1. Resume PageIndex indexing for the 3 failed MVP PDFs after the JSON-output issue is handled.
2. Add a question-answering retrieval step for PageIndex.
3. Implement Long-context baseline.
4. Implement Vector RAG + reranker baseline.
5. Generate the first benchmark report.

## Stage 1 Exit Criteria

Stage 1 is complete when:

- 12 FinanceBench MVP questions can be run through PageIndex.
- At least one baseline can run on the same questions.
- All methods produce `BenchmarkResult`.
- Evidence recall and citation precision are reported.
- A Markdown benchmark report is generated under `reports/`.

## Current Blocker

Model-backed PageIndex indexing and QA require a provider API key in the current shell, usable provider quota, and reliable JSON output.

The first 8 structures were generated across DashScope/Qwen and DeepSeek. Further indexing is currently blocked because DeepSeek V4 Pro did not always return parseable JSON for PageIndex prompts:

```text
KeyError: 'toc_detected'
KeyError: 'page_index_given_in_toc'
```

To continue, either harden PageIndex JSON parsing / prompts for DeepSeek output or use a model/provider that consistently returns the required JSON.
