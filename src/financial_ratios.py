"""Common financial ratio calculations."""

from math import isfinite


def _ratio(numerator: float, denominator: float, denominator_name: str) -> float:
    top = float(numerator)
    bottom = float(denominator)
    if not isfinite(top) or not isfinite(bottom):
        raise ValueError("ratio inputs must be finite")
    if bottom == 0:
        raise ValueError(f"{denominator_name} must not be zero")
    return top / bottom


def gross_margin(gross_profit: float, revenue: float) -> float:
    """Gross profit divided by revenue."""
    return _ratio(gross_profit, revenue, "revenue")


def operating_margin(operating_income: float, revenue: float) -> float:
    """Operating income divided by revenue."""
    return _ratio(operating_income, revenue, "revenue")


def net_margin(net_income: float, revenue: float) -> float:
    """Net income divided by revenue."""
    return _ratio(net_income, revenue, "revenue")


def return_on_assets(net_income: float, average_total_assets: float) -> float:
    """Net income divided by average total assets."""
    return _ratio(net_income, average_total_assets, "average_total_assets")


def return_on_equity(net_income: float, average_shareholders_equity: float) -> float:
    """Net income divided by average shareholders' equity."""
    return _ratio(net_income, average_shareholders_equity, "average_shareholders_equity")


def current_ratio(current_assets: float, current_liabilities: float) -> float:
    """Current assets divided by current liabilities."""
    return _ratio(current_assets, current_liabilities, "current_liabilities")


def quick_ratio(
    cash: float,
    marketable_securities: float,
    accounts_receivable: float,
    current_liabilities: float,
) -> float:
    """Quick assets divided by current liabilities."""
    quick_assets = float(cash) + float(marketable_securities) + float(accounts_receivable)
    return _ratio(quick_assets, current_liabilities, "current_liabilities")


def debt_to_equity(total_debt: float, shareholders_equity: float) -> float:
    """Total debt divided by shareholders' equity."""
    return _ratio(total_debt, shareholders_equity, "shareholders_equity")


def interest_coverage(ebit: float, interest_expense: float) -> float:
    """Earnings before interest and tax divided by interest expense."""
    return _ratio(ebit, interest_expense, "interest_expense")


def asset_turnover(revenue: float, average_total_assets: float) -> float:
    """Revenue divided by average total assets."""
    return _ratio(revenue, average_total_assets, "average_total_assets")

