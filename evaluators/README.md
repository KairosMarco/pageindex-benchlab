# Evaluators

Planned metrics:

- `answer_accuracy`
- `evidence_recall`
- `citation_precision`
- `unsupported_claim_rate`
- `retrieval_explainability`
- `token_cost`
- `latency`
- `indexing_cost`

First metrics to implement:

1. `evidence_recall`
2. `citation_precision`

Status: implemented in `evaluators/evidence.py`.

FinanceBench stores evidence pages as zero-indexed page numbers. PageIndex local tree output appears to use one-indexed page ranges, so every evaluation call must declare the prediction page base.
