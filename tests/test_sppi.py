"""Tests for the IFRS 9 SPPI screening helper."""

import unittest

from src.sppi import assess_sppi


class SPPITests(unittest.TestCase):
    def test_plain_vanilla_loan_passes(self) -> None:
        result = assess_sppi()
        self.assertEqual(result.status, "pass")
        self.assertTrue(result.passes)

    def test_leveraged_return_fails(self) -> None:
        result = assess_sppi(leveraged_returns=True)
        self.assertEqual(result.status, "fail")
        self.assertIn("leveraged", result.reasons[0])

    def test_equity_link_fails(self) -> None:
        result = assess_sppi(equity_or_commodity_linked=True)
        self.assertEqual(result.status, "fail")

    def test_unassessed_modified_time_value_requires_review(self) -> None:
        result = assess_sppi(modified_time_value_of_money=True)
        self.assertEqual(result.status, "review")

    def test_insignificant_assessed_time_value_modification_passes(self) -> None:
        result = assess_sppi(
            modified_time_value_of_money=True,
            modified_time_value_assessed=True,
            modified_time_value_significant=False,
        )
        self.assertEqual(result.status, "pass")

    def test_non_recourse_feature_requires_review(self) -> None:
        result = assess_sppi(non_recourse=True)
        self.assertEqual(result.status, "review")

    def test_investment_linked_contingent_feature_fails(self) -> None:
        result = assess_sppi(
            contingent_feature=True,
            contingent_related_to_basic_lending=False,
            contingent_represents_investment_exposure=True,
        )
        self.assertEqual(result.status, "fail")

    def test_esg_like_feature_can_require_review(self) -> None:
        result = assess_sppi(
            contingent_feature=True,
            contingent_related_to_basic_lending=False,
            contingent_cash_flows_significantly_different=False,
            contingent_represents_investment_exposure=False,
        )
        self.assertEqual(result.status, "review")


if __name__ == "__main__":
    unittest.main()

