from __future__ import annotations

import argparse
import importlib.metadata
import json
import platform
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "reports" / "stage1_environment_report.json"


PACKAGES = [
    "pydantic",
    "pymupdf",
    "litellm",
    "llama-index",
    "llama-index-core",
    "llama-index-embeddings-huggingface",
    "llama-index-retrievers-bm25",
    "sentence-transformers",
]


IMPORTS = {
    "fitz": "PyMuPDF PDF extraction",
    "litellm": "LLM provider wrapper",
    "llama_index.core": "LlamaIndex core",
    "sentence_transformers": "local embedding model support",
}


def package_version(package_name: str) -> str | None:
    try:
        return importlib.metadata.version(package_name)
    except importlib.metadata.PackageNotFoundError:
        return None


def import_status(module_name: str) -> dict[str, str | bool]:
    try:
        __import__(module_name)
    except Exception as exc:
        return {
            "module": module_name,
            "available": False,
            "error": str(exc),
        }
    return {
        "module": module_name,
        "available": True,
        "error": "",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Check the Stage 1 benchmark Python environment.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    packages = [
        {
            "name": package,
            "version": package_version(package),
            "available": package_version(package) is not None,
        }
        for package in PACKAGES
    ]
    imports = [
        {
            **import_status(module),
            "purpose": purpose,
        }
        for module, purpose in IMPORTS.items()
    ]
    missing_required_for_llamaindex = [
        package["name"]
        for package in packages
        if package["name"] in {"llama-index", "llama-index-core", "sentence-transformers"}
        and not package["available"]
    ]
    payload = {
        "summary": {
            "python_executable": sys.executable,
            "python_version": sys.version,
            "platform": platform.platform(),
            "llamaindex_ready": not missing_required_for_llamaindex,
            "missing_required_for_llamaindex": missing_required_for_llamaindex,
        },
        "packages": packages,
        "imports": imports,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Environment report: {args.output}")
    print(f"llamaindex_ready={payload['summary']['llamaindex_ready']}")
    if missing_required_for_llamaindex:
        print("missing_required_for_llamaindex=" + ",".join(missing_required_for_llamaindex))


if __name__ == "__main__":
    main()
