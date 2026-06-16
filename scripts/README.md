# Scripts

Utility scripts for repeatable local benchmark setup.

## Download FinanceBench MVP PDFs

```powershell
python scripts\download_mvp_pdfs.py
```

Outputs local PDFs to:

```text
datasets/raw/financebench/pdfs/
```

This directory is intentionally ignored by git.

The script writes a committed manifest to:

```text
reports/mvp_pdf_manifest.json
```

## Run PageIndex Indexing

Requires a local PageIndex checkout and an LLM provider key.

Default PageIndex path on Windows:

```text
D:\pageindex-demo\PageIndex
```

Override with:

```powershell
$env:PAGEINDEX_REPO="D:\path\to\PageIndex"
```

Set a model API key in the current shell. For DashScope/Qwen:

```powershell
$env:DASHSCOPE_API_KEY="YOUR_NEW_KEY"
```

For DeepSeek:

```powershell
$env:DEEPSEEK_API_KEY="YOUR_KEY"
```

Dry run:

```powershell
python scripts\run_pageindex_mvp.py --dry-run --limit 3
```

Run all MVP PDFs:

```powershell
python scripts\run_pageindex_mvp.py
```

Outputs copied PageIndex structures to:

```text
reports/pageindex/structures/
```

Do not commit API keys.

## Run PageIndex MVP QA

Run retrieval-only QA on all 12 MVP questions:

```powershell
python scripts\run_pageindex_qa_mvp.py --no-llm --force --continue-on-error
```

Use `--max-pages` to control how many citation pages are returned per question. The default is 3.

Outputs:

```text
reports/pageindex/qa/
reports/pageindex/qa_manifest.json
```

Run evidence evaluation:

```powershell
python scripts\evaluate_evidence_mvp.py --continue-on-error
```

Output:

```text
reports/pageindex/evidence_eval.json
```

LLM answer mode requires a LiteLLM model name and the matching provider key in the current shell:

```powershell
python scripts\run_pageindex_qa_mvp.py --model deepseek/deepseek-v4-pro --output-dir reports\pageindex\qa_llm --manifest reports\pageindex\qa_llm_manifest.json --force --continue-on-error
python scripts\evaluate_evidence_mvp.py --results-dir reports\pageindex\qa_llm --output reports\pageindex\evidence_eval_llm.json --continue-on-error
```

## Run Long-context MVP Baseline

Smoke test without LLM answer generation:

```powershell
python scripts\run_long_context_mvp.py --no-llm --output-dir reports\long_context\qa_smoke --manifest reports\long_context\qa_smoke_manifest.json --force --continue-on-error
python scripts\evaluate_evidence_mvp.py --results-dir reports\long_context\qa_smoke --output reports\long_context\evidence_eval_smoke.json --continue-on-error
```

LLM mode:

```powershell
python scripts\run_long_context_mvp.py --model deepseek/deepseek-v4-pro --output-dir reports\long_context\qa_llm --manifest reports\long_context\qa_llm_manifest.json --force --continue-on-error
python scripts\evaluate_evidence_mvp.py --results-dir reports\long_context\qa_llm --output reports\long_context\evidence_eval_llm.json --continue-on-error
```

## Run Vector RAG MVP Baseline

Smoke test without LLM answer generation:

```powershell
python scripts\run_vector_rag_mvp.py --no-llm --output-dir reports\vector_rag\qa_smoke --manifest reports\vector_rag\qa_smoke_manifest.json --force --continue-on-error
python scripts\evaluate_evidence_mvp.py --results-dir reports\vector_rag\qa_smoke --output reports\vector_rag\evidence_eval_smoke.json --continue-on-error
```

LLM mode:

```powershell
python scripts\run_vector_rag_mvp.py --model deepseek/deepseek-v4-pro --output-dir reports\vector_rag\qa_llm --manifest reports\vector_rag\qa_llm_manifest.json --force --continue-on-error
python scripts\evaluate_evidence_mvp.py --results-dir reports\vector_rag\qa_llm --output reports\vector_rag\evidence_eval_llm.json --continue-on-error
```

## Evaluate Answer Accuracy

Heuristic mode:

```powershell
python scripts\evaluate_answers_mvp.py --results-dir reports\pageindex\qa_llm --output reports\pageindex\answer_eval_heuristic.json --mode heuristic --continue-on-error
```

LLM judge mode:

```powershell
python scripts\evaluate_answers_mvp.py --results-dir reports\pageindex\qa_llm --output reports\pageindex\answer_eval_llm.json --mode llm --model deepseek/deepseek-v4-pro --continue-on-error
```
