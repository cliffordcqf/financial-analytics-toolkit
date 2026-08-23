"""Financial analytics toolkit."""

from .capital_cost import (
    after_tax_cost_of_debt,
    cost_of_equity_capm,
    weighted_average_cost_of_capital,
)
from .carbon_accounting import (
    emissions_from_activity,
    emissions_from_sources,
    emissions_intensity,
    emissions_reduction,
    greenhouse_gas_inventory,
    scope_2_emissions,
)
from .cas_financial_instruments import (
    JournalEntry,
    JournalLine,
    classify_financial_asset,
    effective_interest_entry,
    fair_value_change_entry,
    impairment_entry,
    initial_recognition_entry,
)
from .dcf import enterprise_value, equity_value, terminal_value
from .investment_metrics import internal_rate_of_return, net_present_value, payback_period
from .risk_metrics import (
    annualized_volatility,
    downside_deviation,
    historical_volatility,
    log_returns,
    simple_returns,
)
from .sppi import SPPIAssessment, assess_sppi

__all__ = [
    "after_tax_cost_of_debt",
    "annualized_volatility",
    "assess_sppi",
    "classify_financial_asset",
    "cost_of_equity_capm",
    "downside_deviation",
    "effective_interest_entry",
    "emissions_from_activity",
    "emissions_from_sources",
    "emissions_intensity",
    "emissions_reduction",
    "enterprise_value",
    "equity_value",
    "fair_value_change_entry",
    "greenhouse_gas_inventory",
    "historical_volatility",
    "impairment_entry",
    "initial_recognition_entry",
    "internal_rate_of_return",
    "log_returns",
    "JournalEntry",
    "JournalLine",
    "net_present_value",
    "payback_period",
    "scope_2_emissions",
    "simple_returns",
    "SPPIAssessment",
    "terminal_value",
    "weighted_average_cost_of_capital",
]

