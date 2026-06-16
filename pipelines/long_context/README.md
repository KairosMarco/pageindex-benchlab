# Long-context LLM Baseline

Goal:

```text
full document text -> long context prompt -> answer with page citations
```

This is a baseline, not a RAG framework.

First task:

- Extract page text with PyMuPDF.
- Preserve `[PAGE n]` markers.
- Ask the model to answer using only the document.

## Adapter

Implemented:

```text
pipelines/long_context/adapter.py
scripts/run_long_context_mvp.py
```

No-LLM smoke mode:

```powershell
python scripts\run_long_context_mvp.py --no-llm --force --continue-on-error
python scripts\evaluate_evidence_mvp.py --results-dir reports\long_context\qa --output reports\long_context\evidence_eval.json --continue-on-error
```

Current no-LLM smoke result:

```text
12 / 12 outputs generated
Average evidence recall: 0.583
Average citation precision: 0.194
```

This no-LLM mode only validates document loading, output schema, and evaluation wiring. It is not the final long-context LLM baseline.

LLM mode requires a LiteLLM model string and provider API key:

```powershell
$env:DEEPSEEK_API_KEY="YOUR_KEY"
python scripts\run_long_context_mvp.py --model deepseek/deepseek-v4-pro --force --continue-on-error
python scripts\evaluate_evidence_mvp.py --results-dir reports\long_context\qa --output reports\long_context\evidence_eval.json --continue-on-error
```
