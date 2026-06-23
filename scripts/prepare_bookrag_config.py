from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

DEFAULT_DATASET = ROOT / "datasets" / "bookrag" / "financebench_expanded_25.json"
DEFAULT_MAPPING = ROOT / "datasets" / "bookrag" / "financebench_expanded_25_mapping.json"
DEFAULT_OUTPUT_DIR = ROOT / "reports" / "bookrag" / "config"
DEFAULT_WORKING_DIR = ROOT / "reports" / "bookrag" / "workdir"
DEFAULT_SYSTEM_CONFIG = DEFAULT_OUTPUT_DIR / "financebench_gbc_template.yaml"
DEFAULT_DATASET_CONFIG = DEFAULT_OUTPUT_DIR / "financebench_expanded_25.yaml"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_yaml(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")


def build_dataset_config(dataset_path: Path, working_dir: Path, dataset_name: str) -> dict[str, Any]:
    return {
        "dataset_path": str(dataset_path.resolve()),
        "working_dir": str(working_dir.resolve()),
        "dataset_name": dataset_name,
    }


def build_system_config(mapping_path: Path, working_dir: Path) -> dict[str, Any]:
    mapping = read_json(mapping_path)
    first_doc = mapping["documents"][0] if mapping.get("documents") else {}
    default_pdf = first_doc.get("doc_path", "TODO")
    default_save_path = str((working_dir / "indexes" / first_doc.get("doc_name", "TODO_DOC")).resolve())

    return {
        "pdf_path": default_pdf,
        "save_path": default_save_path,
        "llm": {
            "model_name": "TODO_LLM_MODEL",
            "api_key": "TODO_LLM_API_KEY_OR_PLACEHOLDER",
            "api_base": "TODO_OPENAI_COMPATIBLE_BASE_URL",
            "backend": "openai",
            "max_tokens": 5000,
            "temperature": 0.1,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
            "max_workers": 4,
        },
        "vlm": {
            "model_name": "TODO_VLM_MODEL",
            "api_key": "TODO_VLM_API_KEY_OR_PLACEHOLDER",
            "api_base": "TODO_VLM_OPENAI_COMPATIBLE_BASE_URL",
            "temperature": 0.1,
            "max_tokens": 6000,
            "backend": "gpt",
        },
        "index": {
            "chunk_size": 512,
            "overlap": 50,
        },
        "mineru": {
            # Use MinerU's local pipeline backend by default so a fresh BenchLab
            # setup does not immediately require a running SGLang parsing service.
            # Switch this to vlm-sglang-client plus a real server_url when
            # reproducing the upstream BookRAG high-throughput VLM setup.
            "backend": "pipeline",
            "method": "auto",
            "server_url": "",
            "lang": "en",
        },
        "tree": {
            "node_keywords": True,
            "node_summary": True,
        },
        "graph": {
            "extractor_type": "llm",
            "local_model_name": "en_core_web_sm",
            "image_description_force": True,
            "max_gleaning": 0,
            "refine_type": "advanced",
            "embedding_config": {
                "model_name": "TODO_TEXT_EMBEDDING_MODEL",
                "backend": "openai",
                "max_length": 4096,
                "device": "cpu",
                "api_base": "TODO_EMBEDDING_OPENAI_COMPATIBLE_BASE_URL",
            },
            "reranker_config": {
                "model_name": "TODO_RERANKER_MODEL",
                "max_length": 4096,
                "device": "cpu",
                "backend": "vllm",
                "api_base": "TODO_RERANKER_OPENAI_COMPATIBLE_BASE_URL",
            },
        },
        "vdb": {
            "mm_embedding": True,
            "vdb_dir_name": "Tree_vdb",
            "collection_name": "TreeVDB",
            "embedding_config": {
                "model_name": "TODO_MULTIMODAL_EMBEDDING_MODEL",
                "device": "cpu",
            },
        },
        "rag_force_reprocess": True,
        "rag": {
            "strategy": "gbc",
            "variant": "standard",
            "topk": 10,
            "sim_threshold_e": 0.3,
            "select_depth": 2,
            "max_retry": 2,
            "reranker_config": {
                "model_name": "TODO_RERANKER_MODEL",
                "max_length": 4096,
                "device": "cpu",
                "backend": "vllm",
                "api_base": "TODO_RERANKER_OPENAI_COMPATIBLE_BASE_URL",
            },
            "mm_reranker_config": {
                "model_name": "TODO_MULTIMODAL_EMBEDDING_MODEL",
                "device": "cpu",
            },
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare BookRAG dataset and system YAML templates for BenchLab.")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--mapping", type=Path, default=DEFAULT_MAPPING)
    parser.add_argument("--working-dir", type=Path, default=DEFAULT_WORKING_DIR)
    parser.add_argument("--dataset-config", type=Path, default=DEFAULT_DATASET_CONFIG)
    parser.add_argument("--system-config", type=Path, default=DEFAULT_SYSTEM_CONFIG)
    parser.add_argument("--dataset-name", default="financebench")
    args = parser.parse_args()

    if not args.dataset.exists():
        raise FileNotFoundError(f"BookRAG dataset does not exist: {args.dataset}")
    if not args.mapping.exists():
        raise FileNotFoundError(f"BookRAG mapping does not exist: {args.mapping}")

    args.working_dir.mkdir(parents=True, exist_ok=True)
    dataset_config = build_dataset_config(args.dataset, args.working_dir, args.dataset_name)
    system_config = build_system_config(args.mapping, args.working_dir)

    write_yaml(args.dataset_config, dataset_config)
    write_yaml(args.system_config, system_config)

    print(f"BookRAG dataset config: {args.dataset_config}")
    print(f"BookRAG system config template: {args.system_config}")
    print("Replace TODO_* values before running BookRAG indexing or RAG inference.")


if __name__ == "__main__":
    main()
