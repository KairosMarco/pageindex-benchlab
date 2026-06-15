# Scripts

Utility scripts for repeatable local benchmark setup.

## Download FinanceBench MVP PDFs

```powershell
python scripts\download_mvp_pdfs.py
```

Outputs local PDFs to:

```text
datasets/raw/financebench/pdfs/
```

This directory is intentionally ignored by git.

The script writes a committed manifest to:

```text
reports/mvp_pdf_manifest.json
```

## Run PageIndex Indexing

Requires a local PageIndex checkout and an LLM provider key.

Default PageIndex path on Windows:

```text
D:\pageindex-demo\PageIndex
```

Override with:

```powershell
$env:PAGEINDEX_REPO="D:\path\to\PageIndex"
```

Set a model API key in the current shell. For DashScope/Qwen:

```powershell
$env:DASHSCOPE_API_KEY="YOUR_NEW_KEY"
```

Dry run:

```powershell
python scripts\run_pageindex_mvp.py --dry-run --limit 3
```

Run all MVP PDFs:

```powershell
python scripts\run_pageindex_mvp.py
```

Outputs copied PageIndex structures to:

```text
reports/pageindex/structures/
```

Do not commit API keys.

