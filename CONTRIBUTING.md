# Contributing

This project is an early benchmark workspace. Contributions should be small, reproducible, and easy to review.

## Principles

- Every task should have a GitHub issue.
- Every PR should solve one problem.
- Every experiment should record model name, prompt, version, token usage, latency, and raw output.
- Benchmark claims must be reproducible.
- Do not claim that one method is universally better than another without scoped evidence.

## Local Setup

```powershell
git clone https://github.com/YOUR_USERNAME/pageindex-benchlab.git
cd pageindex-benchlab
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Branch Naming

Use short descriptive branch names:

```text
docs/windows-quickstart
adapter/pageindex
eval/evidence-recall
baseline/vector-rag
```

## PR Checklist

Before opening a PR:

- [ ] The change is scoped to one issue.
- [ ] The README or docs are updated if needed.
- [ ] Example commands are tested.
- [ ] New benchmark output includes raw results or a reproducible command.
- [ ] No API keys, private data, or paid credentials are committed.

