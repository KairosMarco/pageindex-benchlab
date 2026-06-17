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

    def test_concept_questions_boost_main_financial_statements(self) -> None:
        examples = [
            (
                "What drove gross margin change for a financial services company?",
                """
                Consolidated Statements of Income
                Total revenues net of interest expense 52,862 42,380 36,087
                Interest income 12,658 9,033 10,083
                Interest expense 2,763 1,283 2,098
                Net interest income 9,895 7,750 7,985
                """,
                "financial_services_income_lines",
            ),
            (
                "Does the company have positive working capital based on FY2022 data?",
                """
                Consolidated Balance Sheets
                Assets Current assets Total current assets 7,453
                Liabilities and Equity Current liabilities Total current liabilities 5,175
                """,
                "working_capital_line_items",
            ),
            (
                "Is the company a capital-intensive business based on FY2022 data?",
                """
                Consolidated Balance Sheets
                Assets Current assets Total current assets 65,682
                Property and equipment, net 12,873
                Goodwill 78,150
                Total assets 228,275
                Liabilities and Equity Current liabilities Total liabilities 156,960
                """,
                "capital_intensity_balance_sheet_lines",
            ),
            (
                "Did Pfizer grow its PPNE between FY20 and FY21?",
                """
                Consolidated Balance Sheets
                Assets Current assets Total current assets 59,693
                Property, plant and equipment 14,882 13,745
                Liabilities and Equity Current liabilities
                """,
                "ppne_line_item",
            ),
        ]

        for question_text, statement_text, expected_reason in examples:
            with self.subTest(expected_reason=expected_reason):
                score, reasons = financial_line_item_boost(make_question(question_text), statement_text)

                self.assertGreater(score, 0.0)
                self.assertIn(expected_reason, reasons)

    def test_balance_sheet_title_requires_main_statement_context(self) -> None:
        question = make_question("Is CVS Health a capital-intensive business based on FY2022 data?")
        note_text = """
        Notes to Consolidated Financial Statements
        The note references balance sheets and capital gains, but it does not present
        assets, liabilities, total assets, or property and equipment as a main table.
        """

        _, reasons = financial_line_item_boost(question, note_text)

        self.assertNotIn("balance_sheet_title", reasons)
        self.assertNotIn("capital_intensity_balance_sheet_lines", reasons)


if __name__ == "__main__":
    unittest.main()
