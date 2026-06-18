# PageIndex Expanded Ranking Diagnostics

Date: 2026-06-18

## Scope

This report diagnoses PageIndex page ranking on the expanded 25-question FinanceBench subset. It does not call an LLM and does not use gold evidence during scoring.

## Summary

| Method | Questions | Full hit count | Zero hit count | Evidence recall | Citation precision |
|---|---:|---:|---:|---:|---:|
| Legacy PageIndex scorer | 25 | 19 | 6 | 0.760 | 0.253 |
| Current scorer + finance line-item boost | 25 | 25 | 0 | 1.000 | 0.347 |

## Baseline Miss Diagnostics

| Question | Document | Gold pages | Baseline top pages | Baseline gold rank | Candidate top pages | Candidate gold rank |
|---|---|---|---|---|---|---|
| `fb_exp_014` | `AMERICANEXPRESS_2022_10K` | 96 | p104:6.0, p121:6.0, p134:6.0, p135:6.0, p190:6.0 | p96: unranked | p47:53.0, p96:50.0, p136:49.9, p103:42.0, p95:38.0 | p96: r2, s50.0 |
| `fb_exp_017` | `CORNING_2022_10K` | 60 | p34:13.0, p16:9.0, p66:9.0, p1:6.0, p2:6.0 | p60: r48, s3.0 | p60:73.0, p20:29.1, p93:24.0, p104:22.6, p34:17.9 | p60: r1, s73.0 |
| `fb_exp_020` | `CVSHEALTH_2022_10K` | 108, 110 | p30:12.0, p32:12.0, p63:12.0, p14:9.0, p25:9.0 | p108: r168, s2.0; p110: r135, s3.0 | p110:67.0, p133:57.8, p108:56.0, p117:55.0, p169:54.0 | p108: r3, s56.0; p110: r1, s67.0 |
| `fb_exp_022` | `COCACOLA_2021_10K` | 62 | p68:27.0, p77:20.0, p85:20.0, p42:19.0, p49:19.0 | p62: r14, s14.0 | p68:45.1, p62:38.0, p101:37.0, p95:36.0, p128:32.6 | p62: r2, s38.0 |
| `fb_exp_023` | `PFIZER_2021_10K` | 59 | p63:9.0, p76:9.0, p10:6.0, p16:6.0, p17:6.0 | p59: unranked | p59:68.0, p72:37.0, p61:34.0, p80:34.0, p88:34.0 | p59: r1, s68.0 |
| `fb_exp_025` | `ULTABEAUTY_2023Q4_EARNINGS` | 2 | p3:9.0, p6:9.0, p9:8.0, p1:6.0, p2:6.0 | p2: r5, s6.0 | p2:56.0, p1:44.0, p6:17.0, p3:16.4, p9:15.8 | p2: r1, s56.0 |

## Candidate Improvements

| Question | Baseline recall | Candidate recall | Gold pages | Candidate predicted pages | Finance reasons on gold pages |
|---|---:|---:|---|---|---|
| `fb_exp_014` | 0.000 | 1.000 | 96 | 47, 96, 136 | p96: table_like_numeric_density, income_statement_title, gross_margin_line_items, financial_services_income_lines |
| `fb_exp_017` | 0.000 | 1.000 | 60 | 60, 20, 93 | p60: table_like_numeric_density, balance_sheet_title, total_assets_line_item, working_capital_line_items |
| `fb_exp_020` | 0.000 | 1.000 | 108, 110 | 110, 133, 108 | p108: table_like_numeric_density, capital_intensity_income_statement_lines, capital_intensity_primary_income_statement_lines; p110: table_like_numeric_density, balance_sheet_title, total_assets_line_item, capital_inte... |
| `fb_exp_022` | 0.000 | 1.000 | 62 | 68, 62, 101 | p62: table_like_numeric_density, income_statement_title |
| `fb_exp_023` | 0.000 | 1.000 | 59 | 59, 72, 61 | p59: table_like_numeric_density, balance_sheet_title, total_assets_line_item, ppne_line_item |
| `fb_exp_025` | 0.000 | 1.000 | 2 | 2, 1, 6 | p2: table_like_numeric_density, sga_percent_of_sales_driver_narrative, sga_driver_terms |

## Interpretation

- The baseline reproduces the pre-fix PageIndex page scorer: question terms, section-title terms, and a small set of financial phrase boosts.
- The current scorer adds the existing label-free finance line-item boost used by LlamaIndex diagnostics. It uses only question text and candidate page text.
- This diagnostic explains the ranking effect of the current scorer without calling an LLM or using gold pages during scoring.
- The current scorer has been validated by the full retrieval-only QA and evidence evaluation artifacts for the same 25-question subset.
