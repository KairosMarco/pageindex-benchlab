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

Implemented metrics:

1. `evidence_recall`
2. `citation_precision`
3. `answer_accuracy`

Evidence status: implemented in `evaluators/evidence.py`.

FinanceBench stores evidence pages as zero-indexed page numbers. PageIndex local tree output appears to use one-indexed page ranges, so every evaluation call must declare the prediction page base.

Answer accuracy status: implemented in `evaluators/answer.py`.

Supported answer modes:

- `heuristic`: conservative numeric, direction, and keyword matching.
- `llm`: model judge returning `correct`, `partial`, or `incorrect`.

Example:

```powershell
python scripts\evaluate_answers_mvp.py --results-dir reports\pageindex\qa_llm --output reports\pageindex\answer_eval_llm.json --mode llm --model deepseek/deepseek-v4-pro --continue-on-error
```
