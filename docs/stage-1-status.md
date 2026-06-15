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

## Next Stage 1 Work

The next work should convert this setup into actual benchmark execution:

1. Download PDFs for the 12 MVP questions.
2. Run PageIndex indexing on those PDFs.
3. Add a question-answering retrieval step for PageIndex.
4. Implement Long-context baseline.
5. Implement Vector RAG + reranker baseline.
6. Generate the first benchmark report.

## Stage 1 Exit Criteria

Stage 1 is complete when:

- 12 FinanceBench MVP questions can be run through PageIndex.
- At least one baseline can run on the same questions.
- All methods produce `BenchmarkResult`.
- Evidence recall and citation precision are reported.
- A Markdown benchmark report is generated under `reports/`.

