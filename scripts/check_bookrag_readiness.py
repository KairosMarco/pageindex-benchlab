from __future__ import annotations

import argparse
import importlib.metadata
import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BOOKRAG_REPO = Path(r"D:\bookrag-source")
DEFAULT_OUTPUT = ROOT / "reports" / "bookrag" / "readiness.json"


REQUIRED_PATHS = [
    "README.md",
    "requirements.txt",
    "environment.yml",
    "main.py",
    "Core",
    "Core/construct_index.py",
    "Core/inference.py",
    "Core/rag",
    "Scripts",
    "Scripts/cfg",
    "config",
]


PACKAGE_CHECKS = [
    ("beautifulsoup4", "HTML parsing dependency"),
    ("chromadb", "BookRAG vector store dependency"),
    ("json_repair", "model JSON repair dependency"),
    ("mineru", "PDF parsing dependency"),
    ("networkx", "graph processing dependency"),
    ("openai", "LLM provider dependency"),
    ("pandas", "dataset and result handling dependency"),
    ("pydantic", "schema/config dependency"),
    ("PyYAML", "YAML config dependency"),
    ("spacy", "entity extraction dependency"),
    ("torch", "model/runtime dependency"),
    ("torchvision", "vision model dependency"),
    ("ultralytics", "layout/document vision dependency"),
]


IMPORT_CHECKS = [
    ("yaml", "YAML config import"),
    ("networkx", "graph processing import"),
    ("spacy", "entity extraction import"),
    ("chromadb", "vector store import"),
    ("mineru", "PDF parsing import"),
]


def package_version(package_name: str) -> str | None:
    try:
        return importlib.metadata.version(package_name)
    except importlib.metadata.PackageNotFoundError:
        return None


def import_status(module_name: str) -> dict[str, Any]:
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


def git_remote(repo_path: Path) -> str | None:
    if not repo_path.exists():
        return None
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_path), "remote", "get-url", "origin"],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except Exception:
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def build_report(bookrag_repo: Path, run_import_checks: bool) -> dict[str, Any]:
    path_checks = [
        {
            "path": relative_path,
            "exists": (bookrag_repo / relative_path).exists(),
        }
        for relative_path in REQUIRED_PATHS
    ]
    package_checks = [
        {
            "name": package_name,
            "purpose": purpose,
            "version": package_version(package_name),
            "available": package_version(package_name) is not None,
        }
        for package_name, purpose in PACKAGE_CHECKS
    ]
    imports = []
    if run_import_checks:
        imports = [
            {
                **import_status(module_name),
                "purpose": purpose,
            }
            for module_name, purpose in IMPORT_CHECKS
        ]

    missing_paths = [item["path"] for item in path_checks if not item["exists"]]
    missing_packages = [item["name"] for item in package_checks if not item["available"]]
    import_failures = [item["module"] for item in imports if not item["available"]]
    python_version_ok = sys.version_info.major == 3 and sys.version_info.minor == 12
    license_present = any((bookrag_repo / name).exists() for name in ("LICENSE", "LICENSE.md", "LICENSE.txt"))

    recommendations: list[str] = []
    if not bookrag_repo.exists():
        recommendations.append("Clone BookRAG outside this repository, for example: git clone https://github.com/sam234990/BookRAG D:\\bookrag-source")
    if missing_paths and bookrag_repo.exists():
        recommendations.append("The BookRAG checkout is incomplete or not the expected repository.")
    if not python_version_ok:
        recommendations.append("Use a Python 3.12 environment for BookRAG, matching the upstream README.")
    if missing_packages:
        recommendations.append("Install BookRAG dependencies in a separate environment, not in BenchLab's main environment.")
    if import_failures:
        recommendations.append("Resolve failing imports before running BookRAG indexing.")
    if not license_present:
        recommendations.append("No local BookRAG license file was detected. Confirm license terms before redistributing code or artifacts.")

    ready_for_adapter_work = (
        bookrag_repo.exists()
        and not missing_paths
        and python_version_ok
        and not missing_packages
        and not import_failures
    )

    return {
        "summary": {
            "bookrag_repo": str(bookrag_repo),
            "repo_exists": bookrag_repo.exists(),
            "remote": git_remote(bookrag_repo),
            "python_executable": sys.executable,
            "python_version": sys.version,
            "platform": platform.platform(),
            "python_version_ok": python_version_ok,
            "license_present": license_present,
            "missing_paths": missing_paths,
            "missing_packages": missing_packages,
            "import_failures": import_failures,
            "ready_for_adapter_work": ready_for_adapter_work,
        },
        "paths": path_checks,
        "packages": package_checks,
        "imports": imports,
        "recommendations": recommendations,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Check local readiness for the external BookRAG baseline.")
    parser.add_argument("--bookrag-repo", type=Path, default=DEFAULT_BOOKRAG_REPO)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--import-check",
        action="store_true",
        help="Import selected BookRAG dependencies. This can be slower than metadata checks.",
    )
    args = parser.parse_args()

    report = build_report(args.bookrag_repo, run_import_checks=args.import_check)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    summary = report["summary"]
    print(f"BookRAG readiness report: {args.output}")
    print(f"repo_exists={summary['repo_exists']}")
    print(f"python_version_ok={summary['python_version_ok']}")
    print(f"ready_for_adapter_work={summary['ready_for_adapter_work']}")
    if summary["missing_paths"]:
        print("missing_paths=" + ",".join(summary["missing_paths"]))
    if summary["missing_packages"]:
        print("missing_packages=" + ",".join(summary["missing_packages"]))
    if summary["import_failures"]:
        print("import_failures=" + ",".join(summary["import_failures"]))


if __name__ == "__main__":
    main()
