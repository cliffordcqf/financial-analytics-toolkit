"""Tests for capital budgeting metrics."""

import unittest

from src.investment_metrics import (
    internal_rate_of_return,
    net_present_value,
    payback_period,
)


class InvestmentMetricTests(unittest.TestCase):
    def test_net_present_value_includes_time_zero_cash_flow(self) -> None:
        result = net_present_value(0.10, [-1000, 400, 400, 400])
        self.assertAlmostEqual(result, -5.259204, places=6)

    def test_internal_rate_of_return(self) -> None:
        result = internal_rate_of_return([-1000, 400, 400, 400])
        self.assertAlmostEqual(result, 0.097010, places=5)

    def test_irr_requires_mixed_cash_flow_signs(self) -> None:
        with self.assertRaisesRegex(ValueError, "negative and positive"):
            internal_rate_of_return([100, 200, 300])

    def test_payback_period_interpolates_partial_period(self) -> None:
        self.assertAlmostEqual(payback_period([-1000, 300, 400, 500]), 2.6)

    def test_payback_period_rejects_unrecovered_investment(self) -> None:
        with self.assertRaisesRegex(ValueError, "not paid back"):
            payback_period([-1000, 100, 100])


if __name__ == "__main__":
    unittest.main()

