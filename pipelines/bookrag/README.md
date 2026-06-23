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

BookRAG is a planned structural graph-tree baseline. It is not part of the committed benchmark result table yet.

This repository intentionally does not add BookRAG's dependencies to the main `requirements.txt`. BookRAG has a heavier runtime profile than the current PageIndex/LlamaIndex baselines, including Python 3.12, MinerU, ChromaDB, spaCy, Torch, Ultralytics, and a MinerU/SGLang parsing service in the default setup. It should be installed and checked as an external method-specific environment.

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

### Phase 3: Offline Index Construction

Run BookRAG's index construction against the same FinanceBench PDFs used by PageIndex and LlamaIndex baselines.

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
