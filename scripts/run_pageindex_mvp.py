from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_QUESTIONS = ROOT / "datasets" / "financebench" / "mvp_questions.jsonl"
DEFAULT_PDF_DIR = ROOT / "datasets" / "raw" / "financebench" / "pdfs"
DEFAULT_OUTPUT_DIR = ROOT / "reports" / "pageindex" / "structures"
DEFAULT_MANIFEST = ROOT / "reports" / "pageindex" / "indexing_manifest.json"


def load_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def default_pageindex_repo() -> Path:
    env_path = os.getenv("PAGEINDEX_REPO")
    if env_path:
        return Path(env_path)
    return Path("D:/pageindex-demo/PageIndex") if os.name == "nt" else ROOT.parent / "PageIndex"


def pageindex_python(pageindex_repo: Path) -> Path:
    if os.name == "nt":
        candidate = pageindex_repo / ".venv" / "Scripts" / "python.exe"
    else:
        candidate = pageindex_repo / ".venv" / "bin" / "python"
    return candidate if candidate.exists() else Path(sys.executable)


def has_model_key() -> bool:
    return any(
        os.getenv(name)
        for name in (
            "DASHSCOPE_API_KEY",
            "DEEPSEEK_API_KEY",
            "OPENAI_API_KEY",
            "ANTHROPIC_API_KEY",
            "GEMINI_API_KEY",
            "OPENROUTER_API_KEY",
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run PageIndex indexing for FinanceBench MVP PDFs.")
    parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS)
    parser.add_argument("--pdf-dir", type=Path, default=DEFAULT_PDF_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--pageindex-repo", type=Path, default=default_pageindex_repo())
    parser.add_argument("--model", default=None, help="Optional model override passed to PageIndex.")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--doc-name", action="append", help="Run only the given document name. Can be repeated.")
    parser.add_argument("--force", action="store_true", help="Re-run documents even if the structure already exists.")
    parser.add_argument("--continue-on-error", action="store_true")
    parser.add_argument("--timeout-seconds", type=int, default=1800)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not args.pageindex_repo.exists():
        raise SystemExit(f"PageIndex repo not found: {args.pageindex_repo}")
    if not (args.pageindex_repo / "run_pageindex.py").exists():
        raise SystemExit(f"run_pageindex.py not found under: {args.pageindex_repo}")
    questions = load_jsonl(args.questions)
    doc_names = sorted({q["doc_name"] for q in questions})
    if args.doc_name:
        requested = set(args.doc_name)
        doc_names = [name for name in doc_names if name in requested]
        missing = sorted(requested - set(doc_names))
        if missing:
            raise SystemExit(f"Requested doc_name not found in MVP questions: {missing}")
    if args.limit:
        doc_names = doc_names[: args.limit]

    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    py = pageindex_python(args.pageindex_repo)
    manifest = []

    docs_to_run = []
    for doc_name in doc_names:
        final_output = args.output_dir / f"{doc_name}_structure.json"
        if final_output.exists() and not args.force:
            manifest.append(
                {
                    "doc_name": doc_name,
                    "status": "exists",
                    "structure_path": str(final_output.relative_to(ROOT)),
                    "size_bytes": final_output.stat().st_size,
                }
            )
        else:
            docs_to_run.append(doc_name)

    if docs_to_run and not args.dry_run and not has_model_key():
        raise SystemExit(
            "No model API key found. Set DASHSCOPE_API_KEY, OPENAI_API_KEY, or another provider key in the current shell."
        )

    for doc_name in docs_to_run:
        pdf_path = args.pdf_dir / f"{doc_name}.pdf"
        final_output = args.output_dir / f"{doc_name}_structure.json"
        if not pdf_path.exists():
            raise SystemExit(f"Missing PDF: {pdf_path}. Run scripts/download_mvp_pdfs.py first.")

        command = [
            str(py),
            "run_pageindex.py",
            "--pdf_path",
            str(pdf_path),
            "--if-add-node-summary",
            "no",
            "--if-add-doc-description",
            "no",
            "--if-add-node-text",
            "no",
            "--toc-check-pages",
            "5",
            "--max-pages-per-node",
            "8",
        ]
        if args.model:
            command.extend(["--model", args.model])

        print(" ".join(command))
        if args.dry_run:
            manifest.append(
                {
                    "doc_name": doc_name,
                    "status": "dry_run",
                    "pdf_path": str(pdf_path.relative_to(ROOT)),
                    "command": command,
                }
            )
            continue

        started = time.perf_counter()
        try:
            subprocess.run(command, cwd=args.pageindex_repo, check=True, timeout=args.timeout_seconds)
            generated = args.pageindex_repo / "results" / f"{doc_name}_structure.json"
            if not generated.exists():
                raise FileNotFoundError(f"Expected PageIndex output not found: {generated}")
            shutil.copy2(generated, final_output)
            manifest.append(
                {
                    "doc_name": doc_name,
                    "status": "generated",
                    "pdf_path": str(pdf_path.relative_to(ROOT)),
                    "structure_path": str(final_output.relative_to(ROOT)),
                    "size_bytes": final_output.stat().st_size,
                    "latency_ms": int((time.perf_counter() - started) * 1000),
                    "command": command,
                }
            )
        except Exception as exc:
            manifest.append(
                {
                    "doc_name": doc_name,
                    "status": "failed",
                    "pdf_path": str(pdf_path.relative_to(ROOT)),
                    "latency_ms": int((time.perf_counter() - started) * 1000),
                    "error": str(exc),
                    "command": command,
                }
            )
            if not args.continue_on_error:
                args.manifest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
                raise

    args.manifest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Indexing manifest: {args.manifest}")
    print(f"PageIndex structures directory: {args.output_dir}")


if __name__ == "__main__":
    main()
