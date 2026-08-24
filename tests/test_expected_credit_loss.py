"""Tests for CAS 22 expected credit loss support."""

import unittest

from src.expected_credit_loss import (
    ECLScenario,
    determine_ecl_stage,
    ecl_adjustment_entry,
    interest_revenue_basis,
    loss_horizon,
    probability_weighted_ecl,
)


class ExpectedCreditLossTests(unittest.TestCase):
    def test_stage_determination(self) -> None:
        self.assertEqual(
            determine_ecl_stage(
                significant_increase_in_credit_risk=False, credit_impaired=False
            ),
            "stage_1",
        )
        self.assertEqual(
            determine_ecl_stage(
                significant_increase_in_credit_risk=True, credit_impaired=False
            ),
            "stage_2",
        )
        self.assertEqual(
            determine_ecl_stage(
                significant_increase_in_credit_risk=True, credit_impaired=True
            ),
            "stage_3",
        )

    def test_loss_horizon(self) -> None:
        self.assertEqual(loss_horizon("stage_1"), "12_month")
        self.assertEqual(loss_horizon("stage_2"), "lifetime")
        self.assertEqual(loss_horizon("stage_3"), "lifetime")

    def test_probability_weighted_ecl(self) -> None:
        scenarios = [
            ECLScenario("base", 0.7, 0.02, 0.40, 1_000_000, 0.98),
            ECLScenario("downside", 0.3, 0.08, 0.55, 1_000_000, 0.95),
        ]
        expected = 0.7 * 0.02 * 0.40 * 1_000_000 * 0.98 + 0.3 * 0.08 * 0.55 * 1_000_000 * 0.95
        self.assertAlmostEqual(probability_weighted_ecl(scenarios), expected)

    def test_scenario_weights_must_sum_to_one(self) -> None:
        scenarios = [ECLScenario("base", 0.8, 0.02, 0.40, 1_000)]
        with self.assertRaisesRegex(ValueError, "sum to 1"):
            probability_weighted_ecl(scenarios)

    def test_stage_three_uses_net_carrying_amount(self) -> None:
        self.assertEqual(interest_revenue_basis("stage_3", 1_000, 150), 850)
        self.assertEqual(interest_revenue_basis("stage_2", 1_000, 150), 1_000)

    def test_ecl_increase_entry_is_balanced(self) -> None:
        entry = ecl_adjustment_entry("amortized_cost", 20, 50)
        self.assertEqual(entry.total, 30)
        self.assertEqual(entry.lines[1].account, "债权投资减值准备")

    def test_ecl_reversal_entry_is_balanced(self) -> None:
        entry = ecl_adjustment_entry("fvoci_debt", 50, 30)
        self.assertEqual(entry.total, 20)
        self.assertEqual(entry.lines[0].account, "其他综合收益—信用减值准备")


if __name__ == "__main__":
    unittest.main()

