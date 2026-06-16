# Stage 1 Detailed Evidence Report

Date: 2026-06-16

## Purpose

This report documents the current Stage 1 FinanceBench MVP experiment with enough detail to support or reject benchmark claims. It is generated from committed JSON artifacts rather than manually edited conclusions.

## Test Protocol

- Dataset: 12-question FinanceBench MVP subset in `datasets/financebench/mvp_questions.jsonl`.
- Documents: 11 unique SEC filing or earnings PDFs, stored locally under ignored `datasets/raw/financebench/pdfs/`.
- LLM answer model: `deepseek/deepseek-v4-pro` for all answer-generating runs.
- LLM judge model: `deepseek/deepseek-v4-pro` for answer accuracy evaluation.
- Evidence metric: page-level recall and citation precision against FinanceBench gold evidence pages.
- Citation convention: predicted citation pages are one-indexed; FinanceBench gold pages are also stored as one-indexed and zero-indexed in the normalized dataset.
- Raw artifacts: method-level result JSON files under `reports/<method>/qa_llm/`, evidence eval JSON, and answer eval JSON.

## Method Summary

| Method | Questions | Evidence recall | Citation precision | Answer accuracy | Avg total tokens | Total tokens | Avg latency ms | Incorrect answers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| PageIndex | 12 | 1.000 | 0.333 | 1.000 | 2984.250 | 35811 | 7156.750 | 0 |
| Long-context | 12 | 0.917 | 0.306 | 1.000 | 84843.083 | 1018117 | 14938.500 | 0 |
| Vector RAG + reranker | 12 | 1.000 | 0.333 | 0.917 | 2298.750 | 27585 | 7381.750 | 1 |
| Hybrid RAG | 12 | 1.000 | 0.333 | 1.000 | 2412.500 | 28950 | 10130.667 | 0 |

## Claims Supported By Current Data

- PageIndex, Vector RAG, and Hybrid RAG all reached 1.000 page-level evidence recall on the 12-question MVP subset.
- Long-context reached 1.000 LLM-judge answer accuracy, but used 28.4x PageIndex's average total tokens in this run.
- Vector RAG had one answer-generation failure despite 1.000 evidence recall, showing that retrieval success does not guarantee final answer correctness.
- Hybrid RAG matched PageIndex's current answer accuracy and evidence recall, while using fewer average tokens (2412 vs 2984).
- PageIndex currently has lower average latency than Hybrid RAG in this MVP run (7157 ms vs 10131 ms).
- Vector RAG used the fewest average tokens, but its answer accuracy was lower (0.917) because of `fb_mvp_006`.

## Claims Not Yet Supported

- The current 12-question MVP is too small to prove broad benchmark superiority; it only validates wiring and early failure modes.
- It cannot prove general superiority across FinanceBench, legal contracts, medical documents, or all long documents.
- It cannot yet isolate retrieval quality from answer-generation quality, because the same LLM is used after retrieval.
- It cannot yet estimate real production cost, because provider pricing and account-level discounts are not recorded.
- It cannot yet evaluate GraphRAG or HyperGraphRAG, because those adapters have not been run on the same questions.

## Failure And Risk Cases

| Question | Method | Evidence recall | Answer verdict | Key rationale |
|---|---|---:|---|---|
| fb_mvp_005 | Long-context | 0.000 | correct | The predicted answer directly confirms that gross margins are historically consistent with fluctuations less than 2% each year, and specifically highlights the 1.1% decline betw... |
| fb_mvp_006 | Vector RAG + reranker | 1.000 | incorrect | The gold answer states that Boeing has reported materially important ongoing legal battles (yes). The predicted answer acknowledges the litigation but states that Boeing does no... |

## Per-question Evidence Matrix

Each cell format is `answer verdict; R=evidence recall; P=citation precision; tok=total tokens; ms=latency`.

| Question | Company | Type | Gold pages | PageIndex | Long-context | Vector RAG | Hybrid RAG |
|---|---|---|---|---|---|---|---|
| fb_mvp_001 | 3M | Information extraction | 60 | correct; R=1.000; P=0.333; tok=2940; ms=6420 | correct; R=1.000; P=0.333; tok=139605; ms=20845 | correct; R=1.000; P=0.333; tok=2333; ms=6048 | correct; R=1.000; P=0.333; tok=2347; ms=7188 |
| fb_mvp_002 | Amazon | Numerical reasoning | 38 | correct; R=1.000; P=0.333; tok=3114; ms=6946 | correct; R=1.000; P=0.333; tok=65303; ms=16003 | correct; R=1.000; P=0.333; tok=2477; ms=7410 | correct; R=1.000; P=0.333; tok=2609; ms=10494 |
| fb_mvp_003 | AMD | Information extraction | 4 | correct; R=1.000; P=0.333; tok=3426; ms=11469 | correct; R=1.000; P=0.333; tok=89165; ms=19247 | correct; R=1.000; P=0.333; tok=2199; ms=9314 | correct; R=1.000; P=0.333; tok=2659; ms=15477 |
| fb_mvp_004 | AMD | Numerical reasoning | 58 | correct; R=1.000; P=0.333; tok=2120; ms=6104 | correct; R=1.000; P=0.333; tok=88781; ms=13380 | correct; R=1.000; P=0.333; tok=2378; ms=7845 | correct; R=1.000; P=0.333; tok=2515; ms=9895 |
| fb_mvp_005 | Best Buy | Logical reasoning (based on numerical reasoning) OR Logical reasoning | 40 | correct; R=1.000; P=0.333; tok=3690; ms=11601 | correct; R=0.000; P=0.000; tok=68485; ms=16568 | correct; R=1.000; P=0.333; tok=2595; ms=10731 | correct; R=1.000; P=0.333; tok=2510; ms=13465 |
| fb_mvp_006 | Boeing | Information extraction | 113 | correct; R=1.000; P=0.333; tok=2518; ms=12005 | correct; R=1.000; P=0.333; tok=114591; ms=22328 | incorrect; R=1.000; P=0.333; tok=2230; ms=11254 | correct; R=1.000; P=0.333; tok=2925; ms=21967 |
| fb_mvp_007 | Costco | Information extraction | 38 | correct; R=1.000; P=0.333; tok=2327; ms=5046 | correct; R=1.000; P=0.333; tok=49231; ms=7114 | correct; R=1.000; P=0.333; tok=2531; ms=6207 | correct; R=1.000; P=0.333; tok=2415; ms=7964 |
| fb_mvp_008 | Microsoft | Information extraction | 52 | correct; R=1.000; P=0.333; tok=2339; ms=4587 | correct; R=1.000; P=0.333; tok=90803; ms=10856 | correct; R=1.000; P=0.333; tok=2030; ms=4899 | correct; R=1.000; P=0.333; tok=2116; ms=5835 |
| fb_mvp_009 | Nike | Numerical reasoning | 62 | correct; R=1.000; P=0.333; tok=2850; ms=6034 | correct; R=1.000; P=0.333; tok=83642; ms=12006 | correct; R=1.000; P=0.333; tok=2229; ms=5604 | correct; R=1.000; P=0.333; tok=2306; ms=7318 |
| fb_mvp_010 | Amcor | novel-generated | 12 | correct; R=1.000; P=0.333; tok=3982; ms=5928 | correct; R=1.000; P=0.333; tok=11613; ms=8325 | correct; R=1.000; P=0.333; tok=2668; ms=7132 | correct; R=1.000; P=0.333; tok=2581; ms=7516 |
| fb_mvp_011 | JPMorgan | novel-generated | 85 | correct; R=1.000; P=0.333; tok=4222; ms=5659 | correct; R=1.000; P=0.333; tok=199629; ms=28837 | correct; R=1.000; P=0.333; tok=2001; ms=7031 | correct; R=1.000; P=0.333; tok=2062; ms=8823 |
| fb_mvp_012 | Johnson & Johnson | novel-generated | 4 | correct; R=1.000; P=0.333; tok=2283; ms=4082 | correct; R=1.000; P=0.333; tok=17269; ms=3753 | correct; R=1.000; P=0.333; tok=1914; ms=5106 | correct; R=1.000; P=0.333; tok=1905; ms=5626 |

## Reproducibility Artifacts

- Machine-readable report: `reports\stage1_detailed_evidence_report.json`
- Per-question CSV: `reports\stage1_per_question_results.csv`
- Aggregate metrics: `reports/stage1_metrics_summary.json` and `reports/stage1_metrics_summary.md`
- Retrieval comparison: `reports/stage1_retrieval_comparison.md`

## Next Required Tests

1. Run a larger FinanceBench subset so the comparison is not dominated by 12 hand-picked MVP examples.
2. Replace dependency-light TF-IDF Vector/Hybrid MVPs with embedding-based LlamaIndex baselines and a stronger reranker.
3. Add answer-evidence consistency checks so the benchmark can detect cases where the right page is retrieved but the final answer misuses the evidence.
4. Record provider pricing assumptions separately before making cost claims.
5. Add GraphRAG and HyperGraphRAG only after the larger question subset and stronger Vector/Hybrid baselines are stable.
