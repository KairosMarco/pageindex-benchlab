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
| PageIndex tree QA | complete | 25 | 0 | 0 | 0.760 | 0.253 | 0.760 | {'correct': 19, 'partial': 1, 'incorrect': 5} | 3045.680 | 3.000 | 5786.600 | passed |

## Failure And Issue Cases

| Issue | Question | Document | Verdict/Recall | Gold pages | Predicted pages | Rationale |
|---|---|---|---:|---|---|---|
| evidence | `fb_exp_014` | `AMERICANEXPRESS_2022_10K` | 0.000 | 96 | 104, 121, 134 | The predicted answer correctly states that gross margin is not a useful metric for American Express and explains why, aligning with the gold answer that performance is not measu... |
| evidence | `fb_exp_017` | `CORNING_2022_10K` | 0.000 | 60 | 34, 16, 66 | The predicted answer correctly states that Corning has positive working capital, matching the gold answer's yes. However, it provides an incorrect specific amount ($2,278 millio... |
| evidence | `fb_exp_020` | `CVSHEALTH_2022_10K` | 0.000 | 108, 110 | 30, 32, 63 | The predicted answer states it is not possible to determine whether CVS Health is a capital-intensive business, while the gold answer gives a definitive 'Yes' supported by FY202... |
| evidence | `fb_exp_022` | `COCACOLA_2021_10K` | 0.000 | 62 | 68, 77, 85 | The predicted answer asserts that the COGS % margin cannot be calculated due to missing data, while the gold answer provides a specific value of 39.7%. This directly contradicts... |
| evidence | `fb_exp_023` | `PFIZER_2021_10K` | 0.000 | 59 | 63, 76, 10 | The gold answer states "Yes, change in PPNE was positive year over year." The predicted answer claims the question cannot be answered due to lack of data. This is materially dif... |
| evidence | `fb_exp_025` | `ULTABEAUTY_2023Q4_EARNINGS` | 0.000 | 2 | 3, 6, 9 | The predicted answer claims the document does not explain the drivers of SG&A reduction, but the gold answer provides specific drivers: lower marketing expenses and leverage of... |

| Issue | Question | Document | Verdict/Recall | Gold pages | Predicted pages | Rationale |
|---|---|---|---:|---|---|---|
| answer | `fb_exp_017` | `CORNING_2022_10K` | partial | 60 | 34, 16, 66 | The predicted answer correctly states that Corning has positive working capital, matching the gold answer's yes. However, it provides an incorrect specific amount ($2,278 millio... |
| answer | `fb_exp_019` | `AMERICANWATERWORKS_2020_10K` | incorrect | 86 | 66, 86, 93 | The gold answer is $0.40 billion, while the predicted answer gives $0.389 billion. The values are materially different (by $11 million) and do not match. |
| answer | `fb_exp_020` | `CVSHEALTH_2022_10K` | incorrect | 108, 110 | 30, 32, 63 | The predicted answer states it is not possible to determine whether CVS Health is a capital-intensive business, while the gold answer gives a definitive 'Yes' supported by FY202... |
| answer | `fb_exp_022` | `COCACOLA_2021_10K` | incorrect | 62 | 68, 77, 85 | The predicted answer asserts that the COGS % margin cannot be calculated due to missing data, while the gold answer provides a specific value of 39.7%. This directly contradicts... |
| answer | `fb_exp_023` | `PFIZER_2021_10K` | incorrect | 59 | 63, 76, 10 | The gold answer states "Yes, change in PPNE was positive year over year." The predicted answer claims the question cannot be answered due to lack of data. This is materially dif... |
| answer | `fb_exp_025` | `ULTABEAUTY_2023Q4_EARNINGS` | incorrect | 2 | 3, 6, 9 | The predicted answer claims the document does not explain the drivers of SG&A reduction, but the gold answer provides specific drivers: lower marketing expenses and leverage of... |

## Per-question Diagnostics

| Question | Document | Evidence recall | Citation precision | Verdict | Total tokens | Citations | Latency ms |
|---|---|---:|---:|---|---:|---:|---:|
| `fb_exp_013` | `ADOBE_2016_10K` | 1.000 | 0.333 | correct | 2775 | 3 | 5616 |
| `fb_exp_014` | `AMERICANEXPRESS_2022_10K` | 0.000 | 0.000 | correct | 3025 | 3 | 7108 |
| `fb_exp_015` | `FOOTLOCKER_2022_8K_dated-2022-05-20` | 1.000 | 0.333 | correct | 2176 | 3 | 3635 |
| `fb_exp_016` | `BLOCK_2016_10K` | 1.000 | 0.333 | correct | 4299 | 3 | 6954 |
| `fb_exp_017` | `CORNING_2022_10K` | 0.000 | 0.000 | partial | 2794 | 3 | 5123 |
| `fb_exp_018` | `MGMRESORTS_2022Q4_EARNINGS` | 1.000 | 0.333 | correct | 3153 | 3 | 5348 |
| `fb_exp_019` | `AMERICANWATERWORKS_2020_10K` | 1.000 | 0.333 | incorrect | 3031 | 3 | 4371 |
| `fb_exp_020` | `CVSHEALTH_2022_10K` | 0.000 | 0.000 | incorrect | 3721 | 3 | 7750 |
| `fb_exp_021` | `PEPSICO_2023Q1_EARNINGS` | 1.000 | 0.333 | correct | 2116 | 3 | 4344 |
| `fb_exp_022` | `COCACOLA_2021_10K` | 0.000 | 0.000 | incorrect | 3332 | 3 | 6231 |
| `fb_exp_023` | `PFIZER_2021_10K` | 0.000 | 0.000 | incorrect | 4459 | 3 | 5146 |
| `fb_exp_024` | `GENERALMILLS_2020_10K` | 1.000 | 0.333 | correct | 3191 | 3 | 5927 |
| `fb_exp_025` | `ULTABEAUTY_2023Q4_EARNINGS` | 0.000 | 0.000 | incorrect | 2430 | 3 | 7268 |
| `fb_mvp_001` | `3M_2018_10K` | 1.000 | 0.333 | correct | 2964 | 3 | 5450 |
| `fb_mvp_002` | `AMAZON_2017_10K` | 1.000 | 0.333 | correct | 3081 | 3 | 5414 |
| `fb_mvp_003` | `AMD_2022_10K` | 1.000 | 0.333 | correct | 3354 | 3 | 8791 |
| `fb_mvp_004` | `AMD_2022_10K` | 1.000 | 0.333 | correct | 2085 | 3 | 5208 |
| `fb_mvp_005` | `BESTBUY_2023_10K` | 1.000 | 0.333 | correct | 3720 | 3 | 12427 |
| `fb_mvp_006` | `BOEING_2022_10K` | 1.000 | 0.333 | correct | 2407 | 3 | 7006 |
| `fb_mvp_007` | `COSTCO_2021_10K` | 1.000 | 0.333 | correct | 2277 | 3 | 3444 |
| `fb_mvp_008` | `MICROSOFT_2016_10K` | 1.000 | 0.333 | correct | 2341 | 3 | 3256 |
| `fb_mvp_009` | `NIKE_2023_10K` | 1.000 | 0.333 | correct | 2925 | 3 | 5142 |
| `fb_mvp_010` | `AMCOR_2023Q4_EARNINGS` | 1.000 | 0.333 | correct | 3992 | 3 | 5721 |
| `fb_mvp_011` | `JPMORGAN_2023Q2_10Q` | 1.000 | 0.333 | correct | 4171 | 3 | 4316 |
| `fb_mvp_012` | `JOHNSON_JOHNSON_2023_8K_dated-2023-08-30` | 1.000 | 0.333 | correct | 2323 | 3 | 3669 |

## Interpretation

- PageIndex completed the mechanical artifact gate for the expanded subset.
- PageIndex used a small three-page answer context, but retrieval misses limited answer accuracy on this expanded subset.
- The answer issues largely overlap with evidence misses, so improving PageIndex ranking is more important than prompt tuning at this point.
- These results should be reported conservatively: PageIndex remains strong on the 12-question MVP set, but the 25-question set exposes ranking gaps.

## Artifacts

- Results: `reports\pageindex\qa_llm_expanded_25`
- Manifest: `reports\pageindex\qa_llm_expanded_25_manifest.json`
- Evidence eval: `reports\pageindex\evidence_eval_qa_llm_expanded_25.json`
- Answer eval: `reports\pageindex\answer_eval_qa_llm_expanded_25.json`
