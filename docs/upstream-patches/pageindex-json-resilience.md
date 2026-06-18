# PageIndex JSON Resilience Patch Notes

Date: 2026-06-15

## Context

DeepSeek V4 Pro can run PageIndex indexing, but it sometimes returns empty output or JSON wrapped in extra text. Before this patch, PageIndex could crash with direct dictionary lookups such as:

```text
KeyError: 'toc_detected'
KeyError: 'page_index_given_in_toc'
AttributeError: 'dict' object has no attribute 'extend'
TypeError: unsupported operand type(s) for +: 'int' and 'NoneType'
KeyError: 'physical_index'
```

This blocked indexing for several FinanceBench MVP PDFs.

## Local Patch

Local PageIndex path:

```text
D:\pageindex-demo\PageIndex
```

Files changed locally:

```text
pageindex/utils.py
pageindex/page_index.py
```

Changes:

- Improved `extract_json()` to parse fenced JSON, JSON embedded in explanatory text, JSON arrays, Python-style `None` / `True` / `False`, and trailing text after the decoded object.
- Added conservative fallbacks for table-of-contents detector helpers when expected keys are missing.
- Avoided crashes in `single_toc_item_index_fixer()` when a model does not return `physical_index`.
- Normalized model-produced TOC JSON to lists before using list operations such as `.extend()`.
- Avoided page-offset addition when PageIndex detects a missing offset.
- Returned low-confidence no-TOC structures instead of raising after repeated verification failures.
- Left unresolved TOC items unresolved when a page-number repair response is empty or omits `physical_index`.

## Result

After the patch, the remaining PageIndex MVP indexing jobs completed with:

```text
Model: deepseek/deepseek-v4-pro
Generated: COSTCO_2021_10K, JPMORGAN_2023Q2_10Q, NIKE_2023_10K
Final status: 11 / 11 unique MVP PDFs indexed
Expanded status: 24 / 24 unique expanded PDFs indexed
Expanded retrieval-only QA: 25 / 25 questions generated
Expanded retrieval-only evidence recall: 0.760
Expanded retrieval-only citation precision: 0.253
Expanded LLM QA: 25 / 25 answers generated
Expanded LLM answer accuracy: 0.760
```

## Upstream Contribution Candidate

This is a good PageIndex PR candidate because it is provider-agnostic. It improves robustness for any model that occasionally adds text around JSON or returns incomplete JSON fields.

Suggested upstream PR title:

```text
Improve JSON extraction and fallback handling for LLM responses
```

Suggested tests:

- `extract_json()` parses fenced JSON.
- `extract_json()` parses JSON embedded after explanatory text.
- `extract_json()` parses arrays embedded in text.
- `extract_json()` handles Python-style `None`, `True`, and `False`.
- TOC helper functions return safe defaults instead of raising `KeyError` on missing fields.
- Page-offset helpers tolerate missing offsets without raising `TypeError`.
- No-TOC processing returns low-confidence structures instead of raising when verification does not meet threshold.
- Page-number repair helpers skip unresolved items when `physical_index` is absent.
