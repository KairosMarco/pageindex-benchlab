from __future__ import annotations

import unittest

from benchlab.schemas import BenchmarkQuestion
from pipelines.finance_rerank import financial_line_item_boost, normalize_financial_text


def make_question(question: str) -> BenchmarkQuestion:
    return BenchmarkQuestion(
        question_id="unit_001",
        source_id="unit",
        dataset="financebench",
        company="ExampleCo",
        doc_name="EXAMPLE_10K",
        question=question,
        gold_answer="unit",
        gold_evidence=[],
    )


class FinanceRerankTests(unittest.TestCase):
    def test_cash_flow_line_item_receives_boost(self) -> None:
        question = make_question("What were 2018 capital expenditures from the cash flow statement?")
        table_text = """
        Consolidated Statements of Cash Flows
        Purchases of property, plant and equipment 2018 1,577 2017 1,373 2016 1,420
        Net cash provided by operating activities 6,439 6,240 6,662
        """

        score, reasons = financial_line_item_boost(question, table_text)

        self.assertGreater(score, 0.0)
        self.assertIn("cash_flow_statement_title", reasons)
        self.assertIn("capex_line_item", reasons)

    def test_unrelated_narrative_gets_no_specific_boost(self) -> None:
        question = make_question("What were 2018 capital expenditures from the cash flow statement?")
        narrative_text = "The company discusses strategy, markets, customers, and general risk factors."

        score, reasons = financial_line_item_boost(question, narrative_text)

        self.assertEqual(score, 0.0)
        self.assertEqual(reasons, [])

    def test_pdf_extraction_spacing_is_normalized(self) -> None:
        normalized = normalize_financial_text("Consolidated Statement s of Cash Flow s")

        self.assertIn("statements of cash flows", normalized)


if __name__ == "__main__":
    unittest.main()
