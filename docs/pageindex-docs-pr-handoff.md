# PageIndex PR #334: Windows And Provider Docs

PR:

```text
https://github.com/VectifyAI/PageIndex/pull/334
```

Title:

```text
docs: document Windows and LiteLLM provider setup
```

Status on 2026-06-22:

```text
Open; no maintainer comments or reviews yet.
```

## Purpose

Improve the PageIndex README quickstart for Windows PowerShell users and non-OpenAI LiteLLM providers.

## Scope

Changed upstream file:

```text
README.md
```

Local branch:

```text
D:\pageindex-upstream-pr
docs/windows-provider-quickstart
f650b6c Document Windows and LiteLLM provider setup
```

## Implementation Summary

- Recommend creating a Python virtual environment before dependency installation.
- Add Windows PowerShell virtualenv activation commands.
- Document the scoped `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` fix for blocked `Activate.ps1`.
- Add a LiteLLM non-OpenAI provider example using `DASHSCOPE_API_KEY` and `--model dashscope/qwen-plus`.
- Point users to LiteLLM provider docs for exact model prefixes and environment variables.

## Validation

Command:

```powershell
git diff --check
```

Result:

```text
No whitespace errors.
```

## Review Strategy

This is a low-risk docs PR. If maintainers object to the specific provider example, replace it with a generic LiteLLM provider placeholder.
