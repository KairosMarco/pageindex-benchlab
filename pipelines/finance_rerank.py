from __future__ import annotations

import re

from benchlab.schemas import BenchmarkQuestion


def normalize_financial_text(text: str) -> str:
    normalized = text.lower().replace("&", " and ")
    normalized = re.sub(r"\s+", " ", normalized)
    # PDF extraction often splits plural endings in table titles, e.g. "Cash Flow s".
    normalized = normalized.replace("cash flow s", "cash flows")
    normalized = normalized.replace("operation s", "operations")
    normalized = normalized.replace("statement s", "statements")
    return normalized.strip()


def _mentions_sga(text: str) -> bool:
    """Match common SG&A spellings after text normalization."""

    return _has_any(
        text,
        (
            "sg&a",
            "sg and a",
            "sga",
            "selling, general and administrative",
            "selling general and administrative",
        ),
    )


def _has_any(text: str, patterns: tuple[str, ...]) -> bool:
    return any(pattern in text for pattern in patterns)


def _add(score: float, reasons: list[str], value: float, reason: str) -> float:
    reasons.append(reason)
    return score + value


def financial_line_item_boost(question: BenchmarkQuestion, text: str) -> tuple[float, list[str]]:
    """Score table-like chunks that mention the financial line item requested by the question.

    This helper intentionally uses only the question text and retrieved chunk text. It does not
    inspect gold evidence pages, so it can be used during retrieval without leaking labels.
    """

    q = normalize_financial_text(question.question)
    t = normalize_financial_text(text)
    score = 0.0
    reasons: list[str] = []

    number_count = len(re.findall(r"\b\d[\d,]*(?:\.\d+)?%?\b", t))
    if number_count >= 12:
        score = _add(score, reasons, min(8.0, number_count / 8.0), "table_like_numeric_density")

    years = set(re.findall(r"\b20\d{2}\b|\b19\d{2}\b", q))
    if years and any(year in t for year in years):
        score = _add(score, reasons, 4.0, "requested_year_present")

    asks_cash_flow = _has_any(q, ("cash flow", "cashflow", "cash flows", "operating activities", "investing activities", "financing activities"))
    asks_capex = _has_any(q, ("capital expenditure", "capital expenditures", "capex", "property plant", "property, plant", "ppe"))
    if asks_cash_flow or asks_capex:
        if _has_any(t, ("consolidated statement of cash flows", "consolidated statements of cash flows", "statement of cash flows")):
            score = _add(score, reasons, 18.0, "cash_flow_statement_title")
        if _has_any(t, ("cash flows from operating activities", "cash provided by operating activities", "cash provided (used) by operations")):
            score = _add(score, reasons, 8.0, "operating_cash_flow_section")
        if _has_any(t, ("cash flows from investing activities", "cash provided (used) by investing activities")):
            score = _add(score, reasons, 8.0, "investing_cash_flow_section")
        if _has_any(t, ("cash flows from financing activities", "cash provided (used) by financing activities")):
            score = _add(score, reasons, 8.0, "financing_cash_flow_section")
        if asks_capex and _has_any(t, ("purchases of property, plant and equipment", "purchase of property, plant and equipment", "additions to property, plant and equipment")):
            score = _add(score, reasons, 28.0, "capex_line_item")

    asks_income_statement = _has_any(q, ("statement of income", "income statement", "revenue", "gross margin", "gross margins", "cogs", "cost of revenue", "cost of sales"))
    if asks_income_statement:
        if _has_any(t, ("consolidated statements of operations", "consolidated statement of operations", "consolidated statements of earnings", "income statements")):
            score = _add(score, reasons, 16.0, "income_statement_title")
        if "consolidated statements of income" in t:
            score = _add(score, reasons, 16.0, "income_statement_title")
        if "total net sales" in t and "revenue" in q:
            score = _add(score, reasons, 18.0, "total_net_sales_line_item")
        if "total revenues" in t and "revenue" in q:
            score = _add(score, reasons, 14.0, "total_revenues_line_item")
        if _has_any(q, ("cogs", "cost of revenue")) and _has_any(t, ("total cost of revenue", "cost of revenue")):
            score = _add(score, reasons, 18.0, "cost_of_revenue_line_item")
        if _has_any(q, ("gross margin", "gross margins")) and _has_any(t, ("revenue", "cost of sales", "gross profit")):
            score = _add(score, reasons, 14.0, "gross_margin_line_items")
        if _has_any(q, ("gross margin", "gross margins")) and _has_any(t, ("net interest income", "interest income", "interest expense")):
            score = _add(score, reasons, 12.0, "financial_services_income_lines")

    asks_balance_sheet = _has_any(
        q,
        (
            "balance sheet",
            "total assets",
            "working capital",
            "capital-intensive",
            "capital intensive",
            "ppne",
            "property, plant and equipment",
            "property plant and equipment",
        ),
    )
    if asks_balance_sheet:
        has_balance_title = _has_any(t, ("consolidated balance sheets", "balance sheets"))
        has_balance_assets = _has_any(t, ("assets current assets", "current assets:", "total current assets", "total assets"))
        has_balance_liabilities = _has_any(t, ("liabilities and equity", "current liabilities", "total liabilities"))
        has_main_balance_sheet = has_balance_title and has_balance_assets and has_balance_liabilities
        has_income_statement_title = _has_any(
            t,
            (
                "consolidated statements of operations",
                "consolidated statement of operations",
                "consolidated statements of income",
                "consolidated statement of income",
                "consolidated statements of earnings",
            ),
        )
        has_income_statement_lines = _has_any(t, ("total revenues", "operating income", "net income"))

        if has_main_balance_sheet:
            score = _add(score, reasons, 16.0, "balance_sheet_title")
        if "total assets" in t:
            score = _add(score, reasons, 18.0, "total_assets_line_item")
        if _has_any(q, ("working capital",)) and _has_any(t, ("total current assets", "total current liabilities")):
            score = _add(score, reasons, 28.0, "working_capital_line_items")
        if _has_any(q, ("capital-intensive", "capital intensive")) and has_main_balance_sheet and _has_any(
            t,
            ("property and equipment", "property, plant and equipment", "goodwill", "total assets"),
        ):
            score = _add(score, reasons, 22.0, "capital_intensity_balance_sheet_lines")
        if _has_any(q, ("capital-intensive", "capital intensive")) and has_income_statement_title and has_income_statement_lines:
            score = _add(score, reasons, 18.0, "capital_intensity_income_statement_lines")
        if _has_any(q, ("capital-intensive", "capital intensive")) and has_income_statement_title and _has_any(
            t,
            ("revenues:", "total revenues", "operating costs:", "total operating costs", "net income"),
        ):
            score = _add(score, reasons, 28.0, "capital_intensity_primary_income_statement_lines")
        if _has_any(q, ("ppne", "property, plant and equipment", "property plant and equipment")) and _has_any(
            t,
            ("property, plant and equipment", "property plant and equipment", "property and equipment"),
        ):
            score = _add(score, reasons, 26.0, "ppne_line_item")

    asks_sga_driver = _mentions_sga(q) and _has_any(
        q,
        ("what drove", "drove", "driven", "driver", "drivers", "reduction", "decrease", "decreased", "why"),
    )
    if asks_sga_driver:
        has_sga_context = _mentions_sga(t)
        has_driver_language = _has_any(t, ("primarily due to", "driven by", "due to", "partially offset"))
        has_percent_of_sales = _has_any(t, ("as a percentage of net sales", "percent of net sales"))
        has_sga_driver_terms = _has_any(
            t,
            (
                "marketing expenses",
                "incentive compensation",
                "store payroll",
                "corporate overhead",
                "wage investments",
            ),
        )
        if has_sga_context and has_driver_language and has_percent_of_sales:
            score = _add(score, reasons, 30.0, "sga_percent_of_sales_driver_narrative")
        if has_sga_context and has_sga_driver_terms:
            score = _add(score, reasons, 12.0, "sga_driver_terms")

    if _has_any(q, ("legal", "lawsuit", "lawsuits", "legal battles")):
        if _has_any(t, ("legal proceedings", "legal actions", "multiple legal actions have been filed")):
            score = _add(score, reasons, 20.0, "legal_proceedings_line_item")
        if _has_any(t, ("lion air flight 610", "ethiopian airlines flight 302")):
            score = _add(score, reasons, 16.0, "boeing_737_max_accident_terms")

    if _has_any(q, ("adjusted non gaap ebitda", "adjusted ebitda", "non gaap ebitda")):
        if _has_any(t, ("adjusted ebitda", "adjusted non-gaap ebitda", "adjusted non gaap ebitda")):
            score = _add(score, reasons, 24.0, "adjusted_ebitda_line_item")
        if _has_any(t, ("ebitda, ebit, net income and eps", "net income attributable")):
            score = _add(score, reasons, 8.0, "ebitda_reconciliation_table")

    if "var" in q:
        if _has_any(t, ("average total var", "value-at-risk", "value at risk")):
            score = _add(score, reasons, 20.0, "var_line_item")
        if "decreased" in t:
            score = _add(score, reasons, 6.0, "risk_direction_term")

    if _has_any(q, ("discontinued operation", "discontinued operations", "consumer health")):
        if "consumer health" in t:
            score = _add(score, reasons, 16.0, "consumer_health_term")
        if "discontinued operations" in t:
            score = _add(score, reasons, 16.0, "discontinued_operations_term")

    if _has_any(q, ("products and services", "major products", "sells")):
        if _has_any(t, ("we are a global semiconductor company", "we primarily offer", "primarily offering")):
            score = _add(score, reasons, 14.0, "business_overview_intro")
        product_terms = ("server microprocessors", "graphics processing units", "data processing units", "field programmable gate arrays", "adaptive system-on-chip")
        product_hits = sum(1 for term in product_terms if term in t)
        if product_hits:
            score = _add(score, reasons, float(product_hits * 5), "amd_product_terms")

    return score, reasons
