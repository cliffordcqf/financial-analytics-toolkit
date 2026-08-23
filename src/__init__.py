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
from .dcf import enterprise_value, equity_value, terminal_value
from .investment_metrics import internal_rate_of_return, net_present_value, payback_period

__all__ = [
    "after_tax_cost_of_debt",
    "cost_of_equity_capm",
    "emissions_from_activity",
    "emissions_from_sources",
    "emissions_intensity",
    "emissions_reduction",
    "enterprise_value",
    "equity_value",
    "internal_rate_of_return",
    "greenhouse_gas_inventory",
    "net_present_value",
    "payback_period",
    "scope_2_emissions",
    "terminal_value",
    "weighted_average_cost_of_capital",
]

