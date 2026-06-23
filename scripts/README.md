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

## Check PageIndex Expanded Readiness

Summarize which expanded 25-question FinanceBench documents already have PageIndex structures:

```powershell
python scripts\summarize_pageindex_expanded_readiness.py
```

Outputs:

```text
reports/pageindex/expanded_readiness.md
reports/pageindex/expanded_readiness.json
```

As of the committed readiness report, the expanded set has `25` questions across `24` unique source documents. PageIndex structures exist for all `24` documents, covering all `25` runnable questions.

Run retrieval-only expanded PageIndex QA:

```powershell
python scripts\run_pageindex_qa_mvp.py --questions datasets\financebench\expanded_questions_25.jsonl --structure-dir reports\pageindex\structures --output-dir reports\pageindex\qa_expanded_25 --manifest reports\pageindex\qa_expanded_25_manifest.json --no-llm --force --continue-on-error
python scripts\evaluate_evidence_mvp.py --questions datasets\financebench\expanded_questions_25.jsonl --results-dir reports\pageindex\qa_expanded_25 --output reports\pageindex\evidence_eval_qa_expanded_25.json --continue-on-error
python scripts\summarize_pageindex_expanded_partial.py
python scripts\analyze_pageindex_expanded_ranking.py
```

Current expanded PageIndex retrieval-only result:

```text
Generated QA outputs: 25 / 25
Average evidence recall: 1.000
Average citation precision: 0.347
```

Run expanded PageIndex LLM answer generation and validation:

```powershell
$env:DEEPSEEK_API_KEY="YOUR_KEY"
python scripts\run_pageindex_qa_mvp.py --questions datasets\financebench\expanded_questions_25.jsonl --structure-dir reports\pageindex\structures --output-dir reports\pageindex\qa_llm_expanded_25 --manifest reports\pageindex\qa_llm_expanded_25_manifest.json --model deepseek/deepseek-v4-pro --force --continue-on-error
python scripts\evaluate_evidence_mvp.py --questions datasets\financebench\expanded_questions_25.jsonl --results-dir reports\pageindex\qa_llm_expanded_25 --output reports\pageindex\evidence_eval_qa_llm_expanded_25.json --continue-on-error
python scripts\evaluate_answers_mvp.py --questions datasets\financebench\expanded_questions_25.jsonl --results-dir reports\pageindex\qa_llm_expanded_25 --output reports\pageindex\answer_eval_qa_llm_expanded_25.json --mode llm --model deepseek/deepseek-v4-pro --continue-on-error
python scripts\summarize_pageindex_expanded_llm.py
python scripts\validate_expanded_pageindex_llm_artifacts.py
python scripts\analyze_pageindex_answer_issues.py
```

Current expanded PageIndex LLM result:

```text
Generated answers: 25 / 25
Evidence recall: 1.000
Citation precision: 0.347
Answer accuracy: 0.920
Verdicts: 23 correct, 0 partial, 2 incorrect
```

Current non-correct answer analysis:

```text
Issue count: 2
Retrieval succeeded for issue cases: 2 / 2
fb_exp_019: rounding or judge-policy case
fb_exp_020: capital-intensity reasoning case
```

Run targeted PageIndex answer-prompt probes for the two remaining expanded answer issues:

```powershell
$env:DEEPSEEK_API_KEY="YOUR_KEY"
python scripts\run_pageindex_qa_mvp.py --questions datasets\financebench\expanded_questions_25.jsonl --structure-dir reports\pageindex\structures --output-dir reports\pageindex\qa_llm_expanded_25_finance_reasoning_v2_probe --manifest reports\pageindex\qa_llm_expanded_25_finance_reasoning_v2_probe_manifest.json --model deepseek/deepseek-v4-pro --answer-prompt-mode finance_reasoning_v2 --question-id fb_exp_019 --question-id fb_exp_020 --force --continue-on-error
python scripts\evaluate_evidence_mvp.py --questions datasets\financebench\expanded_questions_25.jsonl --results-dir reports\pageindex\qa_llm_expanded_25_finance_reasoning_v2_probe --output reports\pageindex\evidence_eval_qa_llm_expanded_25_finance_reasoning_v2_probe.json --continue-on-error
python scripts\evaluate_answers_mvp.py --questions datasets\financebench\expanded_questions_25.jsonl --results-dir reports\pageindex\qa_llm_expanded_25_finance_reasoning_v2_probe --output reports\pageindex\answer_eval_qa_llm_expanded_25_finance_reasoning_v2_probe.json --mode llm --model deepseek/deepseek-v4-pro --continue-on-error

python scripts\run_pageindex_qa_mvp.py --questions datasets\financebench\expanded_questions_25.jsonl --structure-dir reports\pageindex\structures --output-dir reports\pageindex\qa_llm_expanded_25_finance_reasoning_v3_probe --manifest reports\pageindex\qa_llm_expanded_25_finance_reasoning_v3_probe_manifest.json --model deepseek/deepseek-v4-pro --answer-prompt-mode finance_reasoning_v3 --question-id fb_exp_019 --question-id fb_exp_020 --force --continue-on-error
python scripts\evaluate_evidence_mvp.py --questions datasets\financebench\expanded_questions_25.jsonl --results-dir reports\pageindex\qa_llm_expanded_25_finance_reasoning_v3_probe --output reports\pageindex\evidence_eval_qa_llm_expanded_25_finance_reasoning_v3_probe.json --continue-on-error
python scripts\evaluate_answers_mvp.py --questions datasets\financebench\expanded_questions_25.jsonl --results-dir reports\pageindex\qa_llm_expanded_25_finance_reasoning_v3_probe --output reports\pageindex\answer_eval_qa_llm_expanded_25_finance_reasoning_v3_probe.json --mode llm --model deepseek/deepseek-v4-pro --continue-on-error
python scripts\summarize_pageindex_prompt_variants.py
python scripts\analyze_pageindex_answer_issues.py
```

Current targeted PageIndex prompt-ablation result:

```text
finance_reasoning_v2 probe: evidence recall 1.000, answer accuracy 0.500
finance_reasoning_v3 probe: evidence recall 1.000, answer accuracy 1.000
```

The prompt probes are diagnostic only. The default prompt remains the main 25-question PageIndex comparison row.

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

Expanded 25-question LLM diagnostics:

```powershell
$env:DEEPSEEK_API_KEY="YOUR_KEY"
python scripts\run_long_context_expanded_llm_diagnostics.py --force --continue-on-error
python scripts\validate_expanded_long_context_artifacts.py
```

This writes:

```text
reports/long_context_expanded_llm_diagnostics.md
reports/long_context_expanded_llm_diagnostics.json
reports/expanded_long_context_validation_report.json
reports/long_context/qa_llm_expanded_25/
reports/long_context/qa_llm_expanded_25_manifest.json
reports/long_context/evidence_eval_qa_llm_expanded_25.json
reports/long_context/answer_eval_qa_llm_expanded_25.json
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

## Check BookRAG Readiness

BookRAG is a planned external graph-tree baseline. Keep its source and environment outside this repository.

Check whether a local BookRAG checkout and environment are ready for adapter work:

```powershell
python scripts\check_bookrag_readiness.py --bookrag-repo D:\bookrag-source
```

This writes:

```text
reports/bookrag/readiness.json
```

The readiness script does not run BookRAG indexing. It checks the expected repository files, Python version, selected package metadata, and optionally selected imports:

```powershell
python scripts\check_bookrag_readiness.py --bookrag-repo D:\bookrag-source --import-check
```

BookRAG requires a heavier method-specific setup than the current baselines, including MinerU and, in the default configuration, a MinerU/SGLang parsing service. Do not add BookRAG dependencies to BenchLab's main `requirements.txt`.

Build the FinanceBench dataset file expected by BookRAG:

```powershell
python scripts\build_bookrag_dataset.py --questions datasets\financebench\expanded_questions_25.jsonl --output datasets\bookrag\financebench_expanded_25.json --mapping datasets\bookrag\financebench_expanded_25_mapping.json
```

This writes a BookRAG-shaped dataset plus a BenchLab sidecar mapping:

```text
datasets/bookrag/financebench_expanded_25.json
datasets/bookrag/financebench_expanded_25_mapping.json
```

Prepare BookRAG YAML configs:

```powershell
python scripts\prepare_bookrag_config.py
```

This writes:

```text
reports/bookrag/config/financebench_expanded_25.yaml
reports/bookrag/config/financebench_gbc_template.yaml
```

The system config is a template and must be edited before running BookRAG. Keep real API keys and service URLs out of git.

Current BookRAG status:

```text
reports/bookrag/status.md
```

## Run LlamaIndex Vector RAG Diagnostic Baseline

Current finance-aware smoke test without LLM answer generation:

```powershell
python scripts\run_llamaindex_vector_rag_mvp.py --no-llm --output-dir reports\llamaindex_vector_rag\qa_smoke_finance --manifest reports\llamaindex_vector_rag\qa_smoke_finance_manifest.json --force --continue-on-error
python scripts\evaluate_evidence_mvp.py --results-dir reports\llamaindex_vector_rag\qa_smoke_finance --output reports\llamaindex_vector_rag\evidence_eval_smoke_finance.json --continue-on-error
```

Generic reranker comparison without the finance line-item boost:

```powershell
python scripts\run_llamaindex_vector_rag_mvp.py --no-llm --disable-finance-rerank --output-dir reports\llamaindex_vector_rag\qa_smoke --manifest reports\llamaindex_vector_rag\qa_smoke_manifest.json --force --continue-on-error
python scripts\evaluate_evidence_mvp.py --results-dir reports\llamaindex_vector_rag\qa_smoke --output reports\llamaindex_vector_rag\evidence_eval_smoke.json --continue-on-error
```

Citation-depth diagnostics:

```powershell
python scripts\run_llamaindex_vector_rag_mvp.py --no-llm --disable-finance-rerank --max-citations 6 --output-dir reports\llamaindex_vector_rag\qa_smoke_cite6 --manifest reports\llamaindex_vector_rag\qa_smoke_cite6_manifest.json --force --continue-on-error
python scripts\evaluate_evidence_mvp.py --results-dir reports\llamaindex_vector_rag\qa_smoke_cite6 --output reports\llamaindex_vector_rag\evidence_eval_smoke_cite6.json --continue-on-error

python scripts\run_llamaindex_vector_rag_mvp.py --no-llm --disable-finance-rerank --max-citations 12 --output-dir reports\llamaindex_vector_rag\qa_smoke_cite12 --manifest reports\llamaindex_vector_rag\qa_smoke_cite12_manifest.json --force --continue-on-error
python scripts\evaluate_evidence_mvp.py --results-dir reports\llamaindex_vector_rag\qa_smoke_cite12 --output reports\llamaindex_vector_rag\evidence_eval_smoke_cite12.json --continue-on-error
```

This is currently a diagnostic baseline. The finance-aware reranker reaches 1.000 evidence recall on the 12-question no-LLM MVP run, and the LLM diagnostic workflow below records answer generation, evidence evaluation, answer judging, token usage, and latency.

Run finance-aware LLM diagnostics for Vector and Hybrid candidates:

```powershell
$env:DEEPSEEK_API_KEY="YOUR_KEY"
python scripts\run_llamaindex_finance_llm_diagnostics.py --force --continue-on-error
```

This runs:

```text
reports/llamaindex_vector_rag/qa_llm_finance/
reports/llamaindex_vector_rag/evidence_eval_llm_finance.json
reports/llamaindex_vector_rag/answer_eval_llm_finance.json
reports/llamaindex_hybrid_rag/qa_llm_finance/
reports/llamaindex_hybrid_rag/evidence_eval_llm_finance.json
reports/llamaindex_hybrid_rag/answer_eval_llm_finance.json
reports/llamaindex_finance_llm_diagnostics.md
reports/llamaindex_finance_llm_diagnostics.json
```

Run context-size tuning without LLM calls:

```powershell
python scripts\run_llamaindex_context_tuning.py --rerank-top-k 3 --rerank-top-k 6 --rerank-top-k 9 --rerank-top-k 12 --force --continue-on-error
```

Build and validate the 25-question expanded FinanceBench retrieval set:

```powershell
python datasets\financebench\build_expanded_subset.py --target-count 25
python scripts\download_mvp_pdfs.py --questions datasets\financebench\expanded_questions_25.jsonl --manifest reports\expanded_25_pdf_manifest.json --continue-on-error
python scripts\run_llamaindex_expanded_retrieval.py --rerank-top-k 3 --rerank-top-k 6 --rerank-top-k 12 --force --continue-on-error
python scripts\run_llamaindex_expanded_retrieval.py --variant-suffix concept_v2 --rerank-top-k 3 --rerank-top-k 6 --rerank-top-k 12 --force --continue-on-error --output-json reports\llamaindex_expanded_retrieval_concept_v2.json --output-md reports\llamaindex_expanded_retrieval_concept_v2.md
python scripts\validate_expanded_retrieval_artifacts.py
```

The default expanded retrieval run preserves the failure case evidence for the first finance-aware reranker. The `concept_v2` run validates the improved label-free concept signals before any expanded LLM answer-generation spend.

Run expanded 25-question LlamaIndex LLM diagnostics after `concept_v2` retrieval passes:

```powershell
$env:DEEPSEEK_API_KEY="YOUR_KEY"
python scripts\run_llamaindex_expanded_llm_diagnostics.py --force --continue-on-error
python scripts\validate_expanded_llm_artifacts.py
```

This writes:

```text
reports/llamaindex_expanded_llm_diagnostics.md
reports/llamaindex_expanded_llm_diagnostics.json
reports/expanded_llm_validation_report.json
reports/llamaindex_vector_rag/qa_llm_expanded_25_concept_v2_r3/
reports/llamaindex_hybrid_rag/qa_llm_expanded_25_concept_v2_r3/
```

The aggregate report is stable by default: rerunning one method still summarizes all known expanded LLM methods if their artifacts already exist. Use `--summary-selected-only` only when a deliberately single-method report is needed.

Run LlamaIndex Vector answer-prompt ablations:

```powershell
$env:DEEPSEEK_API_KEY="YOUR_KEY"
python scripts\run_llamaindex_expanded_llm_diagnostics.py --method vector --summary-selected-only --answer-prompt-mode finance_reasoning_v2 --force --continue-on-error
python scripts\validate_expanded_llm_artifacts.py --diagnostics-json reports\llamaindex_expanded_llm_diagnostics_finance_reasoning_v2.json --required-method vector --output reports\expanded_llm_validation_report_finance_reasoning_v2.json

python scripts\run_llamaindex_expanded_llm_diagnostics.py --method vector --summary-selected-only --answer-prompt-mode finance_reasoning_v3 --force --continue-on-error
python scripts\validate_expanded_llm_artifacts.py --diagnostics-json reports\llamaindex_expanded_llm_diagnostics_finance_reasoning_v3.json --required-method vector --output reports\expanded_llm_validation_report_finance_reasoning_v3.json

python scripts\summarize_finance_prompt_variants.py
```

This writes:

```text
reports/finance_prompt_variant_summary.md
reports/finance_prompt_variant_summary.json
reports/llamaindex_expanded_llm_diagnostics_finance_reasoning_v2.md
reports/llamaindex_expanded_llm_diagnostics_finance_reasoning_v2.json
reports/llamaindex_expanded_llm_diagnostics_finance_reasoning_v3.md
reports/llamaindex_expanded_llm_diagnostics_finance_reasoning_v3.json
reports/expanded_llm_validation_report_finance_reasoning_v2.json
reports/expanded_llm_validation_report_finance_reasoning_v3.json
```

The prompt variants are answer-generation ablations. Keep the default prompt as the main cross-method baseline unless a report explicitly compares prompt modes.

Summarize expanded cost and quality across committed LlamaIndex and Long-context artifacts:

```powershell
python scripts\summarize_expanded_cost_quality.py
```

Outputs:

```text
reports/expanded_cost_quality_summary.md
reports/expanded_cost_quality_summary.json
```

Validate the lowest-context passing LLM candidates:

```powershell
$env:DEEPSEEK_API_KEY="YOUR_KEY"
python scripts\run_llamaindex_vector_rag_mvp.py --model deepseek/deepseek-v4-pro --rerank-top-k 3 --output-dir reports\llamaindex_vector_rag\qa_llm_finance_r3 --manifest reports\llamaindex_vector_rag\qa_llm_finance_r3_manifest.json --force --continue-on-error
python scripts\evaluate_evidence_mvp.py --results-dir reports\llamaindex_vector_rag\qa_llm_finance_r3 --output reports\llamaindex_vector_rag\evidence_eval_llm_finance_r3.json --continue-on-error
python scripts\evaluate_answers_mvp.py --results-dir reports\llamaindex_vector_rag\qa_llm_finance_r3 --output reports\llamaindex_vector_rag\answer_eval_llm_finance_r3.json --mode llm --model deepseek/deepseek-v4-pro --continue-on-error

python scripts\run_llamaindex_hybrid_rag_mvp.py --model deepseek/deepseek-v4-pro --rerank-top-k 3 --output-dir reports\llamaindex_hybrid_rag\qa_llm_finance_r3 --manifest reports\llamaindex_hybrid_rag\qa_llm_finance_r3_manifest.json --force --continue-on-error
python scripts\evaluate_evidence_mvp.py --results-dir reports\llamaindex_hybrid_rag\qa_llm_finance_r3 --output reports\llamaindex_hybrid_rag\evidence_eval_llm_finance_r3.json --continue-on-error
python scripts\evaluate_answers_mvp.py --results-dir reports\llamaindex_hybrid_rag\qa_llm_finance_r3 --output reports\llamaindex_hybrid_rag\answer_eval_llm_finance_r3.json --mode llm --model deepseek/deepseek-v4-pro --continue-on-error
```

## Run LlamaIndex Hybrid RAG Diagnostic Baseline

Current finance-aware smoke test without LLM answer generation:

```powershell
python scripts\run_llamaindex_hybrid_rag_mvp.py --no-llm --output-dir reports\llamaindex_hybrid_rag\qa_smoke_finance --manifest reports\llamaindex_hybrid_rag\qa_smoke_finance_manifest.json --force --continue-on-error
python scripts\evaluate_evidence_mvp.py --results-dir reports\llamaindex_hybrid_rag\qa_smoke_finance --output reports\llamaindex_hybrid_rag\evidence_eval_smoke_finance.json --continue-on-error
```

Generic reranker single-question smoke test:

```powershell
python scripts\run_llamaindex_hybrid_rag_mvp.py --no-llm --disable-finance-rerank --question-id fb_mvp_001 --output-dir reports\llamaindex_hybrid_rag\qa_smoke --manifest reports\llamaindex_hybrid_rag\qa_smoke_manifest.json --force --continue-on-error
python scripts\evaluate_evidence_mvp.py --results-dir reports\llamaindex_hybrid_rag\qa_smoke --output reports\llamaindex_hybrid_rag\evidence_eval_smoke.json --continue-on-error
```

Optional cross-encoder diagnostic:

```powershell
python scripts\run_llamaindex_hybrid_rag_mvp.py --no-llm --disable-finance-rerank --question-id fb_mvp_001 --cross-encoder-model cross-encoder/ms-marco-MiniLM-L-6-v2 --output-dir reports\llamaindex_hybrid_rag\qa_smoke_cross --manifest reports\llamaindex_hybrid_rag\qa_smoke_cross_manifest.json --force --continue-on-error
python scripts\evaluate_evidence_mvp.py --results-dir reports\llamaindex_hybrid_rag\qa_smoke_cross --output reports\llamaindex_hybrid_rag\evidence_eval_smoke_cross.json --continue-on-error
```

This is currently a diagnostic baseline. The finance-aware reranker reaches 1.000 evidence recall on the 12-question no-LLM MVP run, and the LLM diagnostic workflow records answer generation, evidence evaluation, answer judging, token usage, and latency.

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
