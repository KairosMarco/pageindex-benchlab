# Structured Tree-Graph RAG Expanded Diagnostics

## Summary

| Metric | Value |
|---|---:|
| Questions | 25 |
| Generated outputs | 25 |
| Average evidence recall | 0.600 |
| Average citation precision | 0.207 |
| Full hits | 15 |
| Partial hits | 0 |
| Misses | 10 |
| Median latency ms | 264 |
| Average latency ms | 310 |
| Median node count | 291 |

## Interpretation

This local baseline is useful as a controlled structural retrieval floor, not as a claim of superiority. It is weaker than PageIndex on the expanded FinanceBench subset, but it gives BenchLab a license-safe tree-plus-graph implementation surface while full BookRAG runtime work continues.

## Misses

| Question | Document | Recall | Gold pages | Predicted pages | Question type |
|---|---|---:|---|---|---|
| `fb_mvp_001` | `3M_2018_10K` | 0.000 | 60 | 46, 83, 3 | metrics-generated |
| `fb_mvp_003` | `AMD_2022_10K` | 0.000 | 4 | 10, 111, 7 | domain-relevant |
| `fb_mvp_006` | `BOEING_2022_10K` | 0.000 | 113 | 20, 112, 54 | domain-relevant |
| `fb_mvp_012` | `JOHNSON_JOHNSON_2023_8K_dated-2023-08-30` | 0.000 | 4 | 13, 14, 12 | novel-generated |
| `fb_exp_014` | `AMERICANEXPRESS_2022_10K` | 0.000 | 96 | 118, 202, 119 | domain-relevant |
| `fb_exp_017` | `CORNING_2022_10K` | 0.000 | 60 | 34, 65, 99 | domain-relevant |
| `fb_exp_018` | `MGMRESORTS_2022Q4_EARNINGS` | 0.000 | 13 | 15, 14, 8 | novel-generated |
| `fb_exp_020` | `CVSHEALTH_2022_10K` | 0.000 | 108, 110 | 199, 27, 191 | domain-relevant |
| `fb_exp_023` | `PFIZER_2021_10K` | 0.000 | 59 | 18, 21, 71 | novel-generated |
| `fb_exp_025` | `ULTABEAUTY_2023Q4_EARNINGS` | 0.000 | 2 | 6, 1, 3 | novel-generated |

## Per Question

| Question | Document | Recall | Precision | Gold pages | Predicted pages | Latency ms | Nodes |
|---|---|---:|---:|---|---|---:|---:|
| `fb_mvp_001` | `3M_2018_10K` | 0.000 | 0.000 | 60 | 46, 83, 3 | 493 | 400 |
| `fb_mvp_002` | `AMAZON_2017_10K` | 1.000 | 0.333 | 38 | 38, 44, 48 | 213 | 213 |
| `fb_mvp_003` | `AMD_2022_10K` | 0.000 | 0.000 | 4 | 10, 111, 7 | 477 | 292 |
| `fb_mvp_004` | `AMD_2022_10K` | 1.000 | 0.333 | 58 | 101, 59, 58 | 415 | 292 |
| `fb_mvp_005` | `BESTBUY_2023_10K` | 1.000 | 0.333 | 40 | 25, 27, 40 | 174 | 199 |
| `fb_mvp_006` | `BOEING_2022_10K` | 0.000 | 0.000 | 113 | 20, 112, 54 | 364 | 380 |
| `fb_mvp_007` | `COSTCO_2021_10K` | 1.000 | 0.333 | 38 | 38, 51, 53 | 156 | 163 |
| `fb_mvp_008` | `MICROSOFT_2016_10K` | 1.000 | 0.333 | 52 | 52, 33, 35 | 242 | 291 |
| `fb_mvp_009` | `NIKE_2023_10K` | 1.000 | 0.333 | 62 | 69, 62, 93 | 256 | 278 |
| `fb_mvp_010` | `AMCOR_2023Q4_EARNINGS` | 1.000 | 0.333 | 12 | 11, 7, 12 | 33 | 29 |
| `fb_mvp_011` | `JPMORGAN_2023Q2_10Q` | 1.000 | 0.333 | 85 | 85, 84, 47 | 581 | 512 |
| `fb_mvp_012` | `JOHNSON_JOHNSON_2023_8K_dated-2023-08-30` | 0.000 | 0.000 | 4 | 13, 14, 12 | 124 | 43 |
| `fb_exp_013` | `ADOBE_2016_10K` | 1.000 | 0.333 | 62 | 62, 92, 95 | 264 | 278 |
| `fb_exp_014` | `AMERICANEXPRESS_2022_10K` | 0.000 | 0.000 | 96 | 118, 202, 119 | 574 | 591 |
| `fb_exp_015` | `FOOTLOCKER_2022_8K_dated-2022-05-20` | 1.000 | 0.500 | 2 | 2, 3 | 15 | 6 |
| `fb_exp_016` | `BLOCK_2016_10K` | 1.000 | 0.333 | 68 | 68, 65, 84 | 229 | 274 |
| `fb_exp_017` | `CORNING_2022_10K` | 0.000 | 0.000 | 60 | 34, 65, 99 | 384 | 335 |
| `fb_exp_018` | `MGMRESORTS_2022Q4_EARNINGS` | 0.000 | 0.000 | 13 | 15, 14, 8 | 69 | 32 |
| `fb_exp_019` | `AMERICANWATERWORKS_2020_10K` | 1.000 | 0.333 | 86 | 86, 66, 107 | 378 | 427 |
| `fb_exp_020` | `CVSHEALTH_2022_10K` | 0.000 | 0.000 | 108, 110 | 199, 27, 191 | 581 | 564 |
| `fb_exp_021` | `PEPSICO_2023Q1_EARNINGS` | 1.000 | 0.333 | 1 | 1, 3, 10 | 34 | 24 |
| `fb_exp_022` | `COCACOLA_2021_10K` | 1.000 | 0.333 | 62 | 62, 47, 76 | 872 | 483 |
| `fb_exp_023` | `PFIZER_2021_10K` | 0.000 | 0.000 | 59 | 18, 21, 71 | 410 | 499 |
| `fb_exp_024` | `GENERALMILLS_2020_10K` | 1.000 | 0.333 | 50 | 69, 50, 100 | 385 | 311 |
| `fb_exp_025` | `ULTABEAUTY_2023Q4_EARNINGS` | 0.000 | 0.000 | 2 | 6, 1, 3 | 21 | 13 |
