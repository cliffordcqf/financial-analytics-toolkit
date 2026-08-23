"""Tests for return and volatility calculations."""

import math
import unittest

from src.risk_metrics import (
    annualized_volatility,
    downside_deviation,
    historical_volatility,
    log_returns,
    simple_returns,
)


class RiskMetricTests(unittest.TestCase):
    def test_simple_returns(self) -> None:
        result = simple_returns([100, 110, 99])
        self.assertAlmostEqual(result[0], 0.10)
        self.assertAlmostEqual(result[1], -0.10)

    def test_log_returns(self) -> None:
        self.assertAlmostEqual(log_returns([100, 110])[0], math.log(1.1))

    def test_sample_historical_volatility(self) -> None:
        self.assertAlmostEqual(historical_volatility([0.01, 0.03, 0.02]), 0.01)

    def test_population_historical_volatility(self) -> None:
        result = historical_volatility([0.01, 0.03, 0.02], sample=False)
        self.assertAlmostEqual(result, math.sqrt(0.0002 / 3))

    def test_annualized_volatility(self) -> None:
        result = annualized_volatility([0.01, 0.03, 0.02], periods_per_year=252)
        self.assertAlmostEqual(result, 0.01 * math.sqrt(252))

    def test_downside_deviation(self) -> None:
        result = downside_deviation([0.02, -0.01, -0.03, 0.04])
        self.assertAlmostEqual(result, math.sqrt((0.01**2 + 0.03**2) / 4))

    def test_non_positive_prices_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "greater than zero"):
            simple_returns([100, 0])


if __name__ == "__main__":
    unittest.main()

