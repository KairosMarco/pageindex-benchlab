# Upstream PageIndex Issue Draft: FinanceBench Benchmark And Expanded QA Plan

Target repository:

```text
https://github.com/VectifyAI/PageIndex
```

Suggested issue title:

```text
Benchmark plan: PageIndex vs long-context and RAG baselines on FinanceBench evidence QA
```

## Summary

I am building an open benchmark workspace to evaluate PageIndex against long-context LLMs, Vector RAG, Hybrid RAG, GraphRAG, and HyperGraphRAG on structured long-document QA.

The benchmark does not assume PageIndex is better. It asks a narrower question:

```text
On structured long documents such as SEC filings, can PageIndex retrieve the right evidence pages, produce precise citations, and provide an explainable retrieval path compared with strong baselines?
```

Current benchmark repository:

```text
https://github.com/KairosMarco/pageindex-benchlab
```

## Current Local PageIndex Result

PageIndex has been run on a 12-question FinanceBench MVP subset.

```text
Questions: 12
PageIndex structures: 11 unique source documents
Mode: tree-page scoring + LLM answer generation
Model: deepseek/deepseek-v4-pro
Evidence recall: 1.000
Citation precision: 0.333
Answer accuracy: 1.000
Average total tokens per answer: 2,984
```

Relevant artifacts:

```text
reports/pageindex/qa_llm/
reports/pageindex/qa_llm_manifest.json
reports/pageindex/evidence_eval_llm.json
reports/pageindex/answer_eval_llm.json
reports/stage1_detailed_evidence_report.md
reports/stage1_validation_report.json
```

## Strong Baseline Results

The same workspace also runs stronger baselines.

Expanded 25-question FinanceBench subset:

```text
datasets/financebench/expanded_questions_25.jsonl
```

LlamaIndex Vector RAG with finance-aware reranking:

```text
Questions: 25
Evidence recall: 1.000
Citation precision: 0.360
Answer accuracy: 0.920
Average total tokens: 2,543
```

LlamaIndex Hybrid RAG with finance-aware reranking:

```text
Questions: 25
Evidence recall: 1.000
Citation precision: 0.360
Answer accuracy: 0.880
Average total tokens: 2,553
```

Long-context LLM:

```text
Questions: 25
Evidence recall: 0.800
Citation precision: 0.267
Answer accuracy: 0.920
Average total tokens: 92,500
```

PageIndex tree QA:

```text
Questions: 25
Evidence recall: 1.000
Citation precision: 0.347
Answer accuracy: 0.920
Average total tokens: 2,882
```

Key interpretation:

- Long-context used about `36x` more average tokens than LlamaIndex Vector on the expanded subset.
- The strongest LlamaIndex candidate and the current PageIndex scorer both reached perfect page-level evidence recall on this subset, so remaining failures are mostly answer-generation or judge-strictness issues rather than retrieval misses.
- PageIndex used compact three-page answer contexts; its current result is competitive on this small finance subset after ranking diagnostics and finance line-item scoring.
- A shared hard case was `fb_exp_020`, a capital-intensity question where several methods had access to the relevant pages but interpreted the finance concept incorrectly.

## Prompt-Ablation Finding

I also tested stricter finance-reasoning answer prompts for LlamaIndex Vector RAG.

```text
Default prompt:
answer accuracy: 0.920
verdicts: 23 correct, 1 partial, 1 incorrect
average total tokens: 2,543

finance_reasoning_v2:
answer accuracy: 0.960
verdicts: 24 correct, 0 partial, 1 incorrect
average total tokens: 2,885

finance_reasoning_v3:
answer accuracy: 0.920
verdicts: 23 correct, 2 partial, 0 incorrect
average total tokens: 2,978
```

Interpretation:

Stronger prompts can fix some concept-heavy finance reasoning failures, but they also trade one failure mode for another. This is useful as an answer-generation ablation, but not a substitute for robust retrieval and citation evaluation.

Artifacts:

```text
reports/finance_prompt_variant_summary.md
reports/finance_prompt_variant_summary.json
```

## Current PageIndex Expanded Result

PageIndex expanded QA is now mechanically complete for the 25-question subset.

```text
Expanded questions: 25
Unique documents: 24
Documents with PageIndex structures and PDFs: 24
Missing PageIndex structures: 0
Missing PDFs: 0
Runnable questions with current structures: 25
Retrieval-only QA generated: 25
Retrieval-only evidence recall: 1.000
Retrieval-only citation precision: 0.347
LLM answers generated: 25
LLM answer accuracy: 0.920
LLM verdicts: 23 correct, 0 partial, 2 incorrect
```

Artifacts:

```text
reports/pageindex/expanded_readiness.md
reports/pageindex/expanded_readiness.json
reports/pageindex/expanded_indexing_notes.md
reports/pageindex/expanded_partial_summary.md
reports/pageindex/evidence_eval_qa_expanded_25.json
reports/pageindex/pageindex_ranking_diagnostics.md
reports/pageindex_expanded_llm_diagnostics.md
reports/expanded_pageindex_llm_validation_report.json
```

The legacy PageIndex scorer surfaced six retrieval misses: `fb_exp_014`, `fb_exp_017`, `fb_exp_020`, `fb_exp_022`, `fb_exp_023`, and `fb_exp_025`. The current label-free finance line-item scorer fixes those misses without using gold evidence during retrieval. The expanded run also surfaced indexing robustness issues on long SEC filings, including model-produced TOC JSON with unexpected object/list shapes, missing page-offset values, low-confidence no-TOC processing failures, and missing `physical_index` fields.

## Proposed Next Work

I would like to use this benchmark to contribute small, reviewable improvements upstream.

Possible PageIndex contributions:

- Document a Windows quickstart and provider-key setup path.
- Add or document robust JSON parsing for LLM responses that include fenced JSON, explanatory text, or missing fields.
- Add defensive handling when TOC extraction returns objects instead of lists, or when page-offset detection returns null.
- Add benchmark reproduction notes for FinanceBench-style page-evidence QA.
- Add or document PageIndex ranking diagnostics that compare legacy and current page scoring on evidence-page recall.
- Add a minimal script or documentation example showing how to run PageIndex over a local PDF and inspect the produced structure.

## Why This Helps PageIndex

This gives PageIndex a reproducible comparison against strong baselines instead of only a demo-level evaluation. It also identifies the exact place where PageIndex may provide value:

- evidence-page recall
- citation precision
- explainable tree/path retrieval
- lower answer context than full long-context prompting

The benchmark is intentionally conservative: the expanded run is complete and PageIndex is competitive on this small finance subset, but it does not support broad PageIndex superiority claims yet. The current useful contribution target is upstreaming indexing robustness, ranking diagnostics, and reproducible benchmark notes.
