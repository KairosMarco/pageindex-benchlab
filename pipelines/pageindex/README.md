# PageIndex Adapter

Target source:

- https://github.com/VectifyAI/PageIndex

Goal:

```text
PDF/document -> PageIndex tree -> reasoning retrieval -> unified benchmark output
```

First task:

- Run the official PageIndex demo.
- Document setup issues.
- Create a minimal adapter returning the shared output schema.

## First Local Demo

Status: completed.

Result artifact:

```text
examples/pageindex-demo/q1-fy25-earnings_structure.json
```

Key finding:

```text
PageIndex can generate a document tree from the example PDF using DashScope/Qwen through LiteLLM.
```

Observed upstream issue:

```text
litellm==1.83.7 requires python-dotenv==1.0.1, but upstream requirements.txt pins python-dotenv==1.2.2.
```

## Adapter

Implemented:

```text
pipelines/pageindex/adapter.py
```

Current mode:

```text
index_only
```

Example:

```powershell
python -m pipelines.pageindex.adapter examples\pageindex-demo\q1-fy25-earnings_structure.json --output reports\pageindex-demo-result.json
```

The adapter converts PageIndex tree JSON into the shared `BenchmarkResult` schema. Full question answering is the next adapter iteration.

## QA Adapter

Implemented:

```text
pipelines/pageindex/qa_adapter.py
```

Current mode:

```text
tree_page_scoring + optional LLM answer generation
```

No-LLM smoke mode:

```powershell
python pipelines\pageindex\qa_adapter.py --questions datasets\financebench\mvp_questions.jsonl --question-id fb_mvp_001 --structure reports\pageindex\structures\3M_2018_10K_structure.json --pdf datasets\raw\financebench\pdfs\3M_2018_10K.pdf --no-llm --output reports\pageindex\qa\fb_mvp_001.json
```

Batch no-LLM MVP run:

```powershell
python scripts\run_pageindex_qa_mvp.py --no-llm --force --continue-on-error
python scripts\evaluate_evidence_mvp.py --continue-on-error
```

Latest no-LLM MVP evidence result:

```text
12 / 12 results generated
Average evidence recall: 1.000
Average citation precision: 0.333
```

## Expanded Readiness

Current expanded 25-question coverage is tracked in:

```text
reports/pageindex/expanded_readiness.md
reports/pageindex/expanded_readiness.json
```

Summary:

```text
Questions: 25
Unique source documents: 24
Documents with PageIndex structures and PDFs: 24
Runnable questions with current structures: 25
Missing PageIndex structures: 0
Missing PDFs: 0
```

Current expanded retrieval-only result:

```text
Generated QA outputs: 25 / 25
Average evidence recall: 1.000
Average citation precision: 0.347
```

Run or refresh the expanded retrieval-only artifacts:

```powershell
python scripts\summarize_pageindex_expanded_readiness.py
python scripts\run_pageindex_qa_mvp.py --questions datasets\financebench\expanded_questions_25.jsonl --structure-dir reports\pageindex\structures --output-dir reports\pageindex\qa_expanded_25 --manifest reports\pageindex\qa_expanded_25_manifest.json --no-llm --force --continue-on-error
python scripts\evaluate_evidence_mvp.py --questions datasets\financebench\expanded_questions_25.jsonl --results-dir reports\pageindex\qa_expanded_25 --output reports\pageindex\evidence_eval_qa_expanded_25.json --continue-on-error
python scripts\summarize_pageindex_expanded_partial.py
python scripts\analyze_pageindex_expanded_ranking.py
```

Current expanded LLM result:

```text
Generated answers: 25 / 25
Evidence recall: 1.000
Citation precision: 0.347
Answer accuracy: 0.920
Verdicts: 23 correct, 0 partial, 2 incorrect
Average total tokens: 2,882
Average latency: 4,840 ms
```

Expanded LLM artifacts:

```text
reports/pageindex_expanded_llm_diagnostics.md
reports/pageindex_expanded_llm_diagnostics.json
reports/expanded_pageindex_llm_validation_report.json
reports/pageindex/qa_llm_expanded_25/
```

LLM mode requires a LiteLLM model string and provider API key:

```powershell
$env:DASHSCOPE_API_KEY="YOUR_NEW_KEY"
python pipelines\pageindex\qa_adapter.py --questions datasets\financebench\mvp_questions.jsonl --question-id fb_mvp_001 --structure reports\pageindex\structures\3M_2018_10K_structure.json --pdf datasets\raw\financebench\pdfs\3M_2018_10K.pdf --model dashscope/qwen3.7-plus --output reports\pageindex\qa\fb_mvp_001.json
```
