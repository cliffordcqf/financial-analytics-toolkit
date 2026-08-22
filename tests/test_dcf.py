"""Tests for discounted cash flow calculations."""

import unittest

from src.dcf import enterprise_value, equity_value, terminal_value


class DcfTests(unittest.TestCase):
    def test_terminal_value_uses_gordon_growth(self) -> None:
        self.assertAlmostEqual(terminal_value(100, 0.10, 0.03), 1471.428571, places=6)

    def test_enterprise_value_discounts_forecast_and_terminal_value(self) -> None:
        value = enterprise_value([100, 110, 121], 0.10, 0.03)
        self.assertAlmostEqual(value, 1610.389610, places=6)

    def test_equity_value_bridge(self) -> None:
        self.assertEqual(equity_value(1000, cash_and_equivalents=100, total_debt=300), 800)

    def test_discount_rate_must_exceed_growth_rate(self) -> None:
        with self.assertRaisesRegex(ValueError, "discount_rate must be greater"):
            terminal_value(100, 0.03, 0.03)

    def test_forecast_must_not_be_empty(self) -> None:
        with self.assertRaisesRegex(ValueError, "at least one"):
            enterprise_value([], 0.10, 0.03)


if __name__ == "__main__":
    unittest.main()

