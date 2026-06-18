# PageIndex Expanded LLM Diagnostics

Date: 2026-06-18

## Scope

This report summarizes PageIndex answer generation on the expanded 25-question FinanceBench subset.

- Question file: `datasets\financebench\expanded_questions_25.jsonl`
- Question count: `25`
- Model: `deepseek/deepseek-v4-pro`

## Summary

| Method | Status | Questions | Gen failures | Eval failures | Evidence recall | Citation precision | Answer accuracy | Verdicts | Avg total tokens | Avg citations | Avg latency ms | Gate |
|---|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|---|
| PageIndex tree QA | complete | 25 | 0 | 0 | 1.000 | 0.347 | 0.920 | {'correct': 23, 'partial': 0, 'incorrect': 2} | 2882.160 | 3.000 | 4839.600 | passed |

## Failure And Issue Cases

| Issue | Question | Document | Verdict/Recall | Gold pages | Predicted pages | Rationale |
|---|---|---|---:|---|---|---|
| answer | `fb_exp_019` | `AMERICANWATERWORKS_2020_10K` | incorrect | 86 | 86, 66, 93 | The predicted answer states $0.389 billion, which does not match the gold answer of $0.40 billion. The difference is material and not a rounding discrepancy from the provided go... |
| answer | `fb_exp_020` | `CVSHEALTH_2022_10K` | incorrect | 108, 110 | 110, 133, 108 | The gold answer says 'Yes, CVS Health is a capital-intensive business', while the predicted answer says 'No, CVS Health does not appear to be a capital-intensive business.' Thes... |

## Per-question Diagnostics

| Question | Document | Evidence recall | Citation precision | Verdict | Total tokens | Citations | Latency ms |
|---|---|---:|---:|---|---:|---:|---:|
| `fb_exp_013` | `ADOBE_2016_10K` | 1.000 | 0.333 | correct | 2580 | 3 | 3833 |
| `fb_exp_014` | `AMERICANEXPRESS_2022_10K` | 1.000 | 0.333 | correct | 2971 | 3 | 8200 |
| `fb_exp_015` | `FOOTLOCKER_2022_8K_dated-2022-05-20` | 1.000 | 0.333 | correct | 2282 | 3 | 4469 |
| `fb_exp_016` | `BLOCK_2016_10K` | 1.000 | 0.333 | correct | 4171 | 3 | 4300 |
| `fb_exp_017` | `CORNING_2022_10K` | 1.000 | 0.333 | correct | 2798 | 3 | 5002 |
| `fb_exp_018` | `MGMRESORTS_2022Q4_EARNINGS` | 1.000 | 0.333 | correct | 3030 | 3 | 3698 |
| `fb_exp_019` | `AMERICANWATERWORKS_2020_10K` | 1.000 | 0.333 | incorrect | 3059 | 3 | 4261 |
| `fb_exp_020` | `CVSHEALTH_2022_10K` | 1.000 | 0.667 | incorrect | 2675 | 3 | 6969 |
| `fb_exp_021` | `PEPSICO_2023Q1_EARNINGS` | 1.000 | 0.333 | correct | 2125 | 3 | 3783 |
| `fb_exp_022` | `COCACOLA_2021_10K` | 1.000 | 0.333 | correct | 2490 | 3 | 7019 |
| `fb_exp_023` | `PFIZER_2021_10K` | 1.000 | 0.333 | correct | 3350 | 3 | 3951 |
| `fb_exp_024` | `GENERALMILLS_2020_10K` | 1.000 | 0.333 | correct | 2951 | 3 | 4279 |
| `fb_exp_025` | `ULTABEAUTY_2023Q4_EARNINGS` | 1.000 | 0.333 | correct | 2873 | 3 | 4789 |
| `fb_mvp_001` | `3M_2018_10K` | 1.000 | 0.333 | correct | 3144 | 3 | 4694 |
| `fb_mvp_002` | `AMAZON_2017_10K` | 1.000 | 0.333 | correct | 3043 | 3 | 4384 |
| `fb_mvp_003` | `AMD_2022_10K` | 1.000 | 0.333 | correct | 3411 | 3 | 6576 |
| `fb_mvp_004` | `AMD_2022_10K` | 1.000 | 0.333 | correct | 1923 | 3 | 3893 |
| `fb_mvp_005` | `BESTBUY_2023_10K` | 1.000 | 0.333 | correct | 3043 | 3 | 8079 |
| `fb_mvp_006` | `BOEING_2022_10K` | 1.000 | 0.333 | correct | 2336 | 3 | 5406 |
| `fb_mvp_007` | `COSTCO_2021_10K` | 1.000 | 0.333 | correct | 1999 | 3 | 4470 |
| `fb_mvp_008` | `MICROSOFT_2016_10K` | 1.000 | 0.333 | correct | 2356 | 3 | 3185 |
| `fb_mvp_009` | `NIKE_2023_10K` | 1.000 | 0.333 | correct | 2807 | 3 | 3485 |
| `fb_mvp_010` | `AMCOR_2023Q4_EARNINGS` | 1.000 | 0.333 | correct | 3876 | 3 | 3685 |
| `fb_mvp_011` | `JPMORGAN_2023Q2_10Q` | 1.000 | 0.333 | correct | 3730 | 3 | 5421 |
| `fb_mvp_012` | `JOHNSON_JOHNSON_2023_8K_dated-2023-08-30` | 1.000 | 0.333 | correct | 3031 | 3 | 3159 |

## Interpretation

- PageIndex completed the mechanical artifact gate for the expanded subset.
- PageIndex retrieved all gold evidence pages in the top three selected pages for this 25-question subset.
- PageIndex used a compact three-page answer context; the remaining answer issues are answer-reasoning or judge-strictness cases after successful evidence retrieval.
- Non-correct answer cases: `fb_exp_019, fb_exp_020`.
- These results should be reported conservatively: the expanded subset is still small, and stronger claims need larger datasets plus non-finance domains.

## Artifacts

- Results: `reports\pageindex\qa_llm_expanded_25`
- Manifest: `reports\pageindex\qa_llm_expanded_25_manifest.json`
- Evidence eval: `reports\pageindex\evidence_eval_qa_llm_expanded_25.json`
- Answer eval: `reports\pageindex\answer_eval_qa_llm_expanded_25.json`
