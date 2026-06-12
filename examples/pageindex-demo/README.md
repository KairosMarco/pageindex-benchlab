# PageIndex Local Demo Result

This directory records the first local PageIndex demo run.

## Demo Document

Source document:

```text
q1-fy25-earnings.pdf
```

The PDF came from the PageIndex upstream example documents:

```text
https://github.com/VectifyAI/PageIndex/tree/main/examples/documents
```

## Model

The demo was run with a DashScope/Qwen model through LiteLLM:

```yaml
model: "dashscope/qwen3.7-plus"
retrieve_model: "dashscope/qwen3.7-plus"
```

Do not commit API keys. Set the key only in the local shell:

```powershell
$env:DASHSCOPE_API_KEY="YOUR_KEY"
```

## Command

From the PageIndex repo root:

```powershell
.\.venv\Scripts\python.exe run_pageindex.py --pdf_path "examples\documents\q1-fy25-earnings.pdf" --if-add-node-summary no --if-add-doc-description no --if-add-node-text no --toc-check-pages 3 --max-pages-per-node 2
```

## Output

Generated file:

```text
results/q1-fy25-earnings_structure.json
```

Copied benchmark artifact:

```text
examples/pageindex-demo/q1-fy25-earnings_structure.json
```

## Notes

The generated structure contains section titles, node IDs, and page ranges. This confirms that the local PageIndex tree-building path can run with a non-OpenAI model through LiteLLM.

Observed dependency issue in upstream `requirements.txt`:

```text
litellm==1.83.7 requires python-dotenv==1.0.1
requirements.txt pins python-dotenv==1.2.2
```

This is a candidate upstream issue or small PR.

