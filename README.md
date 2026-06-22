# PageIndex BenchLab

PageIndex BenchLab is a reproducible benchmark and upstream-contribution workspace for evaluating **PageIndex** against long-context LLMs and RAG baselines on structured long-document question answering.

The current work has been executed independently by `KairosMarco`. The repository now focuses on two outcomes:

- evidence-backed comparison of PageIndex, long-context LLM, Vector RAG, and Hybrid RAG on FinanceBench-style documents;
- small, reviewable upstream contributions to `VectifyAI/PageIndex`.

## Project Question

PageIndex should not be judged by a broad claim such as "better than all RAG." This project uses a narrower question:

> On structured long documents such as SEC filings, annual reports, contracts, and technical manuals, can PageIndex retrieve better evidence, produce usable citations, and provide a more explainable retrieval path than other RAG methods?

The benchmark tracks:

- `answer_accuracy`
- `evidence_recall`
- `citation_precision`
- `unsupported_claim_rate`
- `retrieval_explainability`
- `token_cost`
- `latency`
- `indexing_cost`

## Compared Methods

| Method | Role | Source |
|---|---|---|
| PageIndex | Main method under evaluation | https://github.com/VectifyAI/PageIndex |
| Long-context LLM | Strong baseline that puts the document into model context | https://platform.openai.com/docs/api-reference/responses/create |
| Vector RAG + reranker | Traditional semantic retrieval baseline | https://github.com/run-llama/llama_index |
| Hybrid RAG | BM25 + vector retrieval + rerank baseline | https://docs.llamaindex.ai/ |
| GraphRAG | Planned graph-based baseline | https://github.com/microsoft/graphrag |
| HyperGraphRAG | Planned hypergraph baseline | https://github.com/LHRLAB/HyperGraphRAG |

## Current Status

Status: **Stage 1 - expanded FinanceBench diagnostics and upstream contribution tracking**.

The repository has progressed beyond the initial MVP setup. It now contains:

- unified benchmark schema in `benchlab/schemas.py`;
- FinanceBench MVP and expanded 25-question subsets;
- PageIndex, Long-context, Vector RAG, and Hybrid RAG pipelines;
- evidence-page and LLM-judge answer evaluators;
- generated reports for retrieval quality, answer quality, token cost, latency, and failure analysis;
- two open upstream PageIndex PRs.

## Upstream Contributions

Two PageIndex upstream PRs have been opened from this work.

| PR | Type | Status | Purpose |
|---|---|---|---|
| https://github.com/VectifyAI/PageIndex/pull/333 | Code + tests | Open | Improve JSON extraction and conservative TOC fallback handling for noisy LLM responses |
| https://github.com/VectifyAI/PageIndex/pull/334 | Documentation | Open | Document Windows PowerShell virtualenv setup and LiteLLM provider configuration |

Local PageIndex PR workspace:

```text
D:\pageindex-upstream-pr
```

PR handoff documents:

- [PageIndex JSON resilience PR handoff](docs/pageindex-upstream-pr-handoff.md)
- [PageIndex docs PR handoff](docs/pageindex-docs-pr-handoff.md)
- [Contributor action plan](docs/contributor-action-plan.md)

## Expanded 25-Question Results

The current expanded comparison uses a 25-question FinanceBench subset over structured financial documents.

| Method | Evidence recall | Citation precision | Answer accuracy | Avg total tokens | Avg latency |
|---|---:|---:|---:|---:|---:|
| PageIndex | `1.000` | `0.347` | `0.920` | `2,882` | `4,840 ms` |
| LlamaIndex Vector RAG | `1.000` | `0.360` | `0.920` | `2,543` | `16,497 ms` |
| LlamaIndex Hybrid RAG | `1.000` | `0.360` | `0.880` | `2,553` | `16,846 ms` |
| Long-context LLM | `0.800` | `0.267` | `0.920` | `92,500` | `12,772 ms` |

Interpretation:

- PageIndex matched LlamaIndex Vector answer accuracy on this subset while using far fewer tokens than the long-context baseline.
- PageIndex retrieval found the gold evidence pages for all 25 questions in the expanded retrieval run.
- Remaining PageIndex answer issues were not retrieval misses; they were answer-generation or judge-policy issues around rounding and finance-definition reasoning.
- These are scoped benchmark results, not a universal claim that one method is always better.

Key reports:

- [Expanded cost/quality summary](reports/expanded_cost_quality_summary.md)
- [PageIndex expanded LLM diagnostics](reports/pageindex_expanded_llm_diagnostics.md)
- [PageIndex expanded retrieval summary](reports/pageindex/expanded_partial_summary.md)
- [PageIndex ranking diagnostics](reports/pageindex/pageindex_ranking_diagnostics.md)
- [PageIndex answer issue analysis](reports/pageindex/pageindex_answer_issue_analysis.md)
- [Finance prompt variant summary](reports/finance_prompt_variant_summary.md)
- [Stage 1 detailed evidence report](reports/stage1_detailed_evidence_report.md)
- [Per-question result CSV](reports/stage1_per_question_results.csv)

## Reproduce The Core Workflow

Create a Python environment:

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

Download FinanceBench MVP PDFs:

```powershell
python scripts\download_mvp_pdfs.py
```

Run PageIndex MVP indexing after setting a provider key:

```powershell
$env:DEEPSEEK_API_KEY="YOUR_KEY"
python scripts\run_pageindex_mvp.py
```

Run major diagnostics from the existing scripts:

```powershell
python scripts\run_pageindex_qa_mvp.py
python scripts\run_long_context_mvp.py
python scripts\run_vector_rag_mvp.py
python scripts\run_hybrid_rag_mvp.py
```

Detailed run commands and historical notes are kept in:

- [Stage 1 status](docs/stage-1-status.md)
- [Scripts README](scripts/README.md)
- [PageIndex pipeline README](pipelines/pageindex/README.md)
- [Long-context pipeline README](pipelines/long_context/README.md)
- [Vector RAG pipeline README](pipelines/vector_rag/README.md)
- [Hybrid RAG pipeline README](pipelines/hybrid_rag/README.md)

## Output Schema

Each pipeline should produce the same JSON-compatible result shape. The canonical models are in `benchlab/schemas.py`.

```json
{
  "method": "pageindex",
  "question_id": "q001",
  "question": "What was the company's operating income in 2023?",
  "answer": "...",
  "citations": [
    {
      "document_id": "example_10k",
      "page": 42,
      "section": "Item 7",
      "text": "..."
    }
  ],
  "retrieval_trace": [
    {
      "step": 1,
      "action": "inspect_tree",
      "target": "Item 7"
    }
  ],
  "token_usage": {
    "input": 12000,
    "output": 800
  },
  "latency_ms": 8400
}
```

Schema documentation:

- [Benchmark schema](docs/schema.md)

## Repository Structure

```text
pageindex-benchlab/
  benchlab/              shared schema and helpers
  datasets/              FinanceBench subsets and dataset notes
  docs/                  status, contribution, and source documents
  evaluators/            evidence and answer evaluators
  examples/              demo outputs
  pipelines/             PageIndex, long-context, vector, hybrid, graph placeholders
  reports/               generated benchmark reports and raw outputs
  scripts/               runnable benchmark and reporting commands
  tests/                 local tests
```

## Hardware Requirements

The current benchmark does **not** require a local GPU.

Recommended setup:

- Python 3.10+
- Git
- 16 GB RAM preferred
- an LLM provider API key for answer generation and judging

A GPU may become useful later for local LLMs, local embeddings, or local rerankers, but it is not required for the current PageIndex contribution workflow.

## Current Next Actions

1. Monitor PageIndex PR #333 and respond to maintainer feedback.
2. Monitor PageIndex PR #334 and adjust wording if maintainers request changes.
3. If #333 is considered too broad, split it into smaller PRs:
   - JSON parser robustness;
   - TOC fallback handling;
   - tests.
4. Open a separate PageIndex issue or discussion for benchmark/ranking diagnostics after maintainers have had time to review the code PR.
5. Continue benchmark work only when it supports a concrete upstream contribution or a clearly scoped report.

## Contribution Principles

- Keep upstream PRs small and reviewable.
- Do not include API keys, private PDFs, or generated raw outputs in upstream PRs.
- Do not make broad superiority claims without scoped evidence.
- Separate code fixes, documentation fixes, and benchmark discussion into different PRs or issues.
- Treat benchmark results as evidence for hypotheses, not marketing claims.
