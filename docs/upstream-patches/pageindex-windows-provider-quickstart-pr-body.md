## Summary

This PR adds a small quickstart clarification for local PageIndex setup:

- recommend a Python virtual environment before installing dependencies,
- add Windows PowerShell activation commands,
- document the common `Activate.ps1` execution-policy fix,
- show how to use a non-OpenAI LiteLLM provider by setting the provider key and passing `--model`.

## Why

New users can currently follow the README successfully on Unix-like shells, but Windows users may hit PowerShell's script execution policy when activating `.venv`.

The README also mentions multi-LLM support through LiteLLM, but the quickstart only shows `OPENAI_API_KEY`. Adding a provider-key example makes it clearer that users can run PageIndex with other LiteLLM-supported providers without changing code.

## Changes

- Extend the install step with `python3 -m venv .venv` and activation.
- Add equivalent Windows PowerShell commands.
- Add `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` as the scoped fix for blocked virtualenv activation.
- Add a non-OpenAI provider example using `DASHSCOPE_API_KEY` and `--model dashscope/qwen-plus`.
- Point users back to LiteLLM provider docs for exact model prefixes and environment variables.

## Validation

```powershell
git diff --check
```

Local result:

```text
No whitespace errors.
```
