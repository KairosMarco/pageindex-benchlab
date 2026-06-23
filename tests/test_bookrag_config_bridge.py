from __future__ import annotations

import json
from pathlib import Path

import yaml

from scripts.prepare_bookrag_config import build_dataset_config, build_system_config


def test_build_dataset_config_uses_absolute_paths(tmp_path: Path) -> None:
    dataset = tmp_path / "dataset.json"
    working_dir = tmp_path / "work"

    payload = build_dataset_config(dataset, working_dir, "financebench")

    assert payload["dataset_name"] == "financebench"
    assert payload["dataset_path"].endswith("dataset.json")
    assert payload["working_dir"].endswith("work")


def test_build_system_config_writes_bookrag_required_sections(tmp_path: Path) -> None:
    mapping = tmp_path / "mapping.json"
    mapping.write_text(
        json.dumps(
            {
                "documents": [
                    {
                        "doc_name": "EXAMPLE_10K",
                        "doc_path": str(tmp_path / "EXAMPLE_10K.pdf"),
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    payload = build_system_config(mapping, tmp_path / "work")

    assert payload["pdf_path"].endswith("EXAMPLE_10K.pdf")
    assert payload["save_path"].endswith("EXAMPLE_10K")
    assert payload["mineru"]["backend"] == "pipeline"
    assert payload["mineru"]["method"] == "auto"
    assert payload["mineru"]["server_url"] == ""
    assert payload["rag"]["strategy"] == "gbc"
    assert payload["rag"]["sim_threshold_e"] == 0.3


def test_system_config_template_is_yaml_serializable(tmp_path: Path) -> None:
    mapping = tmp_path / "mapping.json"
    mapping.write_text(json.dumps({"documents": []}), encoding="utf-8")

    serialized = yaml.safe_dump(build_system_config(mapping, tmp_path / "work"))

    assert "TODO_LLM_MODEL" in serialized
    assert "mineru:" in serialized
