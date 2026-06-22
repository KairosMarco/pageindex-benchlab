# PageIndex Upstream PR Handoff

Date: 2026-06-22

## Objective

Open a focused upstream PR to `VectifyAI/PageIndex` so the project owner can earn a visible contributor record through a real bug fix with tests.

Target upstream repository:

```text
https://github.com/VectifyAI/PageIndex
```

Prepared PR title:

```text
Improve JSON extraction and TOC fallback handling
```

## Current Status

The PR branch has been prepared locally against the current upstream `main`.

Local PageIndex PR workspace:

```text
D:\pageindex-upstream-pr
```

Branch:

```text
fix/json-response-resilience
```

Local commit:

```text
1cf28e5 Improve JSON extraction and TOC fallback handling
```

Changed files:

```text
pageindex/utils.py
pageindex/page_index.py
tests/test_json_resilience.py
```

## Validation

Commands run from `D:\pageindex-upstream-pr`:

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

Note: the test run emitted a LiteLLM warning about failing to fetch a remote model cost map and falling back to a local backup. This warning did not affect the unit tests.

## Why This PR Is Good Contributor Material

- It fixes concrete failures observed during PageIndex indexing.
- It is small enough to review.
- It includes focused tests.
- It does not make broad benchmark claims.
- It improves provider robustness for noisy LLM JSON responses.

Observed failure classes:

```text
KeyError: 'toc_detected'
KeyError: 'page_index_given_in_toc'
AttributeError: 'dict' object has no attribute 'extend'
TypeError: unsupported operand type(s) for +: 'int' and 'NoneType'
KeyError: 'physical_index'
```

## Current Blocker

The local GitHub CLI is not authenticated:

```text
gh auth status
=> You are not logged into any GitHub hosts.
```

The expected fork is also not currently reachable:

```text
https://github.com/KairosMarco/PageIndex
=> Repository not found
```

This means the code is ready, but the upstream PR cannot be opened from this machine until the owner either logs in with GitHub CLI or creates the fork through the GitHub web UI.

## Path A: GitHub CLI

Run:

```powershell
gh auth login
gh repo fork VectifyAI/PageIndex --clone=false
cd D:\pageindex-upstream-pr
git remote set-url origin https://github.com/KairosMarco/PageIndex.git
git remote add upstream https://github.com/VectifyAI/PageIndex.git
git push -u origin fix/json-response-resilience
gh pr create --repo VectifyAI/PageIndex --head KairosMarco:fix/json-response-resilience --base main --title "Improve JSON extraction and TOC fallback handling" --body-file D:\pageindex-benchlab\docs\upstream-patches\pageindex-json-resilience-pr-body.md
```

If `git remote add upstream` says the remote already exists, continue with the next command.

## Path B: GitHub Web UI

1. Open:

```text
https://github.com/VectifyAI/PageIndex/fork
```

2. Create the fork under the `KairosMarco` account.

3. Push the prepared local branch:

```powershell
cd D:\pageindex-upstream-pr
git remote set-url origin https://github.com/KairosMarco/PageIndex.git
git remote add upstream https://github.com/VectifyAI/PageIndex.git
git push -u origin fix/json-response-resilience
```

4. Open the compare URL:

```text
https://github.com/VectifyAI/PageIndex/compare/main...KairosMarco:PageIndex:fix/json-response-resilience
```

5. Use this PR body:

```text
D:\pageindex-benchlab\docs\upstream-patches\pageindex-json-resilience-pr-body.md
```

## After The PR Is Open

Update these files with the PR URL:

```text
README.md
docs/stage-1-status.md
docs/contributor-action-plan.md
docs/pageindex-upstream-pr-handoff.md
```

Then commit and push the BenchLab documentation update.

Next contributor action after the PR is opened:

```text
Open a separate PageIndex issue or discussion summarizing the benchmark-backed ranking diagnostics. Do not mix benchmark claims into the JSON resilience PR.
```
