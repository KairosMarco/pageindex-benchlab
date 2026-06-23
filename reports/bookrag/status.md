# BookRAG Status

Date: 2026-06-23

## Summary

BookRAG is now tracked as a planned external graph-tree baseline in PageIndex BenchLab.

Current local status:

| Item | Status |
|---|---|
| BookRAG source | Available at `D:\bookrag-source` |
| BookRAG environment | `conda` env `gbc-rag` created |
| Python version | `3.12.13` in `gbc-rag` |
| Dependency readiness | Passed |
| Import readiness | Passed |
| CLI smoke | `python D:\bookrag-source\main.py --help` starts successfully |
| BenchLab dataset bridge | Generated for expanded 25-question FinanceBench subset |
| BookRAG system config | Template generated, not runnable until `TODO_*` values are replaced |
| Actual BookRAG index/RAG run | Not started |

## Generated BenchLab Artifacts

```text
datasets/bookrag/financebench_expanded_25.json
datasets/bookrag/financebench_expanded_25_mapping.json
reports/bookrag/readiness.json
reports/bookrag/config/financebench_expanded_25.yaml
reports/bookrag/config/financebench_gbc_template.yaml
```

## Readiness Result

The latest readiness report says:

```text
repo_exists=True
python_version_ok=True
ready_for_adapter_work=True
```

This means adapter work can continue. It does not mean BookRAG has produced benchmark answers yet.

## VLDB 2026 Value

BookRAG's README states that the paper has been accepted to VLDB 2026.

VLDB is a top-tier database and data-management research venue. For this project, the acceptance is meaningful because it signals that BookRAG is not just a GitHub demo or blog concept; it is attached to peer-reviewed systems/data-management research.

Reference points:

- VLDB 2026 official site: https://vldb.org/2026/
- VLDB Endowment conference page: https://www.vldb.org/conference.html
- CORE ranking entry for VLDB: https://portal.core.edu.au/conf-ranks/1261/

Practical interpretation:

- High research credibility for structured-document indexing and retrieval.
- Strong reason to include BookRAG as a serious baseline.
- Not proof that BookRAG is easier to run, production-ready, or better on FinanceBench.
- Not a reason to abandon PageIndex contribution work.

## Why It Matters For PageIndex BenchLab

BookRAG directly tests the next question after PageIndex:

> Is a tree-only structure enough, or does adding entity graph relations and tree-graph mappings improve long-document QA enough to justify the extra runtime and setup cost?

This makes BookRAG more strategically relevant than a generic graph baseline.

## Current Blockers Before Running BookRAG

The environment is installed, but real indexing/RAG still needs method-specific runtime configuration:

- valid `mineru.server_url` for MinerU/SGLang client parsing;
- LLM endpoint and model for tree/graph construction;
- VLM endpoint and model if visual parsing is required;
- embedding endpoint/model;
- reranker endpoint/model;
- decision on CPU vs GPU runtime for local components;
- reviewed BookRAG license position before redistributing modified code or generated artifacts.

The generated system config is intentionally a template:

```text
reports/bookrag/config/financebench_gbc_template.yaml
```

It contains `TODO_*` placeholders and no real API keys.

## Next Engineering Steps

1. Create a local, non-committed runnable config from `financebench_gbc_template.yaml`.
2. Decide whether to use external OpenAI-compatible endpoints or local models for LLM/embedding/reranker.
3. Configure MinerU/SGLang service or choose an alternative MinerU backend.
4. Run one-document indexing on `3M_2018_10K.pdf`.
5. Map one BookRAG answer into `BenchmarkResult`.
6. Run BenchLab evidence evaluation on that single output.

Promotion rule:

BookRAG should stay out of the main comparison table until at least one schema-valid answer output is generated and evaluated.
