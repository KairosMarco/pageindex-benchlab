from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path
from typing import Any

import fitz
from litellm import completion

from benchlab.schemas import BenchmarkQuestion, BenchmarkResult, Citation, RetrievalTraceStep, TokenUsage
from pipelines.pageindex.adapter import flatten_nodes, load_structure


def load_question(path: Path, question_id: str) -> BenchmarkQuestion:
    with path.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            if row["question_id"] == question_id:
                return BenchmarkQuestion.model_validate(row)
    raise ValueError(f"Question not found: {question_id}")


def keywords(text: str) -> set[str]:
    stop = {
        "the",
        "and",
        "for",
        "with",
        "from",
        "what",
        "which",
        "does",
        "have",
        "using",
        "answer",
        "fy",
        "usd",
        "year",
    }
    return {w for w in re.findall(r"[A-Za-z][A-Za-z0-9_&-]+", text.lower()) if len(w) > 2 and w not in stop}


def select_nodes(structure: dict[str, Any], question: str, top_k: int = 5) -> list[dict[str, Any]]:
    question_terms = keywords(question)
    scored = []
    for node in flatten_nodes(structure.get("structure", [])):
        title = node.get("title") or ""
        score = len(question_terms & keywords(title))
        if score:
            scored.append((score, node))
    scored.sort(key=lambda item: (-item[0], item[1].get("start_index") or 10**9))
    if not scored:
        return flatten_nodes(structure.get("structure", []))[:top_k]
    return [node for _, node in scored[:top_k]]


def pages_from_nodes(nodes: list[dict[str, Any]], max_pages: int = 8) -> list[int]:
    pages: list[int] = []
    for node in nodes:
        start = node.get("start_index")
        end = node.get("end_index") or start
        if not start:
            continue
        pages.extend(range(int(start), int(end) + 1))
    return sorted(set(pages))[:max_pages]


def extract_pages(pdf_path: Path, pages_one_indexed: list[int]) -> list[dict[str, Any]]:
    doc = fitz.open(pdf_path)
    extracted = []
    for page in pages_one_indexed:
        zero = page - 1
        if 0 <= zero < len(doc):
            extracted.append({"page": page, "text": doc[zero].get_text()})
    return extracted


def answer_with_llm(model: str, question: str, page_text: list[dict[str, Any]]) -> tuple[str, TokenUsage]:
    context = "\n\n".join(f"[PAGE {p['page']}]\n{p['text']}" for p in page_text)
    prompt = f"""Use only the provided document pages to answer the question.
Return a concise answer and cite page numbers.

QUESTION:
{question}

DOCUMENT PAGES:
{context}
"""
    response = completion(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    usage = getattr(response, "usage", None)
    token_usage = TokenUsage(
        input=getattr(usage, "prompt_tokens", None) if usage else None,
        output=getattr(usage, "completion_tokens", None) if usage else None,
        total=getattr(usage, "total_tokens", None) if usage else None,
    )
    return response.choices[0].message.content, token_usage


def run_pageindex_qa(
    question: BenchmarkQuestion,
    structure_path: Path,
    pdf_path: Path,
    *,
    model: str | None,
    no_llm: bool = False,
) -> BenchmarkResult:
    started = time.perf_counter()
    structure = load_structure(structure_path)
    selected = select_nodes(structure, question.question)
    pages = pages_from_nodes(selected)
    page_text = extract_pages(pdf_path, pages)

    citations = [
        Citation(
            document_id=question.doc_name,
            page=node.get("start_index"),
            section=node.get("title"),
            metadata={
                "node_id": node.get("node_id"),
                "start_index": node.get("start_index"),
                "end_index": node.get("end_index"),
            },
        )
        for node in selected
    ]
    trace = [
        RetrievalTraceStep(
            step=i + 1,
            action="select_tree_node",
            target=node.get("title", ""),
            metadata={
                "node_id": node.get("node_id"),
                "start_index": node.get("start_index"),
                "end_index": node.get("end_index"),
            },
        )
        for i, node in enumerate(selected)
    ]

    if no_llm:
        answer = f"Selected {len(selected)} PageIndex nodes and {len(page_text)} pages for answering."
        token_usage = TokenUsage()
    else:
        if not model:
            raise ValueError("model is required unless --no-llm is set")
        answer, token_usage = answer_with_llm(model, question.question, page_text)

    latency_ms = int((time.perf_counter() - started) * 1000)
    return BenchmarkResult(
        method="pageindex_tree_qa",
        question_id=question.question_id,
        question=question.question,
        answer=answer,
        citations=citations,
        retrieval_trace=trace,
        token_usage=token_usage,
        latency_ms=latency_ms,
        metadata={
            "structure_path": str(structure_path),
            "pdf_path": str(pdf_path),
            "selected_pages_one_indexed": pages,
            "adapter_mode": "tree_node_selection",
            "llm_enabled": not no_llm,
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Answer one benchmark question using a PageIndex structure.")
    parser.add_argument("--questions", type=Path, required=True)
    parser.add_argument("--question-id", required=True)
    parser.add_argument("--structure", type=Path, required=True)
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--model", default=None)
    parser.add_argument("--no-llm", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    question = load_question(args.questions, args.question_id)
    result = run_pageindex_qa(
        question,
        args.structure,
        args.pdf,
        model=args.model,
        no_llm=args.no_llm,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(result.model_dump_json(indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

