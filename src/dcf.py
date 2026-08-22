"""Discounted cash flow valuation utilities."""

from collections.abc import Iterable
from math import isfinite


def _finite_number(value: float, name: str) -> float:
    number = float(value)
    if not isfinite(number):
        raise ValueError(f"{name} must be finite")
    return number


def terminal_value(
    final_free_cash_flow: float,
    discount_rate: float,
    terminal_growth_rate: float,
) -> float:
    """Calculate terminal value using the Gordon growth model."""
    cash_flow = _finite_number(final_free_cash_flow, "final_free_cash_flow")
    discount = _finite_number(discount_rate, "discount_rate")
    growth = _finite_number(terminal_growth_rate, "terminal_growth_rate")
    if discount <= growth:
        raise ValueError("discount_rate must be greater than terminal_growth_rate")
    return cash_flow * (1 + growth) / (discount - growth)


def enterprise_value(
    free_cash_flows: Iterable[float],
    discount_rate: float,
    terminal_growth_rate: float,
) -> float:
    """Return enterprise value from forecast cash flows and terminal value."""
    cash_flows = [
        _finite_number(value, f"free_cash_flows[{index}]")
        for index, value in enumerate(free_cash_flows)
    ]
    if not cash_flows:
        raise ValueError("free_cash_flows must contain at least one forecast")

    discount = _finite_number(discount_rate, "discount_rate")
    if discount <= -1:
        raise ValueError("discount_rate must be greater than -1")

    present_value = sum(
        cash_flow / (1 + discount) ** year
        for year, cash_flow in enumerate(cash_flows, start=1)
    )
    terminal = terminal_value(cash_flows[-1], discount, terminal_growth_rate)
    return present_value + terminal / (1 + discount) ** len(cash_flows)


def equity_value(
    enterprise_value_amount: float,
    cash_and_equivalents: float = 0,
    total_debt: float = 0,
    minority_interest: float = 0,
) -> float:
    """Bridge enterprise value to equity value."""
    enterprise = _finite_number(enterprise_value_amount, "enterprise_value_amount")
    cash = _finite_number(cash_and_equivalents, "cash_and_equivalents")
    debt = _finite_number(total_debt, "total_debt")
    minority = _finite_number(minority_interest, "minority_interest")
    return enterprise + cash - debt - minority

