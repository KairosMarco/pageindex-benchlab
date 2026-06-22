# PageIndex PR Pattern Review

Date: 2026-06-22

## Scope

Reviewed:

- current open PRs on the first PageIndex pull-request page;
- recently merged PRs;
- several closed-but-unmerged PRs related to malformed JSON, TOC robustness, docs, and setup.

Current PRs from this project:

| PR | Updated title | Status |
|---|---|---|
| https://github.com/VectifyAI/PageIndex/pull/333 | `fix: improve JSON extraction and TOC fallback handling` | Open |
| https://github.com/VectifyAI/PageIndex/pull/334 | `docs: document Windows and LiteLLM provider setup` | Open |

## Title Pattern

Open PRs commonly use:

- `fix: ...`
- `feat: ...`
- `docs: ...`
- `feat(scope): ...`
- `fix(scope): ...`

The two project PR titles were updated to match this style.

## Merged PR Patterns

The PRs most likely to be accepted tend to be one of these:

### 1. Small Concrete Fixes

Examples:

- `fix: prevent infinite loop in extract_toc_content` (#65)
- `Fix TOC prompt variable typo (tob -> toc)` (#109)
- `Fix typo in header for the step: Extract JSON results` (#118)
- `Fix: handle TOC items exceeding document length` (#21)

Common traits:

- narrow failure mode;
- small file count;
- clear before/after behavior;
- easy maintainer review.

### 2. Maintainer-Driven README Updates

Examples:

- `update readme` (#332, #322, #319, #318, #313)
- `Tighten FinanceBench sentence in README` (#312)
- `Update README: Connect with Us buttons and header tagline` (#311)

Common traits:

- mostly maintainer-authored;
- very small edits;
- product-positioning or docs polish.

### 3. Provider Or SDK Improvements

Examples:

- `Integrate litellm for multi-provider LLM support` (#168)
- `feat: add PageIndex SDK with local/cloud dual-mode support` (#207)
- `Add PageIndexClient with agent-based retrieval via OpenAI Agents SDK` (#125)

Common traits:

- aligned with maintainer roadmap;
- often larger but merged by core contributors;
- higher review bar for external contributors.

## Closed-But-Unmerged Warning Cases

Several malformed JSON / LLM-output robustness PRs were closed without merge:

- `fix(extract_json): tolerate non-strict model JSON (e.g. DeepSeek)` (#325)
- `fix: comprehensive crash guards for malformed LLM output` (#218)
- `Add Pydantic validation for LLM responses in page_index` (#100)
- `Fix KeyError in process_none_page_numbers (#97)` (#98)

This matters for PR #333. It means maintainers may already be cautious about broad LLM-output hardening patches. The safest posture is to present #333 as small, tested, and splittable.

## Implications For Our PRs

### PR #333

Strengths:

- uses the repository's `fix:` title style now;
- addresses real observed crashes;
- includes focused tests;
- is directly related to PageIndex indexing robustness.

Risks:

- overlaps with closed malformed-JSON robustness PRs;
- touches multiple fallback sites, not only `extract_json()`;
- may be considered broader than maintainer preference.

Recommended response if maintainers hesitate:

```text
Happy to split this into a smaller parser-only PR first, then follow with TOC fallback handling and tests separately.
```

### PR #334

Strengths:

- uses the repository's `docs:` title style now;
- low-risk documentation change;
- based on real Windows/LiteLLM setup friction.

Risks:

- README changes are often maintainer-driven;
- maintainers may prefer a different provider example or wording.

Recommended response if maintainers hesitate:

```text
Happy to make the provider example generic or move this into a shorter troubleshooting note.
```

## Recommended Contributor Strategy

1. Keep #333 as the primary contribution.
2. Do not add benchmark claims to #333 unless asked.
3. If no response after several working days, leave one concise follow-up on #333.
4. If maintainers request changes, reduce scope rather than defending the full patch.
5. Treat #334 as a supporting docs contribution, not the main path to contributor credit.
