"""Tests for fixed-income analytics."""

import unittest

from src.fixed_income import (
    bond_price,
    convexity,
    macaulay_duration,
    modified_duration,
    yield_to_maturity,
)


class FixedIncomeTests(unittest.TestCase):
    def test_par_bond_prices_at_face_value(self) -> None:
        self.assertAlmostEqual(bond_price(1_000, 0.05, 5, 0.05), 1_000)

    def test_discount_and_premium_prices(self) -> None:
        self.assertLess(bond_price(1_000, 0.04, 5, 0.06), 1_000)
        self.assertGreater(bond_price(1_000, 0.06, 5, 0.04), 1_000)

    def test_yield_to_maturity_recovers_input_yield(self) -> None:
        price = bond_price(1_000, 0.045, 7, 0.0575)
        result = yield_to_maturity(price, 1_000, 0.045, 7)
        self.assertAlmostEqual(result, 0.0575, places=8)

    def test_zero_coupon_duration_equals_maturity(self) -> None:
        result = macaulay_duration(1_000, 0.0, 4, 0.05)
        self.assertAlmostEqual(result, 4.0)

    def test_modified_duration_is_below_macaulay_duration(self) -> None:
        macaulay = macaulay_duration(1_000, 0.05, 5, 0.06)
        modified = modified_duration(1_000, 0.05, 5, 0.06)
        self.assertLess(modified, macaulay)
        self.assertAlmostEqual(modified, macaulay / 1.03)

    def test_convexity_is_positive(self) -> None:
        self.assertGreater(convexity(1_000, 0.05, 5, 0.06), 0)

    def test_fractional_payment_period_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "whole payment periods"):
            bond_price(1_000, 0.05, 1.2, 0.05, payments_per_year=2)


if __name__ == "__main__":
    unittest.main()

