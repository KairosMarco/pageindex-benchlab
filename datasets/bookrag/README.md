# BookRAG Dataset Bridges

This directory stores small dataset bridge files that adapt BenchLab question sets to the input shape expected by BookRAG.

Generated files:

- `financebench_expanded_25.json`: BookRAG-shaped records with `question`, `answer`, `doc_uuid`, and `doc_path`.
- `financebench_expanded_25_mapping.json`: BenchLab sidecar mapping with `question_id`, document metadata, and gold evidence pages.

Regenerate:

```powershell
python scripts\build_bookrag_dataset.py --questions datasets\financebench\expanded_questions_25.jsonl --output datasets\bookrag\financebench_expanded_25.json --mapping datasets\bookrag\financebench_expanded_25_mapping.json
```

The generated JSON does not contain private data or API keys. The `doc_path` values point to local PDFs under `datasets/raw/financebench/pdfs/`; that raw PDF directory is intentionally not committed.
