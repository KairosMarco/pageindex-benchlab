from __future__ import annotations

from benchlab.schemas import BenchmarkQuestion, GoldEvidence
from pipelines.structured_rag.adapter import PageText, build_structured_index, retrieve_nodes, run_structured_rag_qa


def make_question() -> BenchmarkQuestion:
    return BenchmarkQuestion(
        question_id="q_structured",
        source_id="source_structured",
        dataset="financebench",
        company="ExampleCo",
        doc_name="EXAMPLE_10K",
        doc_type="10k",
        doc_period=2024,
        question="What did the legal proceedings say about litigation claims?",
        gold_answer="The company disclosed legal proceedings and litigation claims.",
        gold_evidence=[
            GoldEvidence(
                document_id="EXAMPLE_10K",
                page_zero_indexed=1,
                page_one_indexed=2,
                text="Legal proceedings",
            )
        ],
    )


def test_build_structured_index_maps_entities_to_nodes() -> None:
    pages = [
        PageText(page=1, text="BUSINESS\nExampleCo sells products and services."),
        PageText(page=2, text="LEGAL PROCEEDINGS\nExampleCo faces litigation claims in California."),
    ]

    index = build_structured_index(pages, node_words=40, overlap=5)

    assert index.nodes
    assert "exampleco" in index.entity_to_nodes
    assert any(node.title == "LEGAL PROCEEDINGS" for node in index.nodes)
    assert index.entity_edges


def test_retrieve_nodes_prefers_matching_structural_section() -> None:
    question = make_question()
    pages = [
        PageText(page=1, text="BUSINESS\nExampleCo sells products and services."),
        PageText(page=2, text="LEGAL PROCEEDINGS\nExampleCo faces litigation claims in California."),
    ]
    index = build_structured_index(pages, node_words=40, overlap=5)

    retrieved = retrieve_nodes(question, index, retrieve_top_k=3)

    assert retrieved
    assert retrieved[0]["node"].page == 2
    assert "legal" in retrieved[0]["matched_terms"]


def test_run_structured_rag_qa_outputs_benchmark_result(monkeypatch) -> None:
    question = make_question()
    pages = [
        PageText(page=1, text="BUSINESS\nExampleCo sells products and services."),
        PageText(page=2, text="LEGAL PROCEEDINGS\nExampleCo faces litigation claims in California."),
    ]

    monkeypatch.setattr("pipelines.structured_rag.adapter.extract_pages", lambda _path: pages)

    result = run_structured_rag_qa(question, pdf_path="unused.pdf")

    assert result.method == "structured_tree_graph_rag"
    assert result.question_id == "q_structured"
    assert result.citations[0].page == 2
    assert result.retrieval_trace[0].action == "build_document_tree"
    assert result.metadata["entity_count"] > 0
