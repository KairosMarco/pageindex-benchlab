# FinanceBench MVP Subset

Source:

- Dataset repository: https://github.com/patronus-ai/financebench
- Paper: https://arxiv.org/abs/2311.11944

This directory stores the first small question subset for the PageIndex BenchLab MVP.

## Files

```text
mvp_questions.jsonl
```

The subset contains 12 FinanceBench questions selected for first-stage RAG pipeline testing.

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
```

