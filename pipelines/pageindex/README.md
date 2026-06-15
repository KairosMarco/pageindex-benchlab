# PageIndex Adapter

Target source:

- https://github.com/VectifyAI/PageIndex

Goal:

```text
PDF/document -> PageIndex tree -> reasoning retrieval -> unified benchmark output
```

First task:

- Run the official PageIndex demo.
- Document setup issues.
- Create a minimal adapter returning the shared output schema.

## First Local Demo

Status: completed.

Result artifact:

```text
examples/pageindex-demo/q1-fy25-earnings_structure.json
```

Key finding:

```text
PageIndex can generate a document tree from the example PDF using DashScope/Qwen through LiteLLM.
```

Observed upstream issue:

```text
litellm==1.83.7 requires python-dotenv==1.0.1, but upstream requirements.txt pins python-dotenv==1.2.2.
```

## Adapter

Implemented:

```text
pipelines/pageindex/adapter.py
```

Current mode:

```text
index_only
```

Example:

```powershell
python -m pipelines.pageindex.adapter examples\pageindex-demo\q1-fy25-earnings_structure.json --output reports\pageindex-demo-result.json
```

The adapter converts PageIndex tree JSON into the shared `BenchmarkResult` schema. Full question answering is the next adapter iteration.
