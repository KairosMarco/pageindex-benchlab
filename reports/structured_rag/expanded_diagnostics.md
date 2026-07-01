# Structured Tree-Graph RAG Expanded Diagnostics

## Summary

| Metric | Value |
|---|---:|
| Questions | 25 |
| Generated outputs | 25 |
| Average evidence recall | 0.740 |
| Average citation precision | 0.260 |
| Full hits | 18 |
| Partial hits | 1 |
| Misses | 6 |
| Median latency ms | 359 |
| Average latency ms | 373 |
| Median node count | 291 |

## Interpretation

This local baseline is useful as a controlled structural retrieval floor, not as a claim of superiority. It is weaker than PageIndex on the expanded FinanceBench subset, but it gives BenchLab a license-safe tree-plus-graph implementation surface while full BookRAG runtime work continues.

## Misses

| Question | Document | Recall | Gold pages | Predicted pages | Question type |
|---|---|---:|---|---|---|
| `fb_mvp_004` | `AMD_2022_10K` | 0.000 | 58 | 101, 62, 73 | domain-relevant |
| `fb_mvp_005` | `BESTBUY_2023_10K` | 0.000 | 40 | 25, 26, 27 | domain-relevant |
| `fb_mvp_008` | `MICROSOFT_2016_10K` | 0.000 | 52 | 34, 35, 33 | metrics-generated |
| `fb_mvp_012` | `JOHNSON_JOHNSON_2023_8K_dated-2023-08-30` | 0.000 | 4 | 13, 14, 12 | novel-generated |
| `fb_exp_014` | `AMERICANEXPRESS_2022_10K` | 0.000 | 96 | 118, 136, 102 | domain-relevant |
| `fb_exp_018` | `MGMRESORTS_2022Q4_EARNINGS` | 0.000 | 13 | 14, 8, 9 | novel-generated |

## Per Question

| Question | Document | Recall | Precision | Gold pages | Predicted pages | Latency ms | Nodes |
|---|---|---:|---:|---|---|---:|---:|
| `fb_mvp_001` | `3M_2018_10K` | 1.000 | 0.333 | 60 | 49, 46, 60 | 695 | 400 |
| `fb_mvp_002` | `AMAZON_2017_10K` | 1.000 | 0.333 | 38 | 44, 38, 48 | 188 | 213 |
| `fb_mvp_003` | `AMD_2022_10K` | 1.000 | 0.333 | 4 | 4, 7, 8 | 511 | 292 |
| `fb_mvp_004` | `AMD_2022_10K` | 0.000 | 0.000 | 58 | 101, 62, 73 | 408 | 292 |
| `fb_mvp_005` | `BESTBUY_2023_10K` | 0.000 | 0.000 | 40 | 25, 26, 27 | 190 | 199 |
| `fb_mvp_006` | `BOEING_2022_10K` | 1.000 | 0.333 | 113 | 19, 113, 20 | 388 | 380 |
| `fb_mvp_007` | `COSTCO_2021_10K` | 1.000 | 0.333 | 38 | 38, 51, 53 | 171 | 163 |
| `fb_mvp_008` | `MICROSOFT_2016_10K` | 0.000 | 0.000 | 52 | 34, 35, 33 | 319 | 291 |
| `fb_mvp_009` | `NIKE_2023_10K` | 1.000 | 0.333 | 62 | 69, 62, 93 | 341 | 278 |
| `fb_mvp_010` | `AMCOR_2023Q4_EARNINGS` | 1.000 | 0.333 | 12 | 11, 12, 7 | 55 | 29 |
| `fb_mvp_011` | `JPMORGAN_2023Q2_10Q` | 1.000 | 0.333 | 85 | 85, 84, 47 | 797 | 512 |
| `fb_mvp_012` | `JOHNSON_JOHNSON_2023_8K_dated-2023-08-30` | 0.000 | 0.000 | 4 | 13, 14, 12 | 195 | 43 |
| `fb_exp_013` | `ADOBE_2016_10K` | 1.000 | 0.333 | 62 | 62, 92, 95 | 359 | 278 |
| `fb_exp_014` | `AMERICANEXPRESS_2022_10K` | 0.000 | 0.000 | 96 | 118, 136, 102 | 721 | 591 |
| `fb_exp_015` | `FOOTLOCKER_2022_8K_dated-2022-05-20` | 1.000 | 0.500 | 2 | 2, 3 | 25 | 6 |
| `fb_exp_016` | `BLOCK_2016_10K` | 1.000 | 0.333 | 68 | 68, 76, 65 | 279 | 274 |
| `fb_exp_017` | `CORNING_2022_10K` | 1.000 | 0.333 | 60 | 20, 60, 104 | 405 | 335 |
| `fb_exp_018` | `MGMRESORTS_2022Q4_EARNINGS` | 0.000 | 0.000 | 13 | 14, 8, 9 | 98 | 32 |
| `fb_exp_019` | `AMERICANWATERWORKS_2020_10K` | 1.000 | 0.333 | 86 | 86, 66, 79 | 470 | 427 |
| `fb_exp_020` | `CVSHEALTH_2022_10K` | 0.500 | 0.333 | 108, 110 | 110, 118, 115 | 681 | 564 |
| `fb_exp_021` | `PEPSICO_2023Q1_EARNINGS` | 1.000 | 0.333 | 1 | 1, 3, 2 | 45 | 24 |
| `fb_exp_022` | `COCACOLA_2021_10K` | 1.000 | 0.333 | 62 | 62, 132, 47 | 1026 | 483 |
| `fb_exp_023` | `PFIZER_2021_10K` | 1.000 | 0.333 | 59 | 61, 53, 59 | 497 | 499 |
| `fb_exp_024` | `GENERALMILLS_2020_10K` | 1.000 | 0.333 | 50 | 50, 69, 103 | 421 | 311 |
| `fb_exp_025` | `ULTABEAUTY_2023Q4_EARNINGS` | 1.000 | 0.333 | 2 | 2, 6, 3 | 29 | 13 |
