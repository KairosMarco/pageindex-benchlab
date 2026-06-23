# Structured Tree-Graph RAG Status

Date: 2026-06-23

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

## Interpretation

This baseline is not competitive with the current PageIndex expanded result. Its value is different:

- it proves BenchLab can evaluate a local tree-plus-graph retrieval method;
- it creates a controllable implementation surface for structural retrieval experiments;
- it provides a license-safe path while BookRAG remains an external dependency with unclear repository license status;
- it gives concrete failure cases for improving entity mapping, section detection, and ranking.

## Next Steps

1. Add expanded 25-question retrieval results.
2. Add better section heading detection for SEC filings.
3. Add table-aware node splitting.
4. Add an optional LLM answer-generation step after retrieval stabilizes.
5. Use failure cases to shape BookRAG and PageIndex upstream issues.
