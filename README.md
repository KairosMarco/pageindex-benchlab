# PageIndex BenchLab

PageIndex BenchLab is a reproducible benchmark and contribution workspace for testing **PageIndex**, **BookRAG**, long-context LLMs, and RAG baselines on structured long-document QA.

The current work was executed independently by `KairosMarco`. The repository has two concrete purposes:

- compare retrieval and answer quality on FinanceBench-style documents;
- turn benchmark findings into small upstream contributions, starting with `VectifyAI/PageIndex` and then BookRAG-related adapter/report work where licensing permits.

## Current State

| Area | Status |
|---|---|
| Benchmark scope | 25-question FinanceBench expanded subset |
| Implemented methods | PageIndex, Long-context LLM, LlamaIndex Vector RAG, LlamaIndex Hybrid RAG |
| BookRAG status | External checkout, conda environment, dataset bridge, config templates, and config-load smoke checks are complete; first index/RAG run is still pending |
| Planned methods | GraphRAG, HyperGraphRAG |
| Main reports | `reports/expanded_cost_quality_summary.md`, `reports/pageindex_expanded_llm_diagnostics.md` |
| Upstream PRs | PageIndex PR #333 and PR #334 are open |

Open upstream PRs:

- [PR #333: fix: improve JSON extraction and TOC fallback handling](https://github.com/VectifyAI/PageIndex/pull/333)
- [PR #334: docs: document Windows and LiteLLM provider setup](https://github.com/VectifyAI/PageIndex/pull/334)

## Benchmark Question

The project does not try to prove that PageIndex is universally better than RAG. It asks a narrower question:

> On structured long documents such as SEC filings, can PageIndex retrieve the right evidence pages, cite them clearly, and answer with competitive cost and latency?

Tracked metrics:

- `evidence_recall`
- `citation_precision`
- `answer_accuracy`
- `token_cost`
- `latency`
- `retrieval_explainability`

## Compared Methods

| Method | Role | Source |
|---|---|---|
| PageIndex | Main method under evaluation | https://github.com/VectifyAI/PageIndex |
| Long-context LLM | Full-document context baseline | https://platform.openai.com/docs/api-reference/responses/create |
| LlamaIndex Vector RAG | Semantic retrieval baseline | https://github.com/run-llama/llama_index |
| LlamaIndex Hybrid RAG | BM25 + vector retrieval baseline | https://docs.llamaindex.ai/ |
| GraphRAG | Planned graph baseline | https://github.com/microsoft/graphrag |
| HyperGraphRAG | Planned hypergraph baseline | https://github.com/LHRLAB/HyperGraphRAG |
| BookRAG | Priority structural graph-tree baseline; adapter preparation in progress | https://github.com/sam234990/BookRAG |

## Key Result Snapshot

Expanded 25-question FinanceBench run:

| Method | Evidence recall | Citation precision | Answer accuracy | Avg tokens | Avg latency |
|---|---:|---:|---:|---:|---:|
| PageIndex | `1.000` | `0.347` | `0.920` | `2,882` | `4,840 ms` |
| LlamaIndex Vector RAG | `1.000` | `0.360` | `0.920` | `2,543` | `16,497 ms` |
| LlamaIndex Hybrid RAG | `1.000` | `0.360` | `0.880` | `2,553` | `16,846 ms` |
| Long-context LLM | `0.800` | `0.267` | `0.920` | `92,500` | `12,772 ms` |

Conservative reading:

- PageIndex is competitive on this small finance subset.
- PageIndex retrieved all gold evidence pages in the expanded PageIndex run.
- Remaining PageIndex misses were answer-generation or judge-strictness cases, not evidence retrieval failures.
- The result supports scoped follow-up work, not broad superiority claims.

## Important Reports

- [Expanded cost/quality summary](reports/expanded_cost_quality_summary.md)
- [PageIndex expanded LLM diagnostics](reports/pageindex_expanded_llm_diagnostics.md)
- [PageIndex retrieval summary](reports/pageindex/expanded_partial_summary.md)
- [PageIndex ranking diagnostics](reports/pageindex/pageindex_ranking_diagnostics.md)
- [PageIndex answer issue analysis](reports/pageindex/pageindex_answer_issue_analysis.md)
- [Finance prompt variant summary](reports/finance_prompt_variant_summary.md)
- [Stage 1 status](docs/stage-1-status.md)
- [Baseline diagnostics summary](docs/baseline-diagnostics-summary.md)
- [BookRAG integration plan](docs/bookrag-integration-plan.md)
- [BookRAG status](reports/bookrag/status.md)
- [Upstream PR overview](docs/upstream-pr-overview.md)
- [PageIndex PR pattern review](docs/pageindex-pr-pattern-review.md)
- [Docs index](docs/README.md)

## Reproduce Core Workflow

Set up Python:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If PowerShell blocks virtualenv activation:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
.\.venv\Scripts\Activate.ps1
```

Download MVP PDFs:

```powershell
python scripts\download_mvp_pdfs.py
```

Run core baselines after setting a provider key:

```powershell
$env:DEEPSEEK_API_KEY="YOUR_KEY"
python scripts\run_pageindex_mvp.py
python scripts\run_pageindex_qa_mvp.py
python scripts\run_long_context_mvp.py
python scripts\run_vector_rag_mvp.py
python scripts\run_hybrid_rag_mvp.py
```

More run details:

- [Scripts README](scripts/README.md)
- [PageIndex pipeline README](pipelines/pageindex/README.md)
- [Long-context pipeline README](pipelines/long_context/README.md)
- [Vector RAG pipeline README](pipelines/vector_rag/README.md)
- [Hybrid RAG pipeline README](pipelines/hybrid_rag/README.md)
- [BookRAG pipeline README](pipelines/bookrag/README.md)

## Repository Structure

```text
benchlab/     shared schema and helpers
datasets/     FinanceBench subsets and dataset notes
docs/         status, contribution, and source documents
evaluators/   evidence and answer evaluators
examples/     demo outputs
pipelines/    benchmark method adapters
reports/      generated reports and raw outputs
scripts/      runnable benchmark commands
tests/        local tests
```

## Next Actions

1. Run the first BookRAG one-document tree-index attempt and record the exact blocker or output.
2. Convert the first BookRAG answer into `BenchmarkResult` once RAG inference succeeds.
3. Evaluate that output with the existing evidence and answer evaluators before adding BookRAG to the result table.
4. Monitor PageIndex PR #333 and PR #334, then respond or split scope if maintainers request changes.
5. Continue benchmark work only when it supports a concrete upstream contribution or a scoped report.

## Contribution Rules

- Keep upstream PRs small and reviewable.
- Keep benchmark claims scoped to the data.
- Do not commit API keys, private PDFs, or generated credentials.
- Separate code fixes, documentation fixes, and benchmark discussion.
