"""Tests for cost of capital calculations."""

import unittest

from src.capital_cost import (
    after_tax_cost_of_debt,
    cost_of_equity_capm,
    weighted_average_cost_of_capital,
)


class CapitalCostTests(unittest.TestCase):
    def test_cost_of_equity_capm(self) -> None:
        result = cost_of_equity_capm(0.03, 1.2, 0.09)
        self.assertAlmostEqual(result, 0.102)

    def test_after_tax_cost_of_debt(self) -> None:
        self.assertAlmostEqual(after_tax_cost_of_debt(0.05, 0.25), 0.0375)

    def test_weighted_average_cost_of_capital(self) -> None:
        result = weighted_average_cost_of_capital(
            market_value_equity=750,
            market_value_debt=250,
            cost_of_equity=0.10,
            pre_tax_cost_of_debt=0.05,
            tax_rate=0.25,
        )
        self.assertAlmostEqual(result, 0.084375)

    def test_wacc_supports_all_equity_financing(self) -> None:
        result = weighted_average_cost_of_capital(1000, 0, 0.10, 0.05, 0.25)
        self.assertAlmostEqual(result, 0.10)

    def test_tax_rate_must_be_a_decimal_percentage(self) -> None:
        with self.assertRaisesRegex(ValueError, "between 0 and 1"):
            after_tax_cost_of_debt(0.05, 25)

    def test_total_capital_must_be_positive(self) -> None:
        with self.assertRaisesRegex(ValueError, "greater than zero"):
            weighted_average_cost_of_capital(0, 0, 0.10, 0.05, 0.25)


if __name__ == "__main__":
    unittest.main()

