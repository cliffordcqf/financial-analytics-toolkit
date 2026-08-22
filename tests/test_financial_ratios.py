"""Tests for financial ratio calculations."""

import unittest

from src.financial_ratios import (
    asset_turnover,
    current_ratio,
    debt_to_equity,
    gross_margin,
    interest_coverage,
    net_margin,
    operating_margin,
    quick_ratio,
    return_on_assets,
    return_on_equity,
)


class FinancialRatioTests(unittest.TestCase):
    def test_profitability_ratios(self) -> None:
        self.assertEqual(gross_margin(40, 100), 0.4)
        self.assertEqual(operating_margin(20, 100), 0.2)
        self.assertEqual(net_margin(10, 100), 0.1)
        self.assertEqual(return_on_assets(10, 200), 0.05)
        self.assertEqual(return_on_equity(10, 100), 0.1)

    def test_liquidity_ratios(self) -> None:
        self.assertEqual(current_ratio(200, 100), 2.0)
        self.assertEqual(quick_ratio(20, 10, 70, 100), 1.0)

    def test_leverage_and_efficiency_ratios(self) -> None:
        self.assertEqual(debt_to_equity(75, 100), 0.75)
        self.assertEqual(interest_coverage(50, 10), 5.0)
        self.assertEqual(asset_turnover(300, 200), 1.5)

    def test_zero_denominator_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "must not be zero"):
            current_ratio(100, 0)


if __name__ == "__main__":
    unittest.main()

