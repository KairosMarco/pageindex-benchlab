# Structured Tree-Graph RAG Adapter

This adapter is an independently implemented BenchLab baseline inspired by the same structural direction that makes BookRAG important:

```text
PDF pages -> document tree nodes -> lightweight entity graph -> entity-to-node mapping -> ranked evidence pages
```

It does not vendor or copy BookRAG source code. It exists so BenchLab has a controllable baseline for testing the value of:

- document hierarchy;
- entity co-occurrence links;
- explicit mappings from entities back to tree nodes;
- page-level evidence output compatible with existing BenchLab evaluators.

## Role

BookRAG remains the serious external graph-tree baseline. This adapter is the local minimal implementation used to:

- validate the benchmark harness before full BookRAG indexing succeeds;
- produce schema-valid `BenchmarkResult` outputs without external services;
- generate concrete experiments that can guide upstream issues and PRs.

## Run

```powershell
python scripts\run_structured_rag_mvp.py --force --continue-on-error
python scripts\evaluate_evidence_mvp.py --results-dir reports\structured_rag\qa_smoke --output reports\structured_rag\evidence_eval_smoke.json --continue-on-error
```

Expanded 25-question subset:

```powershell
python scripts\run_structured_rag_mvp.py --questions datasets\financebench\expanded_questions_25.jsonl --output-dir reports\structured_rag\qa_expanded_25 --manifest reports\structured_rag\qa_expanded_25_manifest.json --force --continue-on-error
python scripts\evaluate_evidence_mvp.py --questions datasets\financebench\expanded_questions_25.jsonl --results-dir reports\structured_rag\qa_expanded_25 --output reports\structured_rag\evidence_eval_qa_expanded_25.json --continue-on-error
```

## Limits

This is not a BookRAG replacement. It uses deterministic heuristics and no LLM answer generation. Its value is controlled measurement of structural retrieval signals before spending model/runtime budget on full BookRAG.
