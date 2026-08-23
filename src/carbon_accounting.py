"""Carbon accounting calculations with user-supplied emission factors.

All functions are unit-agnostic. Activity data and emission factors must use
compatible units; for example, kWh and kg CO2e/kWh produce kg CO2e.
"""

from collections.abc import Iterable, Mapping
from math import isfinite


def _non_negative(value: float, name: str) -> float:
    number = float(value)
    if not isfinite(number) or number < 0:
        raise ValueError(f"{name} must be finite and greater than or equal to zero")
    return number


def emissions_from_activity(activity_data: float, emission_factor: float) -> float:
    """Calculate CO2e as activity data multiplied by an emission factor."""
    activity = _non_negative(activity_data, "activity_data")
    factor = _non_negative(emission_factor, "emission_factor")
    return activity * factor


def emissions_from_sources(sources: Iterable[tuple[float, float]]) -> float:
    """Sum emissions for multiple activity-data and emission-factor pairs."""
    total = 0.0
    for index, (activity, factor) in enumerate(sources):
        total += emissions_from_activity(
            _non_negative(activity, f"sources[{index}].activity_data"),
            _non_negative(factor, f"sources[{index}].emission_factor"),
        )
    return total


def scope_2_emissions(
    electricity_consumption: float,
    *,
    location_based_factor: float,
    market_based_factor: float | None = None,
) -> dict[str, float]:
    """Return location-based and, when supplied, market-based Scope 2 totals."""
    consumption = _non_negative(electricity_consumption, "electricity_consumption")
    results = {
        "location_based": emissions_from_activity(consumption, location_based_factor)
    }
    if market_based_factor is not None:
        results["market_based"] = emissions_from_activity(consumption, market_based_factor)
    return results


def greenhouse_gas_inventory(scopes: Mapping[str, float]) -> dict[str, float]:
    """Validate scope totals and return a normalized inventory with a total."""
    normalized = {
        scope: _non_negative(value, f"scopes[{scope!r}]")
        for scope, value in scopes.items()
    }
    if not normalized:
        raise ValueError("scopes must contain at least one value")
    return {**normalized, "total": sum(normalized.values())}


def emissions_intensity(total_emissions: float, denominator: float) -> float:
    """Calculate emissions per unit of revenue, output, area, or another metric."""
    emissions = _non_negative(total_emissions, "total_emissions")
    basis = _non_negative(denominator, "denominator")
    if basis == 0:
        raise ValueError("denominator must be greater than zero")
    return emissions / basis


def emissions_reduction(baseline_emissions: float, current_emissions: float) -> dict[str, float]:
    """Return absolute and percentage emissions reduction from a baseline."""
    baseline = _non_negative(baseline_emissions, "baseline_emissions")
    current = _non_negative(current_emissions, "current_emissions")
    if baseline == 0:
        raise ValueError("baseline_emissions must be greater than zero")
    absolute = baseline - current
    return {"absolute": absolute, "percentage": absolute / baseline}

