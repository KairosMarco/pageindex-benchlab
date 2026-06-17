# Long-context Expanded LLM Diagnostics

Date: 2026-06-17

## Scope

This report runs the full-document Long-context LLM baseline on the expanded FinanceBench subset.

- Question file: `datasets\financebench\expanded_questions_25.jsonl`
- Question count: `25`
- Model: `deepseek/deepseek-v4-pro`
- Max document chars: `None`

## Summary

| Method | Status | Questions | Gen failures | Eval failures | Evidence recall | Citation precision | Answer accuracy | Avg total tokens | Avg context chars | Avg context pages | Avg latency ms | Gate |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Long-context LLM | complete | 25 | 0 | 0 | 0.800 | 0.267 | 0.920 | 92499.560 | 397912.520 | 113.080 | 12772.160 | passed |

## LlamaIndex Comparison Context

These rows are copied from the committed expanded LlamaIndex diagnostics for quick comparison on the same 25-question subset.

| Method | Questions | Evidence recall | Citation precision | Answer accuracy | Avg total tokens | Avg latency ms |
|---|---:|---:|---:|---:|---:|---:|
| LlamaIndex Vector RAG + finance concept_v2 rerank | 25 | 1.000 | 0.360 | 0.920 | 2543.200 | 16497.160 |
| LlamaIndex Hybrid RAG + finance concept_v2 rerank | 25 | 1.000 | 0.360 | 0.880 | 2553.440 | 16846.440 |

## Failure And Issue Cases

| Issue | Question | Verdict/Recall | Gold pages | Predicted pages | Rationale |
|---|---|---:|---|---|---|
| evidence | `fb_exp_014` | 0.000 | 96 | 40, 44, 104 | The predicted answer correctly states that gross margin is not a useful metric for American Express and explains why, which matches the gold answer's indication that performance... |
| evidence | `fb_exp_017` | 0.000 | 60 | 34, 118, 150 | The question asked whether Corning has positive working capital based on FY2022 data. The predicted answer correctly states 'Yes' which matches the gold answer's affirmative con... |
| evidence | `fb_exp_020` | 0.000 | 108, 110 | 75, 87, 147 | The predicted answer directly contradicts the gold answer. The gold answer states that CVS Health is a capital-intensive business based on FY2022 data, while the predicted answe... |
| evidence | `fb_exp_023` | 0.000 | 59 | 53, 63, 76 | The predicted answer correctly confirms that PPNE grew from FY20 to FY21 with specific figures, fully matching the gold answer's statement that the change was positive year over... |
| evidence | `fb_mvp_005` | 0.000 | 40 | 25, 23, 31 | The predicted answer states margins are historically consistent within 2%, gives specific yearly figures, mentions the 1.1% fluctuation, and confirms gross margin is a relevant... |

| Issue | Question | Verdict/Recall | Gold pages | Predicted pages | Rationale |
|---|---|---:|---|---|---|
| answer | `fb_exp_020` | incorrect | 108, 110 | 75, 87, 147 | The predicted answer directly contradicts the gold answer. The gold answer states that CVS Health is a capital-intensive business based on FY2022 data, while the predicted answe... |
| answer | `fb_mvp_003` | partial | 4 | 4, 60, 7 | The predicted answer covers all major product categories listed in the gold answer but adds an extra item (sales or licenses of IP portfolio) not present in the gold answer, mak... |

## Per-question Diagnostics

| Question | Evidence recall | Citation precision | Verdict | Total tokens | Context chars | Context pages | Latency ms |
|---|---:|---:|---|---:|---:|---:|---:|
| `fb_exp_013` | 1.000 | 0.333 | correct | 90297 | 414947 | 112 | 13387 |
| `fb_exp_014` | 0.000 | 0.000 | correct | 179910 | 824956 | 260 | 15791 |
| `fb_exp_015` | 1.000 | 0.333 | correct | 2512 | 6757 | 4 | 7018 |
| `fb_exp_016` | 1.000 | 0.333 | correct | 145382 | 381246 | 121 | 11811 |
| `fb_exp_017` | 0.000 | 0.000 | correct | 115123 | 500253 | 159 | 15921 |
| `fb_exp_018` | 1.000 | 0.333 | correct | 13056 | 48964 | 15 | 7970 |
| `fb_exp_019` | 1.000 | 0.333 | correct | 140258 | 623348 | 152 | 24565 |
| `fb_exp_020` | 0.000 | 0.000 | incorrect | 182157 | 856198 | 213 | 51233 |
| `fb_exp_021` | 1.000 | 0.333 | correct | 10057 | 36970 | 16 | 6785 |
| `fb_exp_022` | 1.000 | 0.333 | correct | 151723 | 695166 | 183 | 20901 |
| `fb_exp_023` | 0.000 | 0.000 | correct | 154250 | 695505 | 143 | 20934 |
| `fb_exp_024` | 1.000 | 0.333 | correct | 103237 | 436722 | 127 | 14395 |
| `fb_exp_025` | 1.000 | 0.333 | correct | 6366 | 20570 | 9 | 11782 |
| `fb_mvp_001` | 1.000 | 0.333 | correct | 139541 | 609374 | 160 | 8037 |
| `fb_mvp_002` | 1.000 | 0.333 | correct | 65016 | 293108 | 85 | 6113 |
| `fb_mvp_003` | 1.000 | 0.333 | partial | 88983 | 413749 | 121 | 9314 |
| `fb_mvp_004` | 1.000 | 0.333 | correct | 88785 | 413749 | 121 | 6888 |
| `fb_mvp_005` | 0.000 | 0.000 | correct | 68251 | 305877 | 75 | 8727 |
| `fb_mvp_006` | 1.000 | 0.333 | correct | 115136 | 510162 | 190 | 18361 |
| `fb_mvp_007` | 1.000 | 0.333 | correct | 49243 | 222279 | 76 | 3951 |
| `fb_mvp_008` | 1.000 | 0.333 | correct | 90915 | 413444 | 121 | 5926 |
| `fb_mvp_009` | 1.000 | 0.333 | correct | 83675 | 376926 | 106 | 6723 |
| `fb_mvp_010` | 1.000 | 0.333 | correct | 11560 | 44932 | 14 | 5465 |
| `fb_mvp_011` | 1.000 | 0.333 | correct | 199735 | 745545 | 217 | 12630 |
| `fb_mvp_012` | 1.000 | 0.333 | correct | 17321 | 57066 | 27 | 4676 |

## Interpretation

- The Long-context baseline completed the mechanical artifact gate for the expanded subset.
- Compare answer accuracy against token and latency cost. This baseline sends full document context, so it should be treated as a strong but expensive reference point.
- Evidence recall depends on the model's cited pages and the lexical fallback citations, not on a retrieval prefilter.
- Any answer issue rows above are answer-generation or judge-strictness findings, not retrieval-only failures.

## Artifacts

- Results: `reports\long_context\qa_llm_expanded_25`
- Manifest: `reports\long_context\qa_llm_expanded_25_manifest.json`
- Evidence eval: `reports\long_context\evidence_eval_qa_llm_expanded_25.json`
- Answer eval: `reports\long_context\answer_eval_qa_llm_expanded_25.json`
