"""CAS 22 expected credit loss calculations and accounting support.

The module provides transparent building blocks rather than a complete credit
risk model. Entities remain responsible for scenario design, forward-looking
information, significant-increase criteria, default definitions, and overlays.
"""

from dataclasses import dataclass
from math import isclose, isfinite
from typing import Literal

from .cas_financial_instruments import JournalEntry, JournalLine

ECLStage = Literal["stage_1", "stage_2", "stage_3"]


@dataclass(frozen=True)
class ECLScenario:
    """One probability-weighted PD × LGD × EAD scenario."""

    name: str
    scenario_weight: float
    probability_of_default: float
    loss_given_default: float
    exposure_at_default: float
    discount_factor: float = 1.0

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("scenario name must not be empty")
        _unit_interval(self.scenario_weight, "scenario_weight")
        _unit_interval(self.probability_of_default, "probability_of_default")
        _unit_interval(self.loss_given_default, "loss_given_default")
        _non_negative(self.exposure_at_default, "exposure_at_default")
        factor = float(self.discount_factor)
        if not isfinite(factor) or not 0 < factor <= 1:
            raise ValueError("discount_factor must be greater than 0 and at most 1")

    @property
    def expected_loss(self) -> float:
        """Return discounted expected loss before scenario weighting."""
        return (
            self.probability_of_default
            * self.loss_given_default
            * self.exposure_at_default
            * self.discount_factor
        )


def determine_ecl_stage(
    *,
    significant_increase_in_credit_risk: bool,
    credit_impaired: bool,
) -> ECLStage:
    """Return the three-stage ECL classification from assessed credit status."""
    if credit_impaired:
        return "stage_3"
    if significant_increase_in_credit_risk:
        return "stage_2"
    return "stage_1"


def loss_horizon(stage: ECLStage) -> Literal["12_month", "lifetime"]:
    """Return the required ECL horizon for a stage."""
    if stage == "stage_1":
        return "12_month"
    if stage in {"stage_2", "stage_3"}:
        return "lifetime"
    raise ValueError("unsupported ECL stage")


def probability_weighted_ecl(scenarios: list[ECLScenario]) -> float:
    """Calculate probability-weighted discounted ECL across scenarios."""
    if not scenarios:
        raise ValueError("scenarios must contain at least one scenario")
    total_weight = sum(scenario.scenario_weight for scenario in scenarios)
    if not isclose(total_weight, 1.0, abs_tol=1e-8):
        raise ValueError("scenario weights must sum to 1")
    return sum(
        scenario.scenario_weight * scenario.expected_loss for scenario in scenarios
    )


def interest_revenue_basis(
    stage: ECLStage,
    gross_carrying_amount: float,
    loss_allowance: float,
) -> float:
    """Return the carrying amount used to calculate effective interest revenue."""
    gross = _non_negative(gross_carrying_amount, "gross_carrying_amount")
    allowance = _non_negative(loss_allowance, "loss_allowance")
    if allowance > gross:
        raise ValueError("loss_allowance must not exceed gross_carrying_amount")
    if stage in {"stage_1", "stage_2"}:
        return gross
    if stage == "stage_3":
        return gross - allowance
    raise ValueError("unsupported ECL stage")


def ecl_adjustment_entry(
    classification: Literal["amortized_cost", "fvoci_debt"],
    current_allowance: float,
    required_allowance: float,
) -> JournalEntry:
    """Record an increase or reversal in a CAS 22 loss allowance."""
    current = _non_negative(current_allowance, "current_allowance")
    required = _non_negative(required_allowance, "required_allowance")
    change = required - current
    if isclose(change, 0.0, abs_tol=1e-8):
        raise ValueError("required allowance is unchanged")
    allowance_account = (
        "债权投资减值准备"
        if classification == "amortized_cost"
        else "其他综合收益—信用减值准备"
    )
    if change > 0:
        lines = (
            JournalLine("信用减值损失", debit=change),
            JournalLine(allowance_account, credit=change),
        )
        memo = "补提预期信用损失准备"
    else:
        lines = (
            JournalLine(allowance_account, debit=-change),
            JournalLine("信用减值损失", credit=-change),
        )
        memo = "转回预期信用损失准备"
    return JournalEntry(memo, lines)


def _unit_interval(value: float, name: str) -> float:
    number = float(value)
    if not isfinite(number) or not 0 <= number <= 1:
        raise ValueError(f"{name} must be between 0 and 1")
    return number


def _non_negative(value: float, name: str) -> float:
    number = float(value)
    if not isfinite(number) or number < 0:
        raise ValueError(f"{name} must be finite and non-negative")
    return number

