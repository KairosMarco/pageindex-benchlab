# PageIndex Docs PR Handoff

Date: 2026-06-22

## Objective

Open a second focused upstream contribution to `VectifyAI/PageIndex`: a README quickstart improvement for Windows PowerShell and LiteLLM provider setup.

This PR is intentionally separate from the JSON resilience code PR.

Target upstream repository:

```text
https://github.com/VectifyAI/PageIndex
```

Prepared PR title:

```text
Document Windows and LiteLLM provider setup
```

## Current Status

The docs PR branch has been prepared locally against the current upstream `main`.

Local PageIndex PR workspace:

```text
D:\pageindex-upstream-pr
```

Branch:

```text
docs/windows-provider-quickstart
```

Local commit:

```text
f650b6c Document Windows and LiteLLM provider setup
```

Changed file:

```text
README.md
```

## Validation

Command run from `D:\pageindex-upstream-pr`:

```powershell
git diff --check
```

Result:

```text
No whitespace errors.
```

## Why This PR Is Good Contributor Material

- It is small and reviewable.
- It addresses real onboarding friction encountered during local setup.
- It does not touch runtime behavior.
- It documents existing multi-LLM support instead of adding a new dependency.
- It can be reviewed independently from the JSON resilience code PR.

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

## Path A: GitHub CLI

Run:

```powershell
gh auth login
gh repo fork VectifyAI/PageIndex --clone=false
cd D:\pageindex-upstream-pr
git checkout docs/windows-provider-quickstart
git remote set-url origin https://github.com/KairosMarco/PageIndex.git
git remote add upstream https://github.com/VectifyAI/PageIndex.git
git push -u origin docs/windows-provider-quickstart
gh pr create --repo VectifyAI/PageIndex --head KairosMarco:docs/windows-provider-quickstart --base main --title "Document Windows and LiteLLM provider setup" --body-file D:\pageindex-benchlab\docs\upstream-patches\pageindex-windows-provider-quickstart-pr-body.md
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
git checkout docs/windows-provider-quickstart
git remote set-url origin https://github.com/KairosMarco/PageIndex.git
git remote add upstream https://github.com/VectifyAI/PageIndex.git
git push -u origin docs/windows-provider-quickstart
```

4. Open the compare URL:

```text
https://github.com/VectifyAI/PageIndex/compare/main...KairosMarco:PageIndex:docs/windows-provider-quickstart
```

5. Use this PR body:

```text
D:\pageindex-benchlab\docs\upstream-patches\pageindex-windows-provider-quickstart-pr-body.md
```

## Recommended Order

Open the JSON resilience PR first because it is a code contribution with tests.

Open this docs PR second, or use it as the lower-risk first PR if maintainers prefer documentation-only contributions before code changes.
