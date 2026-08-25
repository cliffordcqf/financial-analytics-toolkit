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
from .expected_credit_loss import (
    ECLScenario,
    determine_ecl_stage,
    ecl_adjustment_entry,
    interest_revenue_basis,
    loss_horizon,
    probability_weighted_ecl,
)
from .fixed_income import (
    bond_price,
    convexity,
    macaulay_duration,
    modified_duration,
    yield_to_maturity,
)
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
    "bond_price",
    "classify_financial_asset",
    "cost_of_equity_capm",
    "convexity",
    "downside_deviation",
    "determine_ecl_stage",
    "ECLScenario",
    "ecl_adjustment_entry",
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
    "interest_revenue_basis",
    "internal_rate_of_return",
    "log_returns",
    "JournalEntry",
    "JournalLine",
    "loss_horizon",
    "macaulay_duration",
    "modified_duration",
    "net_present_value",
    "payback_period",
    "probability_weighted_ecl",
    "scope_2_emissions",
    "simple_returns",
    "SPPIAssessment",
    "terminal_value",
    "weighted_average_cost_of_capital",
    "yield_to_maturity",
]

