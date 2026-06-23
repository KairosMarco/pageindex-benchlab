# Stage 1 Status

Date: 2026-06-23

## Summary

Stage 1 has produced a working benchmark workspace, expanded FinanceBench diagnostics, two open upstream PageIndex PRs, and a BookRAG-first adapter preparation path.

The active contributor is `KairosMarco`; there is no active collaborator split in this repository.

## Current Artifacts

| Area | Status | Primary files |
|---|---|---|
| Schema | Complete for current pipelines | `benchlab/schemas.py`, `docs/schema.md` |
| Dataset | MVP and expanded FinanceBench subsets exist | `datasets/financebench/mvp_questions.jsonl`, `datasets/financebench/expanded_questions_25.jsonl` |
| PageIndex | MVP and expanded runs complete | `pipelines/pageindex/`, `reports/pageindex/` |
| Long-context | MVP and expanded diagnostics complete | `pipelines/long_context/`, `reports/long_context_expanded_llm_diagnostics.md` |
| Vector RAG | MVP and expanded LlamaIndex diagnostics complete | `pipelines/llamaindex_vector_rag/`, `reports/llamaindex_expanded_llm_diagnostics.md` |
| Hybrid RAG | MVP and expanded LlamaIndex diagnostics complete | `pipelines/llamaindex_hybrid_rag/`, `reports/llamaindex_expanded_llm_diagnostics.md` |
| GraphRAG | Placeholder only | `pipelines/graphrag/` |
| HyperGraphRAG | Placeholder only | `pipelines/hypergraphrag/` |
| BookRAG | Priority external baseline; readiness, dataset bridge, config templates, and config-load smoke checks added | `pipelines/bookrag/`, `scripts/check_bookrag_readiness.py`, `scripts/build_bookrag_dataset.py`, `scripts/prepare_bookrag_config.py` |
| Upstream PRs | Two PageIndex PRs open | `docs/upstream-pr-overview.md` |

## Current Benchmark Snapshot

Expanded 25-question FinanceBench run:

| Method | Evidence recall | Citation precision | Answer accuracy | Avg tokens | Avg latency |
|---|---:|---:|---:|---:|---:|
| PageIndex | `1.000` | `0.347` | `0.920` | `2,882` | `4,840 ms` |
| LlamaIndex Vector RAG | `1.000` | `0.360` | `0.920` | `2,543` | `16,497 ms` |
| LlamaIndex Hybrid RAG | `1.000` | `0.360` | `0.880` | `2,553` | `16,846 ms` |
| Long-context LLM | `0.800` | `0.267` | `0.920` | `92,500` | `12,772 ms` |

Source:

```text
reports/expanded_cost_quality_summary.md
```

## PageIndex Findings

- PageIndex completed the expanded 25-question LLM run.
- PageIndex evidence recall was `1.000` with three cited pages per answer.
- PageIndex answer accuracy was `0.920`.
- The two remaining PageIndex answer issues were:
  - `fb_exp_019`: rounded USD-billion answer strictness;
  - `fb_exp_020`: capital-intensity reasoning.
- These failures were not evidence-page retrieval misses.

Source reports:

```text
reports/pageindex_expanded_llm_diagnostics.md
reports/pageindex/pageindex_answer_issue_analysis.md
reports/pageindex/pageindex_ranking_diagnostics.md
```

## Upstream Contribution Status

| PR | Status | Purpose |
|---|---|---|
| https://github.com/VectifyAI/PageIndex/pull/333 | Open | JSON extraction and TOC fallback robustness with tests |
| https://github.com/VectifyAI/PageIndex/pull/334 | Open | Windows PowerShell and LiteLLM provider quickstart docs |

Local upstream PR workspace:

```text
D:\pageindex-upstream-pr
```

Detailed PR records:

```text
docs/upstream-pr-overview.md
docs/pageindex-upstream-pr-handoff.md
docs/pageindex-docs-pr-handoff.md
```

Related docs:

```text
docs/baseline-diagnostics-summary.md
docs/README.md
reports/README.md
```

## Validation Records

PageIndex JSON resilience PR validation:

```text
Ran 7 tests
OK
py_compile passed
```

Docs PR validation:

```text
git diff --check passed
```

Benchmark artifact validation records are in:

```text
reports/stage1_validation_report.json
reports/expanded_retrieval_validation_report.json
reports/expanded_llm_validation_report.json
reports/expanded_pageindex_llm_validation_report.json
reports/expanded_long_context_validation_report.json
```

## Current Next Step

The next useful action is BookRAG-first execution while keeping the PageIndex PRs alive.

Recommended order:

1. Run a one-document BookRAG tree-index attempt and record exact output or blocker.
2. If indexing succeeds, run one BookRAG RAG inference and convert the answer to `BenchmarkResult`.
3. Run the existing evidence and answer evaluators on that one output before expanding to the 25-question subset.
4. Monitor PageIndex PR #333 and PR #334; if no response after several working days, leave a concise follow-up comment on PR #333.
5. If PageIndex maintainers request smaller scope, split PR #333 into parser, TOC fallback, and test-only PRs.
