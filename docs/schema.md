# Benchmark Schema

All RAG pipelines should return the same result shape so evaluators and reports can compare them directly.

The canonical Pydantic models live in:

```text
benchlab/schemas.py
```

## BenchmarkQuestion

Represents a gold-labeled benchmark item.

Required fields:

- `question_id`
- `source_id`
- `dataset`
- `company`
- `doc_name`
- `question`
- `gold_answer`
- `gold_evidence`

FinanceBench evidence pages are stored in both page bases:

```text
page_zero_indexed
page_one_indexed
```

## BenchmarkResult

Represents one method's answer to one benchmark question.

```json
{
  "method": "pageindex",
  "question_id": "fb_mvp_001",
  "question": "...",
  "answer": "...",
  "citations": [
    {
      "document_id": "3M_2018_10K",
      "page": 60,
      "section": "Consolidated Statement of Cash Flows",
      "text": "..."
    }
  ],
  "retrieval_trace": [
    {
      "step": 1,
      "action": "inspect_tree",
      "target": "Cash Flow Statement"
    }
  ],
  "token_usage": {
    "input": 12000,
    "output": 800,
    "total": 12800
  },
  "latency_ms": 8400,
  "metadata": {}
}
```

## Citation Page Base

Evaluators must declare the citation page base for each method output:

```text
citation_page_base=0
citation_page_base=1
```

FinanceBench gold evidence is zero-indexed. PageIndex tree ranges from the local demo appear one-indexed.

