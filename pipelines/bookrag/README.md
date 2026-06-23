# BookRAG Adapter

Target sources:

- https://github.com/sam234990/BookRAG
- https://arxiv.org/abs/2512.03413
- https://arxiv.org/pdf/2512.03413
- https://www.51cto.com/aigc/11012.html

Goal:

```text
PDF documents -> BookIndex tree + entity graph + tree-graph links -> agent-planned retrieval -> answer
```

## Status

BookRAG is the priority structural graph-tree baseline. It is not part of the committed benchmark result table yet because no schema-valid BookRAG answer has been produced and evaluated.

This repository intentionally does not add BookRAG's dependencies to the main `requirements.txt`. BookRAG has a heavier runtime profile than the current PageIndex/LlamaIndex baselines, including Python 3.12, MinerU, ChromaDB, spaCy, Torch, Ultralytics, and optional MinerU/SGLang parsing services. It should be installed and checked as an external method-specific environment.

Local readiness is recorded in:

```text
reports/bookrag/status.md
reports/bookrag/readiness.json
```

Current completed preparation:

```text
local BookRAG checkout exists at D:\bookrag-source
conda env gbc-rag created
BookRAG CLI smoke check passes
FinanceBench 25-question dataset bridge generated
BookRAG dataset and system config templates generated
BookRAG config-load smoke checks pass
```

## Why Add It

BookRAG is directly relevant to the PageIndex comparison because it extends the tree-first idea into a richer structure-aware index:

- PageIndex: document hierarchy and reasoning-based traversal.
- BookRAG: document hierarchy plus entity-relation graph plus mappings between entities and tree nodes.

In BenchLab, BookRAG should be used to test whether a graph-tree index improves evidence recall, citation precision, and answer quality on structured long-document QA, especially for cross-section and entity-centric questions.

## Integration Plan

### Phase 0: Readiness

Check whether a local BookRAG checkout and environment are present:

```powershell
python scripts\check_bookrag_readiness.py --bookrag-repo D:\bookrag-source
```

Expected output:

```text
reports/bookrag/readiness.json
```

### Phase 1: External Checkout

Keep BookRAG outside this repository:

```powershell
git clone https://github.com/sam234990/BookRAG D:\bookrag-source
```

Do not vendor BookRAG source code or generated BookIndex artifacts into BenchLab.

### Phase 2: Dataset Bridge

Convert BenchLab question files into BookRAG's expected dataset shape:

```json
[
  {
    "question": "...",
    "answer": "...",
    "doc_uuid": "...",
    "doc_path": "D:/pageindex-benchlab/datasets/raw/financebench/pdfs/..."
  }
]
```

The bridge must preserve:

- BenchLab `question_id`;
- source PDF path;
- gold answer;
- gold evidence pages;
- output path mapping back to BenchLab schemas.

Implemented:

```powershell
python scripts\build_bookrag_dataset.py --questions datasets\financebench\expanded_questions_25.jsonl --output datasets\bookrag\financebench_expanded_25.json --mapping datasets\bookrag\financebench_expanded_25_mapping.json
```

Outputs:

```text
datasets/bookrag/financebench_expanded_25.json
datasets/bookrag/financebench_expanded_25_mapping.json
```

Prepare BookRAG YAML configs:

```powershell
python scripts\prepare_bookrag_config.py
```

Outputs:

```text
reports/bookrag/config/financebench_expanded_25.yaml
reports/bookrag/config/financebench_gbc_template.yaml
```

The system config is a template. It defaults to MinerU's local `pipeline` backend so the first tree-index attempt does not require a running SGLang service. Replace all model endpoint `TODO_*` values before running BookRAG. If you want the upstream VLM/SGLang parsing path, set `mineru.backend` to `vlm-sglang-client` and provide a real `mineru.server_url`.

### Phase 3: Offline Index Construction

Run BookRAG's index construction against the same FinanceBench PDFs used by PageIndex and LlamaIndex baselines.

Environment:

```powershell
conda activate gbc-rag
```

Smoke check:

```powershell
python D:\bookrag-source\main.py --help
```

Record:

- parsing status;
- index construction status;
- index build latency;
- generated index path;
- failures caused by missing MinerU/SGLang service or document parsing.

### Phase 4: Online Retrieval And Answering

Run BookRAG answer generation with the same answer model and citation budget policy used by other methods where possible.

Map BookRAG output into `benchlab.schemas.BenchmarkResult`:

```text
answer -> BenchmarkResult.answer
evidence pages -> BenchmarkResult.citations
retrieval plan/operators -> BenchmarkResult.retrieval_trace
runtime/model details -> BenchmarkResult.metadata
```

### Phase 5: Evaluation

Use the existing BenchLab evaluators:

```powershell
python scripts\evaluate_evidence_mvp.py --questions datasets\financebench\expanded_questions_25.jsonl --results-dir reports\bookrag\qa_expanded_25 --output reports\bookrag\evidence_eval_qa_expanded_25.json --continue-on-error
python scripts\evaluate_answers_mvp.py --questions datasets\financebench\expanded_questions_25.jsonl --results-dir reports\bookrag\qa_expanded_25 --output reports\bookrag\answer_eval_qa_expanded_25.json --mode llm --model deepseek/deepseek-v4-pro --continue-on-error
```

## Comparison Discipline

BookRAG should not be treated as "PageIndex replacement" by default. The benchmark should compare:

- retrieval accuracy;
- answer accuracy;
- citation precision;
- setup complexity;
- index build cost;
- runtime latency;
- required services and hardware;
- traceability of retrieved evidence.

The central question is:

> Does BookRAG's graph-tree BookIndex produce better long-document QA results than PageIndex's tree-only index under the same dataset, answer model, and evaluation policy?
