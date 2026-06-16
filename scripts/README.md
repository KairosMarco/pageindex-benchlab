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

## Run Hybrid RAG MVP Baseline

Smoke test without LLM answer generation:

```powershell
python scripts\run_hybrid_rag_mvp.py --no-llm --output-dir reports\hybrid_rag\qa_smoke --manifest reports\hybrid_rag\qa_smoke_manifest.json --force --continue-on-error
python scripts\evaluate_evidence_mvp.py --results-dir reports\hybrid_rag\qa_smoke --output reports\hybrid_rag\evidence_eval_smoke.json --continue-on-error
```

LLM mode:

```powershell
python scripts\run_hybrid_rag_mvp.py --model deepseek/deepseek-v4-pro --output-dir reports\hybrid_rag\qa_llm --manifest reports\hybrid_rag\qa_llm_manifest.json --force --continue-on-error
python scripts\evaluate_evidence_mvp.py --results-dir reports\hybrid_rag\qa_llm --output reports\hybrid_rag\evidence_eval_llm.json --continue-on-error
python scripts\evaluate_answers_mvp.py --results-dir reports\hybrid_rag\qa_llm --output reports\hybrid_rag\answer_eval_llm.json --mode llm --model deepseek/deepseek-v4-pro --continue-on-error
```

## Run LlamaIndex Vector RAG Diagnostic Baseline

Smoke test without LLM answer generation:

```powershell
python scripts\run_llamaindex_vector_rag_mvp.py --no-llm --output-dir reports\llamaindex_vector_rag\qa_smoke --manifest reports\llamaindex_vector_rag\qa_smoke_manifest.json --force --continue-on-error
python scripts\evaluate_evidence_mvp.py --results-dir reports\llamaindex_vector_rag\qa_smoke --output reports\llamaindex_vector_rag\evidence_eval_smoke.json --continue-on-error
```

Citation-depth diagnostics:

```powershell
python scripts\run_llamaindex_vector_rag_mvp.py --no-llm --max-citations 6 --output-dir reports\llamaindex_vector_rag\qa_smoke_cite6 --manifest reports\llamaindex_vector_rag\qa_smoke_cite6_manifest.json --force --continue-on-error
python scripts\evaluate_evidence_mvp.py --results-dir reports\llamaindex_vector_rag\qa_smoke_cite6 --output reports\llamaindex_vector_rag\evidence_eval_smoke_cite6.json --continue-on-error

python scripts\run_llamaindex_vector_rag_mvp.py --no-llm --max-citations 12 --output-dir reports\llamaindex_vector_rag\qa_smoke_cite12 --manifest reports\llamaindex_vector_rag\qa_smoke_cite12_manifest.json --force --continue-on-error
python scripts\evaluate_evidence_mvp.py --results-dir reports\llamaindex_vector_rag\qa_smoke_cite12 --output reports\llamaindex_vector_rag\evidence_eval_smoke_cite12.json --continue-on-error
```

This is currently a diagnostic baseline. Do not add it to the main comparison table until retrieval quality improves or the report explicitly frames it as a weaker baseline.

## Run LlamaIndex Hybrid RAG Diagnostic Baseline

Single-question smoke test:

```powershell
python scripts\run_llamaindex_hybrid_rag_mvp.py --no-llm --question-id fb_mvp_001 --output-dir reports\llamaindex_hybrid_rag\qa_smoke --manifest reports\llamaindex_hybrid_rag\qa_smoke_manifest.json --force --continue-on-error
python scripts\evaluate_evidence_mvp.py --results-dir reports\llamaindex_hybrid_rag\qa_smoke --output reports\llamaindex_hybrid_rag\evidence_eval_smoke.json --continue-on-error
```

Optional cross-encoder diagnostic:

```powershell
python scripts\run_llamaindex_hybrid_rag_mvp.py --no-llm --question-id fb_mvp_001 --cross-encoder-model cross-encoder/ms-marco-MiniLM-L-6-v2 --output-dir reports\llamaindex_hybrid_rag\qa_smoke_cross --manifest reports\llamaindex_hybrid_rag\qa_smoke_cross_manifest.json --force --continue-on-error
python scripts\evaluate_evidence_mvp.py --results-dir reports\llamaindex_hybrid_rag\qa_smoke_cross --output reports\llamaindex_hybrid_rag\evidence_eval_smoke_cross.json --continue-on-error
```

This diagnostic currently shows that the gold page can appear in a wider candidate set, but the top-three citation ranking still needs improvement.

## Evaluate Answer Accuracy

Heuristic mode:

```powershell
python scripts\evaluate_answers_mvp.py --results-dir reports\pageindex\qa_llm --output reports\pageindex\answer_eval_heuristic.json --mode heuristic --continue-on-error
```

LLM judge mode:

```powershell
python scripts\evaluate_answers_mvp.py --results-dir reports\pageindex\qa_llm --output reports\pageindex\answer_eval_llm.json --mode llm --model deepseek/deepseek-v4-pro --continue-on-error
```

## Summarize Stage 1 Metrics

```powershell
python scripts\summarize_stage1_metrics.py
```

Outputs:

```text
reports/stage1_metrics_summary.json
reports/stage1_metrics_summary.md
```

## Generate Detailed Stage 1 Evidence Report

```powershell
python scripts\check_stage1_environment.py
python scripts\generate_stage1_evidence_report.py
python scripts\validate_stage1_artifacts.py
```

Outputs:

```text
reports/stage1_detailed_evidence_report.md
reports/stage1_detailed_evidence_report.json
reports/stage1_per_question_results.csv
reports/stage1_validation_report.json
reports/stage1_environment_report.json
```

The validation script checks that method result counts, evidence metrics, answer metrics, token usage, latency, and known failure cases are consistent with the committed raw JSON artifacts.
