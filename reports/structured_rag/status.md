# Structured Tree-Graph RAG Status

Date: 2026-06-26

## Purpose

This is BenchLab's independently implemented minimal structural RAG baseline. It is inspired by the same research direction as BookRAG, but it does not copy or vendor BookRAG code.

The adapter tests whether simple document tree nodes, entity co-occurrence links, and entity-to-node mappings can improve page-level evidence retrieval before full BookRAG indexing is available.

## Implementation

```text
pipelines/structured_rag/adapter.py
scripts/run_structured_rag_mvp.py
tests/test_structured_rag_adapter.py
```

Core flow:

```text
PDF pages -> heading-aware tree nodes -> lightweight entity graph -> tree-node ranking -> BenchmarkResult
```

## MVP Smoke Result

Command:

```powershell
python scripts\run_structured_rag_mvp.py --force --continue-on-error
python scripts\evaluate_evidence_mvp.py --results-dir reports\structured_rag\qa_smoke --output reports\structured_rag\evidence_eval_smoke.json --continue-on-error
```

Result:

```text
Generated outputs: 12 / 12
Evidence evaluation result_count: 12
Failure count: 0
Average evidence recall: 0.667
Average citation precision: 0.222
```

Artifacts:

```text
reports/structured_rag/qa_smoke/
reports/structured_rag/qa_smoke_manifest.json
reports/structured_rag/evidence_eval_smoke.json
```

## Expanded 25-Question Result

Command:

```powershell
python scripts\run_structured_rag_mvp.py --questions datasets\financebench\expanded_questions_25.jsonl --output-dir reports\structured_rag\qa_expanded_25 --manifest reports\structured_rag\qa_expanded_25_manifest.json --force --continue-on-error
python scripts\evaluate_evidence_mvp.py --questions datasets\financebench\expanded_questions_25.jsonl --results-dir reports\structured_rag\qa_expanded_25 --output reports\structured_rag\evidence_eval_qa_expanded_25.json --continue-on-error
python scripts\summarize_structured_rag.py
```

Result:

```text
Generated outputs: 25 / 25
Evidence evaluation result_count: 25
Failure count: 0
Average evidence recall: 0.600
Average citation precision: 0.207
Full hits: 15
Misses: 10
Median latency: 264 ms
```

Artifacts:

```text
reports/structured_rag/qa_expanded_25/
reports/structured_rag/qa_expanded_25_manifest.json
reports/structured_rag/evidence_eval_qa_expanded_25.json
reports/structured_rag/expanded_diagnostics.md
reports/structured_rag/expanded_diagnostics.json
```

## Interpretation

This baseline is not competitive with the current PageIndex expanded result. Its value is different:

- it proves BenchLab can evaluate a local tree-plus-graph retrieval method;
- it creates a controllable implementation surface for structural retrieval experiments;
- it provides a license-safe path while BookRAG remains an external dependency with unclear repository license status;
- it gives concrete failure cases for improving entity mapping, section detection, and ranking.

Expanded diagnostics show the current weak points clearly:

- table-heavy financial line-item questions often need better table-aware ranking;
- early-page earnings-release questions can be missed when generic business/summary language outranks the gold page;
- some misses are near misses where a neighboring page is selected, suggesting page-window expansion should be tested;
- citation precision is capped by the current three-page fallback policy, so ranking quality matters more than answer generation at this stage.

## Next Steps

1. Add table-aware node splitting and table phrase boosts.
2. Add an early-page guard for short earnings-release PDFs.
3. Test page-window expansion around high-scoring nodes.
4. Add an optional LLM answer-generation step after retrieval stabilizes.
5. Use failure cases to shape BookRAG and PageIndex upstream issues.
