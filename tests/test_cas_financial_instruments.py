"""Tests for CAS 22 classification and journal entries."""

import unittest

from src.cas_financial_instruments import (
    classify_financial_asset,
    effective_interest_entry,
    fair_value_change_entry,
    impairment_entry,
    initial_recognition_entry,
)
from src.sppi import assess_sppi


class CASFinancialInstrumentTests(unittest.TestCase):
    def test_sppi_pass_and_hold_to_collect_is_amortized_cost(self) -> None:
        result = classify_financial_asset(assess_sppi(), "hold_to_collect")
        self.assertEqual(result, "amortized_cost")

    def test_sppi_pass_and_collect_and_sell_is_fvoci(self) -> None:
        result = classify_financial_asset(assess_sppi(), "collect_and_sell")
        self.assertEqual(result, "fvoci_debt")

    def test_sppi_failure_is_fvtpl(self) -> None:
        result = classify_financial_asset(
            assess_sppi(equity_or_commodity_linked=True), "hold_to_collect"
        )
        self.assertEqual(result, "fvtpl")

    def test_review_outcome_blocks_automatic_classification(self) -> None:
        with self.assertRaisesRegex(ValueError, "requires review"):
            classify_financial_asset(assess_sppi(non_recourse=True), "hold_to_collect")

    def test_initial_entry_capitalizes_costs_except_fvtpl(self) -> None:
        amortized = initial_recognition_entry("amortized_cost", 1_000, 10)
        fvtpl = initial_recognition_entry("fvtpl", 1_000, 10)
        self.assertEqual(amortized.lines[0].debit, 1_010)
        self.assertEqual(fvtpl.lines[0].debit, 1_000)
        self.assertEqual(fvtpl.lines[1].account, "投资收益")

    def test_effective_interest_entry_is_balanced(self) -> None:
        entry = effective_interest_entry("amortized_cost", 1_000, 0.05, 40)
        self.assertEqual(entry.total, 50)
        self.assertEqual(entry.lines[-1].credit, 50)

    def test_fvoci_fair_value_gain_goes_to_oci(self) -> None:
        entry = fair_value_change_entry("fvoci_debt", 25)
        self.assertEqual(entry.lines[1].account, "其他综合收益")

    def test_amortized_cost_impairment_uses_loss_allowance(self) -> None:
        entry = impairment_entry("amortized_cost", 30)
        self.assertEqual(entry.lines[1].account, "债权投资减值准备")


if __name__ == "__main__":
    unittest.main()

