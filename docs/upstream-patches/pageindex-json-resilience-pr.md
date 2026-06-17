# Upstream PageIndex PR Draft: JSON Response Resilience

Target repository:

```text
https://github.com/VectifyAI/PageIndex
```

Suggested PR title:

```text
Improve JSON extraction and fallback handling for LLM responses
```

## Summary

This PR improves PageIndex robustness when an LLM returns JSON wrapped in Markdown, explanatory text, Python-style literals, or incomplete fields.

The local benchmark run found that provider responses can occasionally produce:

```text
KeyError: 'toc_detected'
KeyError: 'page_index_given_in_toc'
```

or noisy JSON such as a fenced response containing `{"toc_detected": "yes"}`.

and:

```text
Here is the JSON:
{"toc_detected": "no"}
```

Before the patch, direct dictionary lookups could stop indexing. After the patch, the local PageIndex MVP indexing jobs completed for all 11 unique FinanceBench MVP PDFs.

## Motivation

PageIndex relies on model-generated JSON in several TOC and page-indexing helpers. Even strong models sometimes:

- wrap JSON in fenced Markdown blocks,
- add explanatory text before or after JSON,
- return arrays instead of objects,
- use Python-style `None`, `True`, or `False`,
- omit expected keys.

The change is provider-agnostic. It improves reliability for OpenAI-compatible providers, DashScope/Qwen, DeepSeek, and other LiteLLM-backed models.

## Local Validation

Local benchmark environment:

```text
OS: Windows
Python: 3.13.9
Model: deepseek/deepseek-v4-pro
Dataset: FinanceBench MVP subset
```

Result after the patch:

```text
PageIndex structures generated: 11 / 11 unique MVP PDFs
```

Local benchmark notes:

```text
docs/upstream-patches/pageindex-json-resilience.md
```

## Implementation Notes

Recommended implementation scope:

- Improve `extract_json()` so it can parse:
  - fenced JSON,
  - JSON embedded after explanatory text,
  - JSON arrays,
  - trailing text after the decoded JSON object,
  - Python-style `None`, `True`, and `False`.
- Make TOC helper functions use conservative defaults when expected fields are missing.
- Avoid crashing `single_toc_item_index_fixer()` when `physical_index` is missing or null.

Examples of safe fallbacks:

```python
json_content = extract_json(response)
if not isinstance(json_content, dict):
    return "no"
return json_content.get("toc_detected", "no")
```

and:

```python
if "physical_index" not in item or item["physical_index"] is None:
    return {
        "list_index": item.get("list_index"),
        "answer": "no",
        "title": title,
        "page_number": None,
    }
```

## Suggested Tests

Add focused tests for the JSON helper:

```text
extract_json parses fenced JSON.
extract_json parses JSON embedded after explanatory text.
extract_json parses arrays embedded in text.
extract_json handles Python-style None, True, and False.
extract_json tolerates trailing text after a valid object.
TOC helpers return safe defaults instead of raising KeyError on missing fields.
single_toc_item_index_fixer handles missing physical_index safely.
```

## Expected Impact

This should reduce indexing failures caused by model response formatting without changing PageIndex's core algorithm.

It is intentionally small and reviewable:

- no benchmark dependency is added,
- no provider-specific behavior is introduced,
- no retrieval algorithm behavior is changed except avoiding crashes and using conservative defaults.
