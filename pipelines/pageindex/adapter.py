from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from benchlab.schemas import BenchmarkResult, Citation, RetrievalTraceStep


def load_structure(structure_path: str | Path) -> dict[str, Any]:
    with Path(structure_path).open(encoding="utf-8") as f:
        return json.load(f)


def flatten_nodes(nodes: list[dict[str, Any]], *, depth: int = 0) -> list[dict[str, Any]]:
    flattened: list[dict[str, Any]] = []
    for node in nodes:
        item = dict(node)
        children = item.pop("nodes", [])
        item["depth"] = depth
        flattened.append(item)
        flattened.extend(flatten_nodes(children, depth=depth + 1))
    return flattened


def structure_to_result(
    structure_path: str | Path,
    *,
    question_id: str = "pageindex_index_demo",
    question: str = "Generate the PageIndex document tree.",
    method: str = "pageindex",
) -> BenchmarkResult:
    """Convert a PageIndex tree JSON artifact into the shared result schema.

    This adapter is index-only for the first milestone: it verifies that
    PageIndex produced a navigable document tree and represents the tree as
    citations and retrieval trace steps. Question answering will build on this
    shared shape in the next adapter iteration.
    """

    payload = load_structure(structure_path)
    doc_name = payload.get("doc_name") or Path(structure_path).stem
    nodes = flatten_nodes(payload.get("structure", []))

    citations = [
        Citation(
            document_id=doc_name,
            page=node.get("start_index"),
            section=node.get("title"),
            text=node.get("summary"),
            metadata={
                "node_id": node.get("node_id"),
                "depth": node.get("depth", 0),
                "start_index": node.get("start_index"),
                "end_index": node.get("end_index"),
            },
        )
        for node in nodes
    ]

    trace = [
        RetrievalTraceStep(
            step=i + 1,
            action="index_node",
            target=node.get("title", ""),
            metadata={
                "node_id": node.get("node_id"),
                "depth": node.get("depth", 0),
                "start_index": node.get("start_index"),
                "end_index": node.get("end_index"),
            },
        )
        for i, node in enumerate(nodes)
    ]

    return BenchmarkResult(
        method=method,
        question_id=question_id,
        question=question,
        answer=f"Generated PageIndex tree with {len(nodes)} nodes for {doc_name}.",
        citations=citations,
        retrieval_trace=trace,
        metadata={
            "adapter_mode": "index_only",
            "structure_path": str(structure_path),
            "doc_name": doc_name,
            "node_count": len(nodes),
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert PageIndex tree JSON to benchmark schema.")
    parser.add_argument("structure_path", help="Path to PageIndex *_structure.json")
    parser.add_argument("--output", help="Optional output JSON path")
    args = parser.parse_args()

    result = structure_to_result(args.structure_path)
    result_json = result.model_dump_json(indent=2)

    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(result_json + "\n", encoding="utf-8")
    else:
        print(result_json)


if __name__ == "__main__":
    main()

