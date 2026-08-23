"""Cost of capital calculations used in corporate finance."""

from math import isfinite


def _finite(value: float, name: str) -> float:
    number = float(value)
    if not isfinite(number):
        raise ValueError(f"{name} must be finite")
    return number


def cost_of_equity_capm(
    risk_free_rate: float,
    beta: float,
    market_return: float,
) -> float:
    """Return the cost of equity using the capital asset pricing model."""
    risk_free = _finite(risk_free_rate, "risk_free_rate")
    beta_value = _finite(beta, "beta")
    market = _finite(market_return, "market_return")
    if beta_value < 0:
        raise ValueError("beta must be greater than or equal to zero")
    return risk_free + beta_value * (market - risk_free)


def after_tax_cost_of_debt(pre_tax_cost_of_debt: float, tax_rate: float) -> float:
    """Return the effective debt cost after the interest tax shield."""
    debt_cost = _finite(pre_tax_cost_of_debt, "pre_tax_cost_of_debt")
    tax = _finite(tax_rate, "tax_rate")
    if not 0 <= tax <= 1:
        raise ValueError("tax_rate must be between 0 and 1")
    return debt_cost * (1 - tax)


def weighted_average_cost_of_capital(
    market_value_equity: float,
    market_value_debt: float,
    cost_of_equity: float,
    pre_tax_cost_of_debt: float,
    tax_rate: float,
) -> float:
    """Return WACC using market-value capital structure weights."""
    equity = _finite(market_value_equity, "market_value_equity")
    debt = _finite(market_value_debt, "market_value_debt")
    equity_cost = _finite(cost_of_equity, "cost_of_equity")
    if equity < 0 or debt < 0:
        raise ValueError("market values must be greater than or equal to zero")
    total_capital = equity + debt
    if total_capital == 0:
        raise ValueError("total capital must be greater than zero")

    debt_cost = after_tax_cost_of_debt(pre_tax_cost_of_debt, tax_rate)
    equity_weight = equity / total_capital
    debt_weight = debt / total_capital
    return equity_weight * equity_cost + debt_weight * debt_cost

