# Contributor Action Plan

Goal:

```text
Earn visible upstream contribution credit through small, reviewable PageIndex contributions backed by local benchmark evidence.
```

## Current Priority

Monitor and respond to the two open PageIndex PRs:

| PR | Priority | Action |
|---|---:|---|
| https://github.com/VectifyAI/PageIndex/pull/333 | 1 | Respond to code review; split if maintainers request smaller scope |
| https://github.com/VectifyAI/PageIndex/pull/334 | 2 | Respond to wording or docs-structure feedback |

Current PR status on 2026-06-22:

```text
PR #333: open, no comments or reviews yet
PR #334: open, no comments or reviews yet
```

## Response Policy

- Do not repeatedly ping maintainers.
- Wait several working days before a follow-up comment.
- Keep follow-up comments short and specific.
- If review arrives, reply within 24 hours when possible.
- Keep benchmark discussion out of the code PR unless maintainers ask for it.

Suggested PR #333 follow-up if there is no response after several working days:

```text
Hi maintainers, just checking whether this PR is aligned with the direction of PageIndex.

I kept the scope focused on JSON response resilience and TOC fallback handling, with unittest coverage. Happy to split this into smaller PRs if that would make review easier.
```

## If PR #333 Is Too Broad

Split into smaller PRs:

1. `extract_json()` parser robustness.
2. TOC fallback handling for missing fields and object/list normalization.
3. Test-only follow-up if maintainers prefer smaller review steps.

## Next Contribution Candidates

Only open these after the current PRs have had time for review:

1. PageIndex benchmark/ranking diagnostics issue or discussion.
2. PageIndex local PDF example with expected output shape.
3. PageIndex `.env.example` or provider setup docs, if maintainers want more quickstart coverage.
4. LlamaIndex docs/example issue based on finance-aware reranking diagnostics.

## Boundaries

- Do not claim PageIndex is broadly better than RAG.
- Do not open large benchmark PRs against PageIndex.
- Do not include API keys, local PDFs, or raw generated benchmark outputs in upstream PRs.
- Keep each upstream contribution scoped to one reviewable topic.

## Success Criteria

Minimum success:

```text
At least one PageIndex PR receives maintainer review.
```

Better success:

```text
At least one PageIndex PR is merged.
```

Best success:

```text
PR #333 is merged, contributor credit is created, and a separate benchmark diagnostics discussion is opened with scoped evidence.
```
