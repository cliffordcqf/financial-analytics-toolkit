"""Capital budgeting and investment decision metrics."""

from collections.abc import Iterable
from math import isfinite


def _cash_flow_series(cash_flows: Iterable[float]) -> list[float]:
    values = [float(value) for value in cash_flows]
    if not values:
        raise ValueError("cash_flows must contain at least one value")
    if not all(isfinite(value) for value in values):
        raise ValueError("cash_flows must contain only finite values")
    return values


def net_present_value(discount_rate: float, cash_flows: Iterable[float]) -> float:
    """Return NPV, treating the first cash flow as occurring at time zero."""
    rate = float(discount_rate)
    if not isfinite(rate) or rate <= -1:
        raise ValueError("discount_rate must be finite and greater than -1")
    values = _cash_flow_series(cash_flows)
    return sum(value / (1 + rate) ** period for period, value in enumerate(values))


def internal_rate_of_return(
    cash_flows: Iterable[float],
    *,
    tolerance: float = 1e-7,
    max_iterations: int = 200,
) -> float:
    """Estimate IRR with bisection and return it as a decimal rate.

    The series must contain at least one negative and one positive cash flow.
    The function finds a root in the interval (-100%, 1,000,000%).
    """
    values = _cash_flow_series(cash_flows)
    if not any(value < 0 for value in values) or not any(value > 0 for value in values):
        raise ValueError("cash_flows must include both negative and positive values")
    if tolerance <= 0 or not isfinite(tolerance):
        raise ValueError("tolerance must be finite and greater than zero")
    if max_iterations <= 0:
        raise ValueError("max_iterations must be greater than zero")

    low, high = -0.999999, 10_000.0
    low_value = net_present_value(low, values)
    high_value = net_present_value(high, values)
    if low_value * high_value > 0:
        raise ValueError("no IRR found within the supported rate range")

    for _ in range(max_iterations):
        midpoint = (low + high) / 2
        midpoint_value = net_present_value(midpoint, values)
        if abs(midpoint_value) <= tolerance or high - low <= tolerance:
            return midpoint
        if low_value * midpoint_value <= 0:
            high = midpoint
        else:
            low = midpoint
            low_value = midpoint_value
    raise ValueError("IRR did not converge")


def payback_period(cash_flows: Iterable[float]) -> float:
    """Return the simple payback period with fractional-period interpolation."""
    values = _cash_flow_series(cash_flows)
    cumulative = values[0]
    if cumulative >= 0:
        return 0.0

    for period, value in enumerate(values[1:], start=1):
        previous = cumulative
        cumulative += value
        if cumulative >= 0:
            if value <= 0:
                return float(period)
            return (period - 1) + (-previous / value)
    raise ValueError("investment is not paid back by the supplied cash flows")

