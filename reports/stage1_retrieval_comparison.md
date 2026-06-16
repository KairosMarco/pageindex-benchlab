# Stage 1 Retrieval Comparison

Date: 2026-06-16

## Current Comparable Results

| Method | Mode | Questions | Failures | Avg evidence recall | Avg citation precision | Status |
|---|---|---:|---:|---:|---:|---|
| PageIndex | Retrieval-only, tree page scoring | 12 | 0 | 1.000 | 0.333 | Completed |
| Long-context | No-LLM smoke, lexical fallback citations | 12 | 0 | 0.583 | 0.194 | Wiring validated |

## Notes

- PageIndex retrieval-only is the current strongest completed result.
- Long-context is not final yet. The current run only validates the baseline pipeline before LLM answer generation.
- LLM answer generation was not run in the latest local shell because no model provider API key was available in the process environment.

## Next Runs

```powershell
$env:DEEPSEEK_API_KEY="YOUR_KEY"

D:\pageindex-demo\PageIndex\.venv\Scripts\python.exe scripts\run_pageindex_qa_mvp.py --model deepseek/deepseek-v4-pro --output-dir reports\pageindex\qa_llm --manifest reports\pageindex\qa_llm_manifest.json --force --continue-on-error
D:\pageindex-demo\PageIndex\.venv\Scripts\python.exe scripts\evaluate_evidence_mvp.py --results-dir reports\pageindex\qa_llm --output reports\pageindex\evidence_eval_llm.json --continue-on-error

D:\pageindex-demo\PageIndex\.venv\Scripts\python.exe scripts\run_long_context_mvp.py --model deepseek/deepseek-v4-pro --force --continue-on-error
D:\pageindex-demo\PageIndex\.venv\Scripts\python.exe scripts\evaluate_evidence_mvp.py --results-dir reports\long_context\qa --output reports\long_context\evidence_eval.json --continue-on-error
```
