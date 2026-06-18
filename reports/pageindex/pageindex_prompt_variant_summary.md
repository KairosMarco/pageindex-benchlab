# PageIndex Prompt Variant Summary

Date: 2026-06-18

## Scope

This report compares targeted PageIndex answer-prompt probes for the two remaining expanded answer issues. The default row is the existing 25-question baseline; the finance rows are two-question probes only.

- Question file: `datasets\financebench\expanded_questions_25.jsonl`
- Method: `pageindex_tree_qa_llm`
- Target questions: `fb_exp_019, fb_exp_020`
- Model: `deepseek/deepseek-v4-pro`

## Run Summary

| Run | Scope | Complete | Results | Evidence recall | Citation precision | Answer accuracy | Correct | Partial | Incorrect | Avg tokens | Avg latency ms |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| default prompt | full_run | yes | 25 | 1.000 | 0.347 | 0.920 | 23 | 0 | 2 | 2882.160 | 4839.600 |
| finance reasoning v2 probe | targeted_probe | yes | 2 | 1.000 | 0.500 | 0.500 | 1 | 0 | 1 | 3521.000 | 12202.000 |
| finance reasoning v3 probe | targeted_probe | yes | 2 | 1.000 | 0.500 | 1.000 | 2 | 0 | 0 | 3714.000 | 15924.500 |

## Target Outcomes

| Run | Question | Verdict | Evidence recall | Citation precision | Selected pages | Tokens | Prompt mode |
|---|---|---|---:|---:|---|---:|---|
| default prompt | `fb_exp_019` | incorrect | 1.000 | 0.333 | 86, 66, 93 | 3059 | `default` |
| default prompt | `fb_exp_020` | incorrect | 1.000 | 0.667 | 110, 133, 108 | 2675 | `default` |
| finance reasoning v2 probe | `fb_exp_019` | incorrect | 1.000 | 0.333 | 86, 66, 93 | 3511 | `finance_reasoning_v2` |
| finance reasoning v2 probe | `fb_exp_020` | correct | 1.000 | 0.667 | 110, 133, 108 | 3531 | `finance_reasoning_v2` |
| finance reasoning v3 probe | `fb_exp_019` | correct | 1.000 | 0.333 | 86, 66, 93 | 4018 | `finance_reasoning_v3` |
| finance reasoning v3 probe | `fb_exp_020` | correct | 1.000 | 0.667 | 110, 133, 108 | 3410 | `finance_reasoning_v3` |

## Answer Evidence

| Run | Question | Predicted answer | Judge rationale |
|---|---|---|---|
| default prompt | `fb_exp_019` | Based on the Consolidated Statements of Cash Flows, American Water Works paid out $389 million in dividends for the fiscal year 2020 (page 86). In USD billions, this amount is $0.389 billion. | The predicted answer states $0.389 billion, which does not match the gold answer of $0.40 billion. The difference is material and not a rounding discrepancy from the provided gold answer. |
| default prompt | `fb_exp_020` | No, based on the FY2022 data provided, CVS Health does not appear to be a capital-intensive business. Capital-intensive businesses typically have a high proportion of fixed assets like property, plant, and equipment relative to total assets. For CVS Health, property and equipm... | The gold answer says 'Yes, CVS Health is a capital-intensive business', while the predicted answer says 'No, CVS Health does not appear to be a capital-intensive business.' These are opposite conclusions, so the predicted answer is incorrect. |
| finance reasoning v2 probe | `fb_exp_019` | According to the consolidated statement of cash flows on page 86, American Water Works paid $389 million in dividends for FY2020. Converted to USD billions, $389 million is $0.389 billion (approximately $0.39 billion). | The predicted answer states $389 million ($0.389 billion, approximately $0.39 billion), while the gold answer is $0.40 billion. The difference of $0.01 billion ($10 million) is material, and the predicted amount does not match the expected figure. |
| finance reasoning v2 probe | `fb_exp_020` | Yes, CVS Health is a capital-intensive business under a broad asset-intensity definition. This definition considers a business capital-intensive if it requires significant total assets relative to its earnings, resulting in a low return on assets (ROA). For FY2022, net income... | The predicted answer agrees with the gold answer that CVS Health is capital-intensive based on FY2022 data, citing a low ROA (~1.8%) and noting that goodwill comprises a significant portion of assets while fixed assets are only about 5.6% of total assets. The predicted answer'... |
| finance reasoning v3 probe | `fb_exp_019` | $0.40 billion ($389 million) (per the Consolidated Statements of Cash Flows, page 86). | The predicted answer provides the amount as $0.40 billion, which exactly matches the gold answer of $0.40 (billion). The additional parenthetical detail does not contradict this amount. |
| finance reasoning v3 probe | `fb_exp_020` | Applying a broad asset-intensity definition, a business is considered capital-intensive if it requires a large asset base relative to its earnings, evidenced by a low Return on Assets (ROA). Under this definition, CVS Health is capital-intensive based on FY2022 data, with the... | The predicted answer correctly concludes that CVS Health is capital-intensive based on FY2022 data, using ROA of ~1.8% and acknowledging the caveat that fixed assets are a small portion of total assets, which aligns with the gold answer's main point and supporting detail. |

## Interpretation

- The PageIndex retrieval stage was already successful for both target questions; the probes isolate answer-generation behavior.
- `fb_exp_019` is primarily a rounding or judge-policy case: the source value is `$389 million`, while the benchmark gold answer is `$0.40` billion.
- `fb_exp_020` is a finance concept-definition case: the gold answer treats low ROA and a broad goodwill-heavy asset base as capital-intensity evidence, while the default answer used a narrow fixed-asset ratio interpretation.
- Treat these rows as prompt-ablation evidence only. They do not replace the default 25-question cross-method baseline unless a full 25-question PageIndex prompt-variant run is executed.

## Artifacts

### default prompt

- Results: `reports\pageindex\qa_llm_expanded_25`
- Evidence eval: `reports\pageindex\evidence_eval_qa_llm_expanded_25.json`
- Answer eval: `reports\pageindex\answer_eval_qa_llm_expanded_25.json`

### finance reasoning v2 probe

- Results: `reports\pageindex\qa_llm_expanded_25_finance_reasoning_v2_probe`
- Evidence eval: `reports\pageindex\evidence_eval_qa_llm_expanded_25_finance_reasoning_v2_probe.json`
- Answer eval: `reports\pageindex\answer_eval_qa_llm_expanded_25_finance_reasoning_v2_probe.json`

### finance reasoning v3 probe

- Results: `reports\pageindex\qa_llm_expanded_25_finance_reasoning_v3_probe`
- Evidence eval: `reports\pageindex\evidence_eval_qa_llm_expanded_25_finance_reasoning_v3_probe.json`
- Answer eval: `reports\pageindex\answer_eval_qa_llm_expanded_25_finance_reasoning_v3_probe.json`
