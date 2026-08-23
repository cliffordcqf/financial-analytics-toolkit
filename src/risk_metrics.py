"""Return and volatility calculations for financial time series."""

from collections.abc import Iterable
from math import isfinite, log, sqrt


def _series(values: Iterable[float], name: str, minimum: int = 1) -> list[float]:
    numbers = [float(value) for value in values]
    if len(numbers) < minimum:
        raise ValueError(f"{name} must contain at least {minimum} values")
    if not all(isfinite(value) for value in numbers):
        raise ValueError(f"{name} must contain only finite values")
    return numbers


def simple_returns(prices: Iterable[float]) -> list[float]:
    """Calculate period-over-period arithmetic returns from positive prices."""
    values = _series(prices, "prices", minimum=2)
    if any(price <= 0 for price in values):
        raise ValueError("prices must be greater than zero")
    return [current / previous - 1 for previous, current in zip(values, values[1:])]


def log_returns(prices: Iterable[float]) -> list[float]:
    """Calculate continuously compounded returns from positive prices."""
    values = _series(prices, "prices", minimum=2)
    if any(price <= 0 for price in values):
        raise ValueError("prices must be greater than zero")
    return [log(current / previous) for previous, current in zip(values, values[1:])]


def historical_volatility(returns: Iterable[float], *, sample: bool = True) -> float:
    """Return sample (default) or population standard deviation of returns."""
    values = _series(returns, "returns", minimum=2 if sample else 1)
    mean = sum(values) / len(values)
    denominator = len(values) - 1 if sample else len(values)
    variance = sum((value - mean) ** 2 for value in values) / denominator
    return sqrt(variance)


def annualized_volatility(
    returns: Iterable[float],
    periods_per_year: int = 252,
    *,
    sample: bool = True,
) -> float:
    """Annualize periodic volatility using the square-root-of-time rule."""
    if not isinstance(periods_per_year, int) or periods_per_year <= 0:
        raise ValueError("periods_per_year must be a positive integer")
    return historical_volatility(returns, sample=sample) * sqrt(periods_per_year)


def downside_deviation(
    returns: Iterable[float],
    minimum_acceptable_return: float = 0.0,
) -> float:
    """Return root mean squared shortfall below a target periodic return."""
    values = _series(returns, "returns")
    target = float(minimum_acceptable_return)
    if not isfinite(target):
        raise ValueError("minimum_acceptable_return must be finite")
    squared_shortfalls = [min(value - target, 0.0) ** 2 for value in values]
    return sqrt(sum(squared_shortfalls) / len(values))

