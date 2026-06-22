# Contributor Action Plan

Goal:

```text
Open concrete upstream contributions so `KairosMarco` can become a visible contributor to PageIndex and related RAG projects.
```

## Current Priority

The highest-priority action is responding to maintainer feedback on the PageIndex JSON response resilience PR.

Open upstream PR:

```text
https://github.com/VectifyAI/PageIndex/pull/333
```

Prepared artifacts:

```text
docs/upstream-patches/pageindex-json-resilience.patch
docs/upstream-patches/pageindex-json-resilience-pr-ready.md
docs/upstream-patches/pageindex-json-resilience-pr-body.md
docs/pageindex-upstream-pr-handoff.md
```

Second prepared PageIndex PR candidate:

```text
docs/upstream-patches/pageindex-windows-provider-quickstart-pr-body.md
docs/pageindex-docs-pr-handoff.md
```

The second candidate is a documentation-only README improvement for Windows PowerShell virtualenv activation and LiteLLM provider setup. It is intentionally separate from the code PR.

Why this first:

- It fixes concrete failures observed during local PageIndex indexing.
- It is small enough for maintainers to review.
- It includes tests.
- It avoids making broad benchmark superiority claims.
- It can directly produce a GitHub contributor record if accepted.

## Maintainer Response Tasks

1. Monitor `https://github.com/VectifyAI/PageIndex/pull/333`.
2. Reply to maintainer review within 24 hours when possible.
3. If maintainers request smaller changes, split the PR into:
   - JSON parser robustness,
   - TOC fallback handling,
   - tests.
4. Monitor the documentation PR: `https://github.com/VectifyAI/PageIndex/pull/334`.
5. Open a separate benchmark/ranking diagnostic issue or discussion after the code PR is in review.

The local PR branch is already prepared:

```text
Workspace: D:\pageindex-upstream-pr
Branch: fix/json-response-resilience
Commit: 1cf28e5 Improve JSON extraction and TOC fallback handling
Validation: 7 unittest tests passed; py_compile passed
```

Exact push and PR commands are documented in:

```text
docs/pageindex-upstream-pr-handoff.md
```

If maintainers prefer a lower-risk first contribution, open the docs PR from:

```text
Workspace: D:\pageindex-upstream-pr
Branch: docs/windows-provider-quickstart
Commit: f650b6c Document Windows and LiteLLM provider setup
Validation: git diff --check passed
Handoff: docs/pageindex-docs-pr-handoff.md
PR: https://github.com/VectifyAI/PageIndex/pull/334
```

## What Not To Do Yet

- Do not open a large benchmark PR in PageIndex before the robustness PR is in flight.
- Do not claim PageIndex is broadly better than RAG.
- Do not mix finance prompt tuning into the first PageIndex code PR.
- Do not include API keys, local PDFs, or generated raw benchmark outputs in upstream PRs.

## Next Contribution Candidates

After the JSON resilience PR is open:

1. PageIndex issue or discussion: benchmark plan and evidence-page QA diagnostics.
2. Documentation PR: Windows quickstart and provider key setup.
3. Documentation PR: local PDF example with expected output shape.
4. Diagnostic PR or example: PageIndex structure-to-evidence-page scoring report.
5. LlamaIndex contribution: small docs/example issue based on finance-aware reranking diagnostics.

## Success Criteria

Minimum success:

```text
One upstream PR opened with tests and clear validation.
```

Better success:

```text
Maintainer review received and addressed.
```

Best success:

```text
PR merged, GitHub contributor record created, and follow-up issue/discussion opened with benchmark evidence.
```
