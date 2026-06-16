# Stage 1 Retrieval Comparison

Date: 2026-06-16

## Current Comparable Results

| Method | Mode | Questions | Failures | Avg evidence recall | Avg citation precision | Status |
|---|---|---:|---:|---:|---:|---|
| PageIndex | Retrieval-only, tree page scoring | 12 | 0 | 1.000 | 0.333 | Completed |
| Long-context | No-LLM smoke, lexical fallback citations | 12 | 0 | 0.583 | 0.194 | Wiring validated |
| PageIndex | LLM answer generation, DeepSeek V4 Pro | 12 | 0 | 1.000 | 0.333 | Completed |
| Long-context | LLM answer generation, DeepSeek V4 Pro | 12 | 0 | 0.917 | 0.306 | Completed |

## Notes

- PageIndex currently has the best evidence recall and citation precision on the MVP subset.
- Long-context LLM is a strong baseline, but it missed the gold evidence page for `fb_mvp_005`.
- The current comparison is still evidence-page focused. Answer accuracy evaluation is the next required metric.

## Next Runs

```powershell
$env:DEEPSEEK_API_KEY="YOUR_KEY"

D:\pageindex-demo\PageIndex\.venv\Scripts\python.exe scripts\run_pageindex_qa_mvp.py --model deepseek/deepseek-v4-pro --output-dir reports\pageindex\qa_llm --manifest reports\pageindex\qa_llm_manifest.json --force --continue-on-error
D:\pageindex-demo\PageIndex\.venv\Scripts\python.exe scripts\evaluate_evidence_mvp.py --results-dir reports\pageindex\qa_llm --output reports\pageindex\evidence_eval_llm.json --continue-on-error

D:\pageindex-demo\PageIndex\.venv\Scripts\python.exe scripts\run_long_context_mvp.py --model deepseek/deepseek-v4-pro --output-dir reports\long_context\qa_llm --manifest reports\long_context\qa_llm_manifest.json --force --continue-on-error
D:\pageindex-demo\PageIndex\.venv\Scripts\python.exe scripts\evaluate_evidence_mvp.py --results-dir reports\long_context\qa_llm --output reports\long_context\evidence_eval_llm.json --continue-on-error
```
