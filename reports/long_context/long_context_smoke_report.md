# Long-context Baseline Smoke Report

Date: 2026-06-16

## Scope

This report covers the first no-LLM smoke run for the Long-context baseline on the FinanceBench MVP subset.

- Dataset: `datasets/financebench/mvp_questions.jsonl`
- Questions: 12
- Unique PDFs: 11
- Method: `long_context_llm`
- Adapter mode: `full_document_context`
- LLM answering: disabled (`--no-llm`)
- Citation pages per question: 3

This is a wiring test, not the final long-context LLM result. It verifies that the baseline can load full PDF text, preserve page markers, produce `BenchmarkResult`, and be evaluated by the shared evidence evaluator.

## Commands

```powershell
D:\pageindex-demo\PageIndex\.venv\Scripts\python.exe scripts\run_long_context_mvp.py --no-llm --force --continue-on-error
D:\pageindex-demo\PageIndex\.venv\Scripts\python.exe scripts\evaluate_evidence_mvp.py --results-dir reports\long_context\qa --output reports\long_context\evidence_eval.json --continue-on-error
```

## Summary

| Metric | Value |
|---|---:|
| Result count | 12 |
| Failure count | 0 |
| Average evidence recall | 0.583 |
| Average citation precision | 0.194 |

Interpretation:

- The baseline wiring is functional for all MVP questions.
- The no-LLM citation fallback is weaker than PageIndex retrieval because it does not use PageIndex document structure or LLM page citation behavior.
- The next meaningful result is the LLM-enabled Long-context run.

## Next Command

After setting a provider key:

```powershell
$env:DEEPSEEK_API_KEY="YOUR_KEY"
D:\pageindex-demo\PageIndex\.venv\Scripts\python.exe scripts\run_long_context_mvp.py --model deepseek/deepseek-v4-pro --force --continue-on-error
D:\pageindex-demo\PageIndex\.venv\Scripts\python.exe scripts\evaluate_evidence_mvp.py --results-dir reports\long_context\qa --output reports\long_context\evidence_eval.json --continue-on-error
```
