# PageIndex PR #333: JSON Resilience

PR:

```text
https://github.com/VectifyAI/PageIndex/pull/333
```

Title:

```text
fix: improve JSON extraction and TOC fallback handling
```

Status on 2026-06-22:

```text
Open; no maintainer comments or reviews yet.
```

## Purpose

Improve PageIndex robustness when LLM responses include noisy or incomplete JSON during TOC and page-index extraction.

## Scope

Changed upstream files:

```text
pageindex/utils.py
pageindex/page_index.py
tests/test_json_resilience.py
```

Local branch:

```text
D:\pageindex-upstream-pr
fix/json-response-resilience
1cf28e5 Improve JSON extraction and TOC fallback handling
```

## Problem Evidence

The patch addresses failure classes observed during local PageIndex indexing:

```text
KeyError: 'toc_detected'
KeyError: 'page_index_given_in_toc'
AttributeError: 'dict' object has no attribute 'extend'
TypeError: unsupported operand type(s) for +: 'int' and 'NoneType'
KeyError: 'physical_index'
```

## Implementation Summary

- Parse fenced JSON, embedded JSON, arrays with trailing text, and Python-style literals.
- Use safe defaults when TOC detector or completeness responses are missing expected fields.
- Normalize model-produced TOC JSON into `list[dict]`.
- Skip page-offset and page-number repair when required fields are missing.
- Return a low-confidence no-TOC structure instead of failing after fallback attempts.
- Add focused standard-library `unittest` coverage.

## Validation

Commands:

```powershell
D:\pageindex-demo\PageIndex\.venv\Scripts\python.exe -m unittest discover -s tests
D:\pageindex-demo\PageIndex\.venv\Scripts\python.exe -m py_compile pageindex\utils.py pageindex\page_index.py tests\test_json_resilience.py
```

Result:

```text
Ran 7 tests
OK
py_compile passed
```

## Review Strategy

If maintainers request a smaller patch, split into:

1. JSON parser robustness.
2. TOC fallback handling.
3. Tests.

Keep benchmark claims out of this PR unless maintainers ask for background.
