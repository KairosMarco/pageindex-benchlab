# FinanceBench Subsets

Source:

- Dataset repository: https://github.com/patronus-ai/financebench
- Paper: https://arxiv.org/abs/2311.11944

This directory stores normalized FinanceBench question subsets for PageIndex BenchLab.

## Files

```text
mvp_questions.jsonl
expanded_questions_25.jsonl
expanded_questions_25_manifest.json
```

The subset contains 12 FinanceBench questions selected for first-stage RAG pipeline testing.

The expanded subset contains 25 questions. It preserves the original 12 MVP questions and adds 13 deterministic balanced selections from the open-source FinanceBench rows.

Selection goals:

- Include information extraction questions.
- Include numerical reasoning questions.
- Include logical reasoning questions.
- Include novel-generated questions.
- Keep each item tied to a single primary document.
- Preserve FinanceBench evidence pages.

## Page Indexing

FinanceBench evidence pages are zero-indexed. The normalized MVP rows store both:

```text
page_zero_indexed
page_one_indexed
```

PageIndex local tree outputs appear to use one-indexed page ranges, so evaluators should declare the citation page base explicitly.

## Regenerating

Download the two open-source FinanceBench JSONL files into this directory:

```text
financebench_open_source.jsonl
financebench_document_information.jsonl
```

Then run:

```powershell
python datasets\financebench\build_mvp_subset.py
python datasets\financebench\build_expanded_subset.py --target-count 25
```

The expanded builder balances `question_type`, reasoning labels, companies, and source documents without using gold evidence during retrieval.
