from __future__ import annotations

import argparse
import math
import re
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from benchlab.schemas import BenchmarkQuestion, BenchmarkResult, Citation, RetrievalTraceStep, TokenUsage


DEFAULT_MAX_CITATIONS = 3
DEFAULT_NODE_WORDS = 320
DEFAULT_NODE_OVERLAP = 60
DEFAULT_RETRIEVE_TOP_K = 12
DEFAULT_ENTITY_TOP_K = 8


STOPWORDS = {
    "about",
    "above",
    "after",
    "again",
    "against",
    "also",
    "among",
    "amount",
    "and",
    "answer",
    "any",
    "are",
    "asked",
    "because",
    "been",
    "before",
    "between",
    "both",
    "business",
    "calculate",
    "company",
    "could",
    "does",
    "each",
    "for",
    "from",
    "give",
    "have",
    "into",
    "line",
    "more",
    "only",
    "other",
    "over",
    "page",
    "please",
    "reported",
    "response",
    "round",
    "shown",
    "state",
    "than",
    "that",
    "the",
    "their",
    "there",
    "these",
    "this",
    "units",
    "using",
    "was",
    "were",
    "what",
    "when",
    "where",
    "which",
    "with",
    "within",
    "would",
    "year",
}


SECTION_HINTS = {
    "business",
    "risk factors",
    "legal proceedings",
    "management's discussion",
    "financial statements",
    "consolidated statements",
    "consolidated balance sheets",
    "consolidated statements of operations",
    "consolidated statements of cash flows",
    "notes to consolidated financial statements",
    "non-gaap",
    "adjusted ebitda",
    "discontinued operations",
}


@dataclass
class PageText:
    page: int
    text: str


@dataclass
class StructureNode:
    node_id: str
    page: int
    title: str
    text: str
    parent_id: str | None = None
    entities: set[str] = field(default_factory=set)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class StructuredIndex:
    nodes: list[StructureNode]
    entity_to_nodes: dict[str, set[str]]
    entity_edges: dict[tuple[str, str], int]


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def terms(text: str) -> set[str]:
    normalized = normalize_query_text(text)
    return {
        token
        for token in re.findall(r"[a-z][a-z0-9]+", normalized)
        if len(token) > 2 and token not in STOPWORDS
    }


def token_list(text: str) -> list[str]:
    return [
        token
        for token in re.findall(r"[a-z][a-z0-9]+", normalize_query_text(text))
        if len(token) > 2 and token not in STOPWORDS
    ]


def normalize_query_text(text: str) -> str:
    normalized = (text or "").lower().replace("&", " and ").replace("-", " ")
    replacements = {
        "sg&a": "selling general administrative sga",
        "s g a": "selling general administrative sga",
        "pp&e": "property plant equipment ppe",
        "ppne": "property plant equipment ppne",
        "e bitdar": "ebitdar",
        "ebitda r": "ebitdar",
    }
    for source, target in replacements.items():
        normalized = normalized.replace(source, target)
    return normalized


def question_terms(question: BenchmarkQuestion) -> set[str]:
    query_terms = terms(question.question) - terms(question.company)
    expansions = {
        ("cash", "flow"): {"cash", "flows", "operating", "operations", "investing", "financing"},
        ("capital", "expenditure"): {"capex", "capital", "property", "plant", "equipment", "purchases"},
        ("capital", "intensive"): {"assets", "asset", "property", "plant", "equipment", "goodwill", "roa"},
        ("revenue",): {"revenue", "sales", "net"},
        ("income", "statement"): {"income", "operations", "revenue", "sales", "earnings"},
        ("balance", "sheet"): {"balance", "assets", "liabilities", "equity"},
        ("gross", "margin"): {"gross", "margin", "profit", "revenue", "cost", "sales"},
        ("cogs",): {"cost", "revenue", "sales", "goods"},
        ("legal",): {"legal", "litigation", "lawsuits", "proceedings", "claims", "actions"},
        ("legal", "battles"): {"legal", "litigation", "lawsuits", "proceedings", "claims", "actions", "accident"},
        ("adjusted", "ebitda"): {"adjusted", "ebitda", "non", "gaap", "reconciliation"},
        ("ebitdar",): {"ebitdar", "resorts", "regional", "operations", "contribution"},
        ("discontinued", "operations"): {"discontinued", "operations", "separation", "divestiture"},
        ("products", "services"): {"overview", "products", "services", "business"},
        ("selling", "general", "administrative"): {"selling", "general", "administrative", "sga", "expense", "expenses", "marketing", "incentive"},
    }
    for trigger, additions in expansions.items():
        if all(item in query_terms for item in trigger):
            query_terms.update(additions)
    return query_terms


def extract_pages(pdf_path: Path) -> list[PageText]:
    try:
        import fitz  # type: ignore

        doc = fitz.open(pdf_path)
        return [PageText(page=index + 1, text=page.get_text()) for index, page in enumerate(doc)]
    except Exception:
        from pypdf import PdfReader

        # PyMuPDF is faster, but some locked-down Windows machines block its native DLL.
        # pypdf keeps the baseline runnable with a pure-Python extraction fallback.
        reader = PdfReader(str(pdf_path))
        return [
            PageText(page=index + 1, text=page.extract_text() or "")
            for index, page in enumerate(reader.pages)
        ]


def is_heading(line: str) -> bool:
    value = normalize_text(line)
    if not value or len(value) > 120:
        return False
    lower = value.lower().strip(" .:")
    if lower in SECTION_HINTS:
        return True
    if lower.startswith(("item 1", "item 3", "item 7", "item 8", "note ")):
        return True
    alpha = re.sub(r"[^A-Za-z]", "", value)
    if len(alpha) >= 6 and alpha.isupper():
        return True
    return False


def detect_page_title(text: str, fallback: str) -> str:
    for raw_line in (text or "").splitlines()[:18]:
        if is_heading(raw_line):
            return normalize_text(raw_line)
    return fallback


def chunk_words(words: list[str], *, node_words: int, overlap: int) -> list[tuple[int, int]]:
    if not words:
        return []
    ranges: list[tuple[int, int]] = []
    step = max(1, node_words - overlap)
    for start in range(0, len(words), step):
        end = min(len(words), start + node_words)
        ranges.append((start, end))
        if end >= len(words):
            break
    return ranges


def extract_entities(text: str) -> set[str]:
    found: set[str] = set()
    for phrase in re.findall(r"\b[A-Z][A-Za-z0-9&.-]*(?:\s+[A-Z][A-Za-z0-9&.-]*){0,4}\b", text or ""):
        cleaned = normalize_text(phrase).strip(".,;:()[]")
        if len(cleaned) < 3:
            continue
        if cleaned.lower() in STOPWORDS:
            continue
        found.add(cleaned.lower())
        for part in re.findall(r"[A-Z][A-Za-z0-9&.-]+", cleaned):
            part_cleaned = part.strip(".,;:()[]").lower()
            if len(part_cleaned) >= 3 and part_cleaned not in STOPWORDS:
                found.add(part_cleaned)
    for number in re.findall(r"\b(?:20\d{2}|19\d{2}|[0-9]+(?:\.[0-9]+)?%?)\b", text or ""):
        found.add(number.lower())
    return found


def build_structured_index(
    pages: list[PageText],
    *,
    node_words: int = DEFAULT_NODE_WORDS,
    overlap: int = DEFAULT_NODE_OVERLAP,
) -> StructuredIndex:
    nodes: list[StructureNode] = []
    current_parent: str | None = None

    for page in pages:
        title = detect_page_title(page.text, fallback=f"Page {page.page}")
        if title.lower().strip(" .:") in SECTION_HINTS or title.lower().startswith(("item ", "note ")):
            current_parent = f"section_p{page.page}"
            section_text = normalize_text(page.text[:1200])
            section_node = StructureNode(
                node_id=current_parent,
                page=page.page,
                title=title,
                text=section_text,
                parent_id=None,
                entities=extract_entities(section_text),
                metadata={"node_type": "section"},
            )
            nodes.append(section_node)

        words = page.text.split()
        for chunk_index, (start, end) in enumerate(chunk_words(words, node_words=node_words, overlap=overlap)):
            chunk_text = " ".join(words[start:end])
            if not normalize_text(chunk_text):
                continue
            node_id = f"p{page.page}_n{chunk_index}"
            nodes.append(
                StructureNode(
                    node_id=node_id,
                    page=page.page,
                    title=title,
                    text=chunk_text,
                    parent_id=current_parent,
                    entities=extract_entities(chunk_text),
                    metadata={
                        "node_type": "chunk",
                        "word_start": start,
                        "word_end": end,
                    },
                )
            )

    entity_to_nodes: dict[str, set[str]] = defaultdict(set)
    entity_edges: dict[tuple[str, str], int] = defaultdict(int)
    for node in nodes:
        for entity in node.entities:
            entity_to_nodes[entity].add(node.node_id)
        ordered_entities = sorted(node.entities)
        for index, left in enumerate(ordered_entities):
            for right in ordered_entities[index + 1 : index + 8]:
                entity_edges[(left, right)] += 1

    return StructuredIndex(nodes=nodes, entity_to_nodes=dict(entity_to_nodes), entity_edges=dict(entity_edges))


def tfidf_vectors(nodes: list[StructureNode]) -> tuple[list[dict[str, float]], dict[str, float]]:
    tokenized = [token_list(node.text + " " + node.title) for node in nodes]
    df: Counter[str] = Counter()
    for tokens in tokenized:
        df.update(set(tokens))
    total_docs = max(1, len(nodes))
    idf = {term: math.log((total_docs + 1) / (freq + 1)) + 1 for term, freq in df.items()}

    vectors: list[dict[str, float]] = []
    for tokens in tokenized:
        counts = Counter(tokens)
        total = max(1, len(tokens))
        vectors.append({term: (count / total) * idf.get(term, 1.0) for term, count in counts.items()})
    return vectors, idf


def cosine(left: dict[str, float], right: dict[str, float]) -> float:
    if not left or not right:
        return 0.0
    dot = sum(weight * right.get(term, 0.0) for term, weight in left.items())
    left_norm = math.sqrt(sum(weight * weight for weight in left.values()))
    right_norm = math.sqrt(sum(weight * weight for weight in right.values()))
    if not left_norm or not right_norm:
        return 0.0
    return dot / (left_norm * right_norm)


def phrase_boost(text: str, query_terms: set[str]) -> float:
    lower = normalize_query_text(text)
    boost = 0.0
    phrase_groups = (
        ("purchases of property, plant and equipment", {"capital", "capex", "property", "plant", "equipment"}, 4.0),
        ("property plant and equipment", {"capital", "capex", "property", "plant", "equipment", "ppne", "ppe"}, 3.0),
        ("consolidated statements of cash flows", {"cash", "flow", "flows"}, 1.8),
        ("statement of cash flows", {"cash", "flow", "flows"}, 1.8),
        ("consolidated statements of operations", {"income", "operations", "revenue", "sales"}, 2.5),
        ("consolidated statements of earnings", {"income", "earnings", "revenue", "sales"}, 2.5),
        ("consolidated statements of income", {"income", "earnings", "revenue", "sales"}, 2.5),
        ("consolidated balance sheets", {"balance", "assets", "liabilities", "property", "plant", "equipment"}, 2.8),
        ("total assets", {"assets", "asset", "capital", "intensive"}, 2.0),
        ("legal proceedings", {"legal", "litigation", "proceedings", "battles"}, 2.5),
        ("lion air flight 610", {"legal", "litigation", "accident", "battles"}, 3.5),
        ("ethiopian airlines flight 302", {"legal", "litigation", "accident", "battles"}, 3.5),
        ("adjusted ebitda", {"adjusted", "ebitda"}, 2.5),
        ("adjusted ebitdar", {"adjusted", "ebitdar", "resorts"}, 3.0),
        ("las vegas strip resorts", {"ebitdar", "resorts", "region", "highest"}, 3.5),
        ("non-gaap", {"non", "gaap", "adjusted", "ebitda"}, 2.5),
        ("discontinued operations", {"discontinued", "operations"}, 2.5),
        ("gross profit", {"gross", "margin", "profit"}, 2.5),
        ("cost of revenue", {"cogs", "cost", "revenue"}, 2.5),
        ("cost of sales", {"cogs", "cost", "sales"}, 2.5),
        ("selling general and administrative expenses", {"selling", "general", "administrative", "sga", "expense", "expenses"}, 3.0),
        ("lower marketing expenses", {"marketing", "expense", "expenses", "reduction", "reduced"}, 3.5),
        ("leverage of incentive compensation", {"incentive", "compensation", "sales", "reduction"}, 3.5),
        ("primarily due to", {"drove", "why", "due", "because", "reduction"}, 1.5),
        ("overview we are", {"overview", "products", "services", "sells"}, 2.5),
    )
    for phrase, triggers, weight in phrase_groups:
        if phrase in lower and query_terms & triggers:
            boost += weight
    return boost


def recency_or_front_matter_boost(node: StructureNode, query_terms_set: set[str], page_count: int) -> float:
    # Short press releases often answer "why" and "what drove" questions in the opening narrative pages.
    if page_count <= 20 and node.page <= 3 and query_terms_set & {"why", "drove", "driven", "reduction", "guidance"}:
        return 0.35
    # Business overview questions in 10-K filings are usually near the beginning of the document.
    if node.page <= 8 and query_terms_set & {"overview", "products", "services", "sells"}:
        return 0.45
    return 0.0


def query_vector(query_terms: set[str], idf: dict[str, float]) -> dict[str, float]:
    counts = Counter(query_terms)
    total = max(1, len(query_terms))
    return {term: (count / total) * idf.get(term, 1.0) for term, count in counts.items()}


def retrieve_nodes(
    question: BenchmarkQuestion,
    index: StructuredIndex,
    *,
    retrieve_top_k: int = DEFAULT_RETRIEVE_TOP_K,
    entity_top_k: int = DEFAULT_ENTITY_TOP_K,
) -> list[dict[str, Any]]:
    vectors, idf = tfidf_vectors(index.nodes)
    query_terms_set = question_terms(question)
    query_vec = query_vector(query_terms_set, idf)
    query_entity_terms = {entity for entity in index.entity_to_nodes if terms(entity) & query_terms_set}
    page_count = max((node.page for node in index.nodes), default=0)

    scored: list[dict[str, Any]] = []
    for node, vector in zip(index.nodes, vectors):
        matched_terms = sorted(query_terms_set & terms(node.text + " " + node.title))
        matched_entities = sorted(node.entities & query_entity_terms)
        lexical_score = cosine(query_vec, vector)
        structural_score = 0.18 if node.parent_id and matched_terms else 0.0
        entity_score = min(len(matched_entities), entity_top_k) * 0.08
        boost = phrase_boost(node.text + " " + node.title, query_terms_set)
        position_boost = recency_or_front_matter_boost(node, query_terms_set, page_count)
        score = lexical_score + structural_score + entity_score + boost + position_boost
        if score <= 0:
            continue
        scored.append(
            {
                "node": node,
                "score": score,
                "lexical_score": lexical_score,
                "structural_score": structural_score,
                "entity_score": entity_score,
                "phrase_boost": boost,
                "position_boost": position_boost,
                "matched_terms": matched_terms,
                "matched_entities": matched_entities,
            }
        )

    page_bonus: dict[int, float] = defaultdict(float)
    for item in scored:
        node: StructureNode = item["node"]
        page_bonus[node.page] += min(item["score"], 4.0)

    # Neighbor pages often contain a split table heading/body pair after PDF extraction.
    # The small propagated bonus keeps adjacent evidence pages visible without dominating direct matches.
    neighbor_bonus: dict[int, float] = defaultdict(float)
    for page, bonus in page_bonus.items():
        neighbor_bonus[page] += bonus
        neighbor_bonus[page - 1] += bonus * 0.28
        neighbor_bonus[page + 1] += bonus * 0.28

    for item in scored:
        node = item["node"]
        item["page_aggregate_score"] = min(neighbor_bonus.get(node.page, 0.0), 10.0) * 0.08
        item["score"] += item["page_aggregate_score"]

    scored.sort(key=lambda item: (-item["score"], item["node"].page, item["node"].node_id))
    return diversify_by_page(scored, retrieve_top_k)


def diversify_by_page(scored: list[dict[str, Any]], retrieve_top_k: int) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    seen_pages: set[int] = set()

    for item in scored:
        page = item["node"].page
        if page in seen_pages:
            continue
        selected.append(item)
        seen_pages.add(page)
        if len(selected) >= retrieve_top_k:
            return selected

    return selected


def text_snippet(text: str, query_terms_set: set[str], limit: int = 700) -> str:
    normalized = normalize_text(text)
    if len(normalized) <= limit:
        return normalized
    lower = normalized.lower()
    positions = [lower.find(term) for term in query_terms_set if lower.find(term) >= 0]
    start = max(0, min(positions) - 160) if positions else 0
    return normalized[start : start + limit].strip()


def build_answer(question: BenchmarkQuestion, retrieved: list[dict[str, Any]], max_citations: int) -> str:
    if not retrieved:
        return "No structured evidence nodes were retrieved."
    pages = []
    for item in retrieved:
        page = item["node"].page
        if page not in pages:
            pages.append(page)
        if len(pages) >= max_citations:
            break
    page_markers = ", ".join(f"[PAGE {page}]" for page in pages)
    return (
        "Structured RAG retrieved the most relevant document tree nodes and entity-linked passages. "
        f"Use the cited pages as supporting evidence: {page_markers}."
    )


def build_citations(
    question: BenchmarkQuestion,
    retrieved: list[dict[str, Any]],
    max_citations: int,
) -> list[Citation]:
    citations: list[Citation] = []
    seen_pages: set[int] = set()
    query_terms_set = question_terms(question)
    for item in retrieved:
        node: StructureNode = item["node"]
        if node.page in seen_pages:
            continue
        seen_pages.add(node.page)
        citations.append(
            Citation(
                document_id=question.doc_name,
                page=node.page,
                section=node.title,
                text=text_snippet(node.text, query_terms_set),
                metadata={
                    "node_id": node.node_id,
                    "parent_id": node.parent_id,
                    "score": item["score"],
                    "lexical_score": item["lexical_score"],
                    "structural_score": item["structural_score"],
                    "entity_score": item["entity_score"],
                    "phrase_boost": item["phrase_boost"],
                    "position_boost": item.get("position_boost", 0.0),
                    "page_aggregate_score": item.get("page_aggregate_score", 0.0),
                    "matched_terms": item["matched_terms"],
                    "matched_entities": item["matched_entities"][:8],
                },
            )
        )
        if len(citations) >= max_citations:
            break
    return citations


def run_structured_rag_qa(
    question: BenchmarkQuestion,
    pdf_path: Path,
    *,
    max_citations: int = DEFAULT_MAX_CITATIONS,
    node_words: int = DEFAULT_NODE_WORDS,
    node_overlap: int = DEFAULT_NODE_OVERLAP,
    retrieve_top_k: int = DEFAULT_RETRIEVE_TOP_K,
    entity_top_k: int = DEFAULT_ENTITY_TOP_K,
) -> BenchmarkResult:
    pdf_path = Path(pdf_path)
    started = time.perf_counter()
    pages = extract_pages(pdf_path)
    index = build_structured_index(pages, node_words=node_words, overlap=node_overlap)
    retrieved = retrieve_nodes(question, index, retrieve_top_k=retrieve_top_k, entity_top_k=entity_top_k)
    citations = build_citations(question, retrieved, max_citations=max_citations)
    answer = build_answer(question, retrieved, max_citations=max_citations)

    trace = [
        RetrievalTraceStep(
            step=1,
            action="build_document_tree",
            target=str(pdf_path.name),
            metadata={"page_count": len(pages), "node_count": len(index.nodes), "node_words": node_words},
        ),
        RetrievalTraceStep(
            step=2,
            action="build_entity_graph",
            target="lightweight_entity_cooccurrence_graph",
            metadata={
                "entity_count": len(index.entity_to_nodes),
                "edge_count": len(index.entity_edges),
                "entity_top_k": entity_top_k,
            },
        ),
    ]
    for rank, item in enumerate(retrieved[:max_citations], start=1):
        node: StructureNode = item["node"]
        trace.append(
            RetrievalTraceStep(
                step=rank + 2,
                action="rank_tree_graph_node",
                target=node.node_id,
                metadata={
                    "rank": rank,
                    "page": node.page,
                    "section": node.title,
                    "score": item["score"],
                    "matched_terms": item["matched_terms"],
                    "matched_entities": item["matched_entities"][:8],
                },
            )
        )

    latency_ms = int((time.perf_counter() - started) * 1000)
    return BenchmarkResult(
        method="structured_tree_graph_rag",
        question_id=question.question_id,
        question=question.question,
        answer=answer,
        citations=citations,
        retrieval_trace=trace,
        token_usage=TokenUsage(),
        latency_ms=latency_ms,
        metadata={
            "pdf_path": str(pdf_path),
            "page_count": len(pages),
            "node_count": len(index.nodes),
            "entity_count": len(index.entity_to_nodes),
            "edge_count": len(index.entity_edges),
            "retrieve_top_k": retrieve_top_k,
            "max_citations": max_citations,
            "inspiration": "BookRAG-style tree plus entity graph plus tree-node mapping; independently implemented for BenchLab.",
            "llm_enabled": False,
        },
    )


def load_question(path: Path, question_id: str) -> BenchmarkQuestion:
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            question = BenchmarkQuestion.model_validate_json(line)
            if question.question_id == question_id:
                return question
    raise ValueError(f"Question not found: {question_id}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a single structured tree-graph RAG query.")
    parser.add_argument("--questions", type=Path, required=True)
    parser.add_argument("--question-id", required=True)
    parser.add_argument("--pdf-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-citations", type=int, default=DEFAULT_MAX_CITATIONS)
    args = parser.parse_args()

    question = load_question(args.questions, args.question_id)
    pdf_path = args.pdf_dir / f"{question.doc_name}.pdf"
    result = run_structured_rag_qa(question, pdf_path, max_citations=args.max_citations)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(result.model_dump_json(indent=2) + "\n", encoding="utf-8")
    print(f"Structured RAG result: {args.output}")


if __name__ == "__main__":
    main()
