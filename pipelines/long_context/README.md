# Long-context LLM Baseline

Goal:

```text
full document text -> long context prompt -> answer with page citations
```

This is a baseline, not a RAG framework.

First task:

- Extract page text with PyMuPDF.
- Preserve `[PAGE n]` markers.
- Ask the model to answer using only the document.

