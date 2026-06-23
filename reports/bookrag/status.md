# BookRAG Status

Date: 2026-06-23

## Summary

BookRAG is now the priority external graph-tree baseline in PageIndex BenchLab.

Current local status:

| Item | Status |
|---|---|
| BookRAG source | Available at `D:\bookrag-source` |
| BookRAG environment | `conda` env `gbc-rag` created |
| Python version | `3.12.13` in `gbc-rag` |
| Dependency readiness | Passed |
| Import readiness | Passed |
| CLI smoke | `python D:\bookrag-source\main.py --help` starts successfully |
| BenchLab dataset bridge | Generated for expanded 25-question FinanceBench subset |
| BookRAG system config | Template generated; MinerU defaults to local `pipeline`; model endpoint `TODO_*` values still need replacement |
| Config-load smoke checks | Passed against BookRAG's own config loaders |
| Actual BookRAG index/RAG run | First one-document tree-index attempt started; not completed |
| Upstream communication | License discussion commented; Windows/setup adapter question opened |

## Generated BenchLab Artifacts

```text
datasets/bookrag/financebench_expanded_25.json
datasets/bookrag/financebench_expanded_25_mapping.json
reports/bookrag/readiness.json
reports/bookrag/config/financebench_expanded_25.yaml
reports/bookrag/config/financebench_gbc_template.yaml
```

## Readiness Result

The latest readiness report says:

```text
repo_exists=True
python_version_ok=True
ready_for_adapter_work=True
```

This means adapter work can continue. It does not mean BookRAG has produced benchmark answers yet.

Additional smoke checks:

```text
Core.configs.system_config.load_system_config loads the generated system template.
Core.configs.dataset_config.load_dataset_config loads the generated dataset template.
```

Latest config-load result:

```text
mineru.backend=pipeline
mineru.method=auto
mineru.server_url=''
rag.strategy=gbc
```

## VLDB 2026 Value

BookRAG's README states that the paper has been accepted to VLDB 2026.

VLDB is not a coding competition. It is a major database and data-management research conference/venue. For this project, the acceptance is meaningful because it signals that BookRAG is attached to peer-reviewed systems/data-management research rather than only a GitHub demo or blog concept.

Reference points:

- VLDB 2026 official site: https://vldb.org/2026/
- VLDB Endowment conference page: https://www.vldb.org/conference.html
- CORE ranking entry for VLDB: https://portal.core.edu.au/conf-ranks/1261/

Practical interpretation:

- High research credibility for structured-document indexing and retrieval.
- Strong reason to include BookRAG as a serious baseline.
- Not proof that BookRAG is easier to run, production-ready, or better on FinanceBench.
- Not a reason to abandon PageIndex contribution work.
- Not a substitute for running the same BenchLab evidence and answer evaluation.

## Why It Matters For PageIndex BenchLab

BookRAG directly tests the next question after PageIndex:

> Is a tree-only structure enough, or does adding entity graph relations and tree-graph mappings improve long-document QA enough to justify the extra runtime and setup cost?

This makes BookRAG more strategically relevant than a generic graph baseline.

## Current Blockers Before Running BookRAG

The environment is installed, and the first one-document tree-index command reached the BookRAG/MinerU parsing stage:

```powershell
conda run -n gbc-rag python D:\bookrag-source\main.py -c D:\pageindex-benchlab\reports\bookrag\config\financebench_gbc_template.yaml -d D:\pageindex-benchlab\reports\bookrag\config\financebench_expanded_25.yaml --nsplit 24 --num 1 index --stage tree
```

Observed run history:

| Attempt | Result | Evidence |
|---|---|---|
| `2026-06-23 13:41` | Failed fast because template used `TODO_MINERU_SGLANG_SERVER_URL` with `vlm-sglang-client` | `reports/bookrag/workdir/0eb1f8f0-3187-5712-9602-b98c53f00183/logs/run_20260623_134157.log` |
| `2026-06-23 13:49` | Reached MinerU local `pipeline` parsing after config fix; stopped after timeout/observation because local model parsing had not completed | `reports/bookrag/workdir/0eb1f8f0-3187-5712-9602-b98c53f00183/logs/run_20260623_134931.log` |

This means the previous invalid-server-URL error is fixed in the generated template. Remaining execution work is now runtime/model related:

- LLM endpoint and model for tree/graph construction;
- VLM endpoint and model if visual parsing is required;
- embedding endpoint/model;
- reranker endpoint/model;
- decision on CPU vs GPU runtime for local components;
- enough time/disk/network for MinerU local `pipeline` model loading, or a valid `mineru.server_url` if using the faster `vlm-sglang-client` path;
- reviewed BookRAG license position before redistributing modified code or generated artifacts.

The generated system config is intentionally a template:

```text
reports/bookrag/config/financebench_gbc_template.yaml
```

It contains `TODO_*` placeholders and no real API keys. Its default PDF parsing path is MinerU `pipeline`, so a fresh run no longer requires a SGLang server just to pass config validation. To reproduce BookRAG's upstream VLM/SGLang path, change `mineru.backend` back to `vlm-sglang-client` and provide a real `mineru.server_url`.

## Next Engineering Steps

1. Create a local, non-committed runnable config from `financebench_gbc_template.yaml`.
2. Fill the LLM endpoint/model fields for tree outline extraction and summaries.
3. Let MinerU `pipeline` finish local model loading, or configure a real MinerU/SGLang service.
4. Re-run one-document indexing with a longer timeout and record index artifacts.
5. Map one BookRAG answer into `BenchmarkResult` after RAG inference succeeds.
6. Run BenchLab evidence evaluation on that single output.

Promotion rule:

BookRAG should stay out of the main comparison table until at least one schema-valid answer output is generated and evaluated.

## Upstream Communication

Current BookRAG upstream links:

- License discussion: https://github.com/sam234990/BookRAG/issues/5
- BenchLab comment on license discussion: https://github.com/sam234990/BookRAG/issues/5#issuecomment-4776317274
- Windows/local setup and external benchmark adapter question: https://github.com/sam234990/BookRAG/issues/6

Rationale:

- Do not duplicate the existing license issue.
- Ask maintainers whether Windows/local setup notes and external benchmark adapter docs are welcome before preparing a PR.
- Keep BenchLab's local structural adapter independent until BookRAG's license and contribution direction are clearer.
