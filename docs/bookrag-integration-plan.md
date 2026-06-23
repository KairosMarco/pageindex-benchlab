# BookRAG Integration Plan

Date: 2026-06-23

## Purpose

BookRAG is added to PageIndex BenchLab as a planned structural graph-tree baseline.

The goal is not to replace PageIndex in the benchmark. The goal is to test whether BookRAG's richer `BookIndex` design improves retrieval and answer quality on the same long-document QA tasks already used for PageIndex, Long-context LLM, Vector RAG, and Hybrid RAG.

## Sources

| Source | URL |
|---|---|
| BookRAG repository | https://github.com/sam234990/BookRAG |
| BookRAG arXiv abstract | https://arxiv.org/abs/2512.03413 |
| BookRAG PDF | https://arxiv.org/pdf/2512.03413 |
| Secondary article | https://www.51cto.com/aigc/11012.html |
| VLDB 2026 official site | https://vldb.org/2026/ |
| VLDB Endowment conference page | https://www.vldb.org/conference.html |
| CORE ranking entry for VLDB | https://portal.core.edu.au/conf-ranks/1261/ |
| PageIndex repository | https://github.com/VectifyAI/PageIndex |

## Technical Positioning

| Method | Index structure | Retrieval style | BenchLab role |
|---|---|---|---|
| PageIndex | Hierarchical document tree | Reasoning-based tree traversal | Main method under evaluation |
| BookRAG | Document tree + entity graph + tree-graph mappings | Agent-planned retrieval over BookIndex | Planned structural graph-tree baseline |
| GraphRAG | Entity and relationship graph | Graph community/entity retrieval | Planned graph baseline |
| HyperGraphRAG | Hypergraph | N-ary relation retrieval | Planned hypergraph baseline |
| Long-context LLM | No persistent index | Full-context prompting | Cost and context baseline |

## Why BookRAG Matters

BookRAG narrows PageIndex's research novelty space because it keeps the document hierarchy idea but adds graph relations and explicit mappings between graph entities and tree nodes.

This makes it a strong candidate baseline for questions that require:

- cross-section evidence;
- entity-centric reasoning;
- table-to-text connections;
- local detail plus global document structure;
- multi-hop relationships across a long document.

## Integration Constraints

BookRAG should be treated as a heavy external dependency, not as a normal BenchLab package dependency.

Known setup constraints from the current BookRAG README and requirements:

- Python 3.12 environment is recommended.
- MinerU is used for PDF parsing.
- Default parsing expects a MinerU/SGLang service through `vlm-sglang-client`.
- The dependency set includes ChromaDB, spaCy, Torch, TorchVision, Ultralytics, and layout/document parsing packages.
- The repository currently has no detected license in GitHub metadata, so reuse and redistribution need caution until clarified.

## Implementation Phases

### Phase 0: Readiness Check

Added in this repository:

```text
scripts/check_bookrag_readiness.py
pipelines/bookrag/README.md
```

Run:

```powershell
python scripts\check_bookrag_readiness.py --bookrag-repo D:\bookrag-source
```

This produces:

```text
reports/bookrag/readiness.json
```

### Phase 1: Dataset Bridge

Create a conversion script from BenchLab JSONL questions to BookRAG's released dataset shape:

```json
[
  {
    "question": "...",
    "answer": "...",
    "doc_uuid": "...",
    "doc_path": "..."
  }
]
```

The bridge must preserve BenchLab `question_id` through metadata or sidecar mapping so BookRAG outputs can be evaluated by existing BenchLab scripts.

Implemented:

```text
scripts/build_bookrag_dataset.py
scripts/prepare_bookrag_config.py
datasets/bookrag/financebench_expanded_25.json
datasets/bookrag/financebench_expanded_25_mapping.json
reports/bookrag/config/financebench_expanded_25.yaml
reports/bookrag/config/financebench_gbc_template.yaml
```

The BookRAG dataset file uses only the upstream fields described in the BookRAG README: `question`, `answer`, `doc_uuid`, and `doc_path`. The BenchLab-specific fields are kept in the sidecar mapping file.

The generated system config is intentionally a template. It contains `TODO_*` placeholders for LLM, VLM, MinerU, embedding, and reranker endpoints. Do not commit real keys or private service URLs.

### Phase 2: Index Construction Adapter

Run BookRAG offline indexing on the same FinanceBench PDFs.

Record per document:

- parse status;
- index status;
- index path;
- build time;
- service/runtime error if any.

### Phase 3: Retrieval And QA Adapter

Map BookRAG answers to `BenchmarkResult`:

- `method`: `bookrag`;
- `answer`: generated answer;
- `citations`: page-level evidence if recoverable;
- `retrieval_trace`: query planning and retrieval operators if available;
- `metadata`: BookRAG config, model, index path, runtime details.

### Phase 4: Shared Evaluation

Use existing evaluators:

```powershell
python scripts\evaluate_evidence_mvp.py --questions datasets\financebench\expanded_questions_25.jsonl --results-dir reports\bookrag\qa_expanded_25 --output reports\bookrag\evidence_eval_qa_expanded_25.json --continue-on-error
python scripts\evaluate_answers_mvp.py --questions datasets\financebench\expanded_questions_25.jsonl --results-dir reports\bookrag\qa_expanded_25 --output reports\bookrag\answer_eval_qa_expanded_25.json --mode llm --model deepseek/deepseek-v4-pro --continue-on-error
```

## Success Criteria

BookRAG can be promoted from `planned` to `active` only after:

- a local BookRAG checkout passes readiness checks;
- at least one FinanceBench PDF is indexed;
- one BenchLab question produces a schema-valid `BenchmarkResult`;
- evidence evaluation runs against that output;
- setup limitations are documented in a report.

## Contributor Relevance

BookRAG strengthens BenchLab's independent value even if PageIndex PRs take time to review.

For PageIndex upstream contribution, BookRAG should be used as comparative context, not as a claim that PageIndex is obsolete. The useful framing is:

> PageIndex is a lightweight tree-only baseline. BookRAG is a heavier graph-tree baseline. BenchLab measures when the additional graph structure is worth the setup and runtime cost.
