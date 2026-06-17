from __future__ import annotations

import unittest

from scripts.run_llamaindex_expanded_llm_diagnostics import artifact_stem
from pipelines.vector_rag.adapter import (
    DEFAULT_ANSWER_PROMPT_MODE,
    FINANCE_REASONING_ANSWER_PROMPT_MODE,
    FINANCE_REASONING_V2_ANSWER_PROMPT_MODE,
    FINANCE_REASONING_V3_ANSWER_PROMPT_MODE,
    build_answer_prompt,
)


class AnswerPromptModeTests(unittest.TestCase):
    def test_default_prompt_preserves_historical_instruction(self) -> None:
        prompt = build_answer_prompt(
            "What is revenue?",
            "[PAGE 1 | CHUNK p1_c0]\nRevenue was $10.",
            prompt_mode=DEFAULT_ANSWER_PROMPT_MODE,
        )

        self.assertIn("Use only the retrieved document chunks", prompt)
        self.assertIn("Return a concise answer", prompt)
        self.assertNotIn("strict finance reasoning", prompt)

    def test_finance_reasoning_prompt_adds_concept_checks(self) -> None:
        prompt = build_answer_prompt(
            "Is CVS Health a capital-intensive business based on FY2022 data?",
            "[PAGE 108 | CHUNK p108_c0]\nROA was 1.82%.",
            prompt_mode=FINANCE_REASONING_ANSWER_PROMPT_MODE,
        )

        self.assertIn("strict finance reasoning", prompt)
        self.assertIn("capital-intensive questions", prompt)
        self.assertIn("low ROA", prompt)
        self.assertIn("working-capital questions", prompt)
        self.assertIn("$389 million = $0.389 billion", prompt)

    def test_unknown_prompt_mode_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            build_answer_prompt("Question?", "Context", prompt_mode="unknown")

    def test_finance_reasoning_v2_adds_asset_intensity_definition(self) -> None:
        prompt = build_answer_prompt(
            "Is CVS Health a capital-intensive business based on FY2022 data?",
            "[PAGE 110 | CHUNK p110_c0]\nTotal assets were $228.3 billion.",
            prompt_mode=FINANCE_REASONING_V2_ANSWER_PROMPT_MODE,
        )

        self.assertIn("broad asset-intensity definition", prompt)
        self.assertIn("low ROA and a large total asset base", prompt)
        self.assertIn("caveat rather than as a standalone negative conclusion", prompt)
        self.assertIn('generally be "Yes, with caveats"', prompt)

    def test_finance_reasoning_v3_adds_billion_rounding_policy(self) -> None:
        prompt = build_answer_prompt(
            "How much (in USD billions) did American Water Works pay out in cash dividends for FY2020?",
            "[PAGE 86 | CHUNK p86_c0]\nDividends paid (389).",
            prompt_mode=FINANCE_REASONING_V3_ANSWER_PROMPT_MODE,
        )

        self.assertIn("benchmark-style rounded billion answer first", prompt)
        self.assertIn('"$0.40 billion ($389 million)"', prompt)
        self.assertIn("rather than only", prompt)

    def test_non_default_prompt_mode_gets_separate_artifact_stem(self) -> None:
        stem = artifact_stem(
            questions=__import__("pathlib").Path("expanded_questions_25.jsonl"),
            variant_suffix="concept_v2",
            rerank_top_k=3,
            answer_prompt_mode=FINANCE_REASONING_ANSWER_PROMPT_MODE,
        )

        self.assertEqual(stem, "qa_llm_expanded_25_concept_v2_r3_finance_reasoning_v1")


if __name__ == "__main__":
    unittest.main()
