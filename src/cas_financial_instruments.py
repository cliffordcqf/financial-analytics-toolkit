"""CAS 22 financial asset classification and journal-entry templates.

The helpers support preliminary processing under Chinese Accounting Standards
for Business Enterprises. Account mappings and conclusions must be confirmed
against the entity's contracts, accounting policies, chart of accounts, and
the CAS requirements effective for the reporting period.
"""

from dataclasses import dataclass
from math import isclose, isfinite
from typing import Literal

from .sppi import SPPIAssessment

BusinessModel = Literal["hold_to_collect", "collect_and_sell", "other"]
AssetClassification = Literal["amortized_cost", "fvoci_debt", "fvtpl"]


@dataclass(frozen=True)
class JournalLine:
    """One debit or credit line in a journal entry."""

    account: str
    debit: float = 0.0
    credit: float = 0.0

    def __post_init__(self) -> None:
        if not self.account.strip():
            raise ValueError("account must not be empty")
        for amount, name in ((self.debit, "debit"), (self.credit, "credit")):
            if not isfinite(amount) or amount < 0:
                raise ValueError(f"{name} must be finite and non-negative")
        if self.debit > 0 and self.credit > 0:
            raise ValueError("a journal line cannot contain both debit and credit")


@dataclass(frozen=True)
class JournalEntry:
    """A balanced accounting entry with an explanatory memo."""

    memo: str
    lines: tuple[JournalLine, ...]

    def __post_init__(self) -> None:
        if not self.lines:
            raise ValueError("journal entry must contain at least one line")
        debit = sum(line.debit for line in self.lines)
        credit = sum(line.credit for line in self.lines)
        if not isclose(debit, credit, abs_tol=1e-8):
            raise ValueError("journal entry is not balanced")

    @property
    def total(self) -> float:
        """Return the total debit, equal to the total credit."""
        return sum(line.debit for line in self.lines)


def classify_financial_asset(
    sppi_assessment: SPPIAssessment,
    business_model: BusinessModel,
) -> AssetClassification:
    """Classify a debt financial asset from SPPI and business-model results."""
    if business_model not in {"hold_to_collect", "collect_and_sell", "other"}:
        raise ValueError("unsupported business_model")
    if sppi_assessment.status == "review":
        raise ValueError("SPPI assessment requires review before classification")
    if sppi_assessment.status == "fail" or business_model == "other":
        return "fvtpl"
    if business_model == "hold_to_collect":
        return "amortized_cost"
    return "fvoci_debt"


def initial_recognition_entry(
    classification: AssetClassification,
    fair_value: float,
    transaction_costs: float = 0.0,
) -> JournalEntry:
    """Create an initial-recognition entry for a debt financial asset."""
    value = _non_negative(fair_value, "fair_value")
    costs = _non_negative(transaction_costs, "transaction_costs")
    account = _asset_account(classification)
    if classification == "fvtpl":
        lines = [JournalLine(account, debit=value)]
        if costs:
            lines.append(JournalLine("投资收益", debit=costs))
    else:
        lines = [JournalLine(account, debit=value + costs)]
    lines.append(JournalLine("银行存款", credit=value + costs))
    return JournalEntry("金融资产初始确认", tuple(lines))


def effective_interest_entry(
    classification: Literal["amortized_cost", "fvoci_debt"],
    opening_carrying_amount: float,
    effective_interest_rate: float,
    cash_interest_received: float,
) -> JournalEntry:
    """Accrue interest income using the effective interest method."""
    carrying = _non_negative(opening_carrying_amount, "opening_carrying_amount")
    rate = float(effective_interest_rate)
    cash = _non_negative(cash_interest_received, "cash_interest_received")
    if not isfinite(rate) or rate < 0:
        raise ValueError("effective_interest_rate must be finite and non-negative")
    income = carrying * rate
    adjustment = income - cash
    account = _asset_account(classification) + "—利息调整"
    lines = [JournalLine("银行存款", debit=cash)] if cash else []
    if adjustment > 0:
        lines.append(JournalLine(account, debit=adjustment))
    elif adjustment < 0:
        lines.append(JournalLine(account, credit=-adjustment))
    lines.append(JournalLine("投资收益", credit=income))
    return JournalEntry("按实际利率法确认利息收入", tuple(lines))


def fair_value_change_entry(
    classification: Literal["fvoci_debt", "fvtpl"],
    fair_value_change: float,
) -> JournalEntry:
    """Record a positive or negative fair value change."""
    change = float(fair_value_change)
    if not isfinite(change) or change == 0:
        raise ValueError("fair_value_change must be finite and non-zero")
    asset = _asset_account(classification) + "—公允价值变动"
    offset = "其他综合收益" if classification == "fvoci_debt" else "公允价值变动损益"
    if change > 0:
        lines = (JournalLine(asset, debit=change), JournalLine(offset, credit=change))
    else:
        lines = (JournalLine(offset, debit=-change), JournalLine(asset, credit=-change))
    return JournalEntry("确认金融资产公允价值变动", lines)


def impairment_entry(
    classification: Literal["amortized_cost", "fvoci_debt"],
    expected_credit_loss: float,
) -> JournalEntry:
    """Recognize an expected credit loss for an eligible debt financial asset."""
    loss = _non_negative(expected_credit_loss, "expected_credit_loss")
    if loss == 0:
        raise ValueError("expected_credit_loss must be greater than zero")
    credit_account = (
        "债权投资减值准备"
        if classification == "amortized_cost"
        else "其他综合收益—信用减值准备"
    )
    return JournalEntry(
        "确认预期信用损失",
        (JournalLine("信用减值损失", debit=loss), JournalLine(credit_account, credit=loss)),
    )


def _asset_account(classification: AssetClassification) -> str:
    accounts = {
        "amortized_cost": "债权投资",
        "fvoci_debt": "其他债权投资",
        "fvtpl": "交易性金融资产",
    }
    try:
        return accounts[classification]
    except KeyError as error:
        raise ValueError("unsupported classification") from error


def _non_negative(value: float, name: str) -> float:
    number = float(value)
    if not isfinite(number) or number < 0:
        raise ValueError(f"{name} must be finite and non-negative")
    return number

