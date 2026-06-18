# PageIndex PR-Ready Contribution: JSON Response Resilience

Target repository:

```text
https://github.com/VectifyAI/PageIndex
```

Recommended PR title:

```text
Improve JSON extraction and TOC fallback handling
```

## Contributor Objective

This is the first upstream contribution candidate because it is small, reviewable, and directly supported by benchmark evidence from `pageindex-benchlab`.

The intended contributor outcome is:

```text
Open a PageIndex pull request that improves indexing robustness for noisy LLM JSON responses.
```

If the PR is accepted, the GitHub account that opens it becomes a contributor to PageIndex.

## Patch File

Apply this zero-context patch to a clean fork of PageIndex:

```text
docs/upstream-patches/pageindex-json-resilience.patch
```

Use `git apply --unidiff-zero` for this patch. The patch is generated in zero-context form to avoid unrelated upstream trailing-whitespace churn in `page_index.py` and `utils.py`.

The patch changes:

```text
pageindex/utils.py
pageindex/page_index.py
tests/test_json_resilience.py
```

## Problem

PageIndex relies on LLM-produced JSON in TOC detection, TOC transformation, page-offset handling, and TOC repair. During local FinanceBench indexing runs, model responses sometimes caused crashes or incomplete indexing because they returned:

- Markdown-fenced JSON
- explanatory text before JSON
- JSON arrays with trailing text
- Python-style `None`, `True`, or `False`
- missing expected keys such as `toc_detected`, `page_index_given_in_toc`, or `physical_index`
- a dict where downstream code expected a list
- missing page offset values

Observed local failures included:

```text
KeyError: 'toc_detected'
KeyError: 'page_index_given_in_toc'
AttributeError: 'dict' object has no attribute 'extend'
TypeError: unsupported operand type(s) for +: 'int' and 'NoneType'
KeyError: 'physical_index'
```

## Implementation Summary

The patch:

- makes `extract_json()` parse fenced JSON, embedded JSON, arrays, trailing text, and Python-style literals;
- returns safe default answers when expected JSON fields are missing;
- normalizes model-produced TOC JSON into `list[dict]`;
- skips page-offset addition when no offset can be inferred;
- leaves unresolved page-number repair items unresolved instead of crashing;
- lets low-confidence no-TOC processing return the best available structure instead of raising `Processing failed`;
- adds `unittest` coverage for the JSON and TOC fallback behavior.

## Validation Already Run Locally

Temporary upstream patch workspace:

```text
D:\pageindex-pr-minimal
```

Commands:

```powershell
D:\pageindex-demo\PageIndex\.venv\Scripts\python.exe -m unittest discover -s tests
D:\pageindex-demo\PageIndex\.venv\Scripts\python.exe -m py_compile pageindex\utils.py pageindex\page_index.py tests\test_json_resilience.py
```

Result:

```text
Ran 7 tests
OK
```

The broader BenchLab validation after applying equivalent local fixes:

```text
Expanded PageIndex structures: 24 / 24 unique source documents
Expanded PageIndex retrieval-only QA: 25 / 25 generated
Expanded evidence recall: 1.000
Expanded LLM QA: 25 / 25 generated
Expanded answer accuracy: 0.920
```

Relevant artifacts:

```text
reports/pageindex/expanded_readiness.md
reports/pageindex/expanded_indexing_notes.md
reports/pageindex/pageindex_ranking_diagnostics.md
reports/pageindex/pageindex_answer_issue_analysis.md
reports/pageindex_expanded_llm_diagnostics.md
```

## PR Body Draft

```markdown
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
```

## Exact Commands To Open The PR

Use these commands after forking PageIndex on GitHub.

```powershell
git clone https://github.com/<YOUR_GITHUB_USERNAME>/PageIndex.git
cd PageIndex
git remote add upstream https://github.com/VectifyAI/PageIndex.git
git fetch upstream
git checkout -b fix/json-response-resilience upstream/main
git apply --unidiff-zero D:\pageindex-benchlab\docs\upstream-patches\pageindex-json-resilience.patch
python -m unittest discover -s tests
python -m py_compile pageindex\utils.py pageindex\page_index.py tests\test_json_resilience.py
git add pageindex\utils.py pageindex\page_index.py tests\test_json_resilience.py
git commit -m "Improve JSON extraction and TOC fallback handling"
git push origin fix/json-response-resilience
```

Then open:

```text
https://github.com/VectifyAI/PageIndex/compare/main...<YOUR_GITHUB_USERNAME>:PageIndex:fix/json-response-resilience
```

## Follow-up Plan

After this PR is opened, the next contributor-oriented actions are:

1. Respond to maintainer review quickly.
2. If maintainers prefer a smaller patch, split it into:
   - `extract_json()` parser robustness,
   - TOC fallback handling,
   - tests.
3. Open a separate issue or discussion for benchmark reproduction notes instead of mixing benchmark claims into the code PR.
