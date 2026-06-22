## Summary

This PR improves PageIndex robustness when LLM calls return JSON in common non-ideal formats or omit optional fields during TOC/page-index extraction.

It keeps the existing indexing flow unchanged, but adds safer parsing and fallback behavior for provider responses that include:

- fenced JSON blocks,
- explanatory text before JSON,
- arrays with trailing text,
- Python-style `None`, `True`, or `False`,
- missing JSON keys,
- object-shaped TOC output where list-shaped output is expected,
- missing page-offset or `physical_index` values.

## Why

While running PageIndex over a FinanceBench PDF subset, I saw indexing failures from model response shape issues such as:

```text
KeyError: 'toc_detected'
KeyError: 'page_index_given_in_toc'
AttributeError: 'dict' object has no attribute 'extend'
TypeError: unsupported operand type(s) for +: 'int' and 'NoneType'
KeyError: 'physical_index'
```

The failures were not specific to one document format; they came from LLM JSON formatting variance.

## Changes

- Make `extract_json()` tolerate fenced JSON, embedded JSON, arrays, trailing text, and Python-style literals.
- Use safe defaults for TOC detector/completeness checks when parsed JSON is missing or not a dict.
- Normalize TOC generation output to `list[dict]` before list operations.
- Skip offset/page repair when the model output is missing required fields.
- Return a low-confidence no-TOC structure instead of raising `Processing failed` after fallback attempts.
- Add focused `unittest` coverage for the JSON parser and TOC fallback helpers.

## Validation

```powershell
python -m unittest discover -s tests
python -m py_compile pageindex\utils.py pageindex\page_index.py tests\test_json_resilience.py
```

Local result:

```text
Ran 7 tests
OK
```

I also validated equivalent fixes in a local benchmark workspace:

```text
Expanded PageIndex structures: 24 / 24 source documents
Expanded PageIndex retrieval-only QA: 25 / 25 generated
Expanded LLM QA: 25 / 25 generated
```

The benchmark artifacts are available here:

https://github.com/KairosMarco/pageindex-benchlab
