"""CAS 6 client and CAS 14 contractor templates for commissioned software.

Stateless helpers: each cost is a current-period increment, never a cumulative
contract value. Recognition facts must be established outside this module.
"""

from dataclasses import dataclass
from math import isfinite
from typing import Literal

from .cas_financial_instruments import JournalEntry, JournalLine


@dataclass(frozen=True)
class SoftwareRecognition:
    """Evidence for one cost tranche; unknown evidence is False by default.

    purchased_asset means acquisition of a controlled software asset, rather
    than an outsourced internal R&D project. SaaS access is not ownership.
    The five development criteria are separate from general asset recognition.
    """

    nature: Literal["purchased_asset", "internal_rd", "service"]
    stage: Literal["research", "development", "indistinguishable"] = "indistinguishable"
    controlled: bool = False
    probable_benefits: bool = False
    reliable_measurement: bool = False
    technically_feasible: bool = False
    intention_to_complete: bool = False
    ability_to_use_or_sell: bool = False
    adequate_resources: bool = False
    development_costs_measurable: bool = False

    def __post_init__(self) -> None:
        if self.nature not in ("purchased_asset", "internal_rd", "service"):
            raise ValueError("unsupported nature")
        if self.stage not in ("research", "development", "indistinguishable"):
            raise ValueError("unsupported stage")
        for name, value in vars(self).items():
            if name not in ("nature", "stage") and type(value) is not bool:
                raise ValueError(f"{name} must be a bool")


def software_cost_treatment(facts: SoftwareRecognition) -> Literal["expense", "capitalize"]:
    """Classify only costs incurred from the date criteria are first met.

    Previously expensed costs must not be reinstated. Purchased assets use
    general recognition criteria; internal R&D also needs all five criteria.
    """
    if not isinstance(facts, SoftwareRecognition):
        raise ValueError("facts must be SoftwareRecognition")
    general = facts.controlled and facts.probable_benefits and facts.reliable_measurement
    if facts.nature == "service" or not general:
        return "expense"
    if facts.nature == "purchased_asset":
        return "capitalize"
    development = (
        facts.technically_feasible and facts.intention_to_complete
        and facts.ability_to_use_or_sell and facts.adequate_resources
        and facts.development_costs_measurable
    )
    return "capitalize" if facts.stage == "development" and development else "expense"


def _amount(value: float, name: str, *, positive: bool = False) -> float:
    if isinstance(value, (bool, str, bytes)):
        raise ValueError(f"{name} must be numeric")
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{name} must be numeric") from exc
    if not isfinite(number) or number < 0 or (positive and number == 0):
        raise ValueError(f"{name} must be finite and {'positive' if positive else 'non-negative'}")
    return number


def _bool(value: bool, name: str) -> None:
    if type(value) is not bool:
        raise ValueError(f"{name} must be a bool")


def client_software_cost_entry(
    facts: SoftwareRecognition, net_cost: float, *, vat_amount: float = 0,
    deductible_vat: bool = False,
) -> JournalEntry:
    """Recognize accepted services/costs on credit, before any advance offset.

    net_cost excludes VAT. VAT is separated only when deduction eligibility
    and supporting documents have already been established by the caller.
    Purchased assets not yet ready accumulate in a pending-use subaccount.
    """
    treatment = software_cost_treatment(facts)
    cost = _amount(net_cost, "net_cost", positive=True)
    vat = _amount(vat_amount, "vat_amount")
    _bool(deductible_vat, "deductible_vat")
    gross = _amount(cost + vat, "gross_cost", positive=True)
    account = "管理费用—软件服务费"
    if facts.nature == "internal_rd":
        account = "研发支出—资本化支出" if treatment == "capitalize" else "管理费用—研发费用"
    elif treatment == "capitalize":
        account = "无形资产—软件（待达到预定用途）"
    lines = [JournalLine(account, debit=cost if deductible_vat else gross)]
    if deductible_vat and vat:
        lines.append(JournalLine("应交税费—应交增值税（进项税额）", debit=vat))
    lines.append(JournalLine("应付账款", credit=gross))
    return JournalEntry("委托方确认本期软件支出", tuple(lines))


def client_software_ready_entry(
    facts: SoftwareRecognition, capitalized_balance: float, *, ready_for_use: bool,
) -> JournalEntry:
    """Transfer an independently reconciled capitalized balance when ready."""
    _bool(ready_for_use, "ready_for_use")
    if software_cost_treatment(facts) != "capitalize" or not ready_for_use:
        raise ValueError("capitalization criteria and ready_for_use must be satisfied")
    balance = _amount(capitalized_balance, "capitalized_balance", positive=True)
    source = ("研发支出—资本化支出" if facts.nature == "internal_rd"
              else "无形资产—软件（待达到预定用途）")
    return JournalEntry("软件达到预定用途", (
        JournalLine("无形资产—软件", debit=balance), JournalLine(source, credit=balance),
    ))


def software_cash_entry(
    party: Literal["client", "contractor"], amount: float, *, advance: bool = False,
) -> JournalEntry:
    """Pay/collect an untaxed advance or settle an existing payable/receivable.

    Advance assumes no VAT tax point has arisen. VAT on advances and advance
    application require separate entries; this helper does not track balances.
    """
    if party not in ("client", "contractor"):
        raise ValueError("unsupported party")
    _bool(advance, "advance")
    value = _amount(amount, "amount", positive=True)
    if party == "client":
        lines = (JournalLine("预付账款" if advance else "应付账款", debit=value),
                 JournalLine("银行存款", credit=value))
    else:
        lines = (JournalLine("银行存款", debit=value),
                 JournalLine("合同负债" if advance else "应收账款", credit=value))
    return JournalEntry("软件合同收付款", lines)


def contractor_software_revenue_entry(
    net_revenue: float, *, recognition_confirmed: bool,
    unconditional_receivable: bool = True, vat_amount: float = 0,
) -> JournalEntry:
    """Recognize an incremental CAS 14 revenue amount, independent of client costs.

    Caller confirms control transfer or eligible over-time performance and
    measured progress. VAT supplied here must be currently payable; use zero
    and a separate tax entry when tax timing differs. No advances are applied.
    """
    _bool(recognition_confirmed, "recognition_confirmed")
    _bool(unconditional_receivable, "unconditional_receivable")
    if not recognition_confirmed:
        raise ValueError("CAS 14 revenue recognition must be confirmed")
    revenue = _amount(net_revenue, "net_revenue", positive=True)
    vat = _amount(vat_amount, "vat_amount")
    total = _amount(revenue + vat, "total_receivable", positive=True)
    lines = [JournalLine("应收账款" if unconditional_receivable else "合同资产", debit=total),
             JournalLine("主营业务收入—软件开发", credit=revenue)]
    if vat:
        lines.append(JournalLine("应交税费—应交增值税（销项税额）", credit=vat))
    return JournalEntry("受托方确认本期软件开发收入", tuple(lines))


def contractor_software_cost_entry(
    cost: float, *, future_performance_asset: bool = False,
) -> JournalEntry:
    """Accrue net contractor costs payable to suppliers.

    True requires all CAS 14 article 26 conditions and no other applicable
    cost standard. Past/current performance costs go directly to cost of sales.
    Payroll and VAT require separate entries. This is not the client's asset.
    """
    value = _amount(cost, "cost", positive=True)
    _bool(future_performance_asset, "future_performance_asset")
    return JournalEntry("受托方归集软件开发成本", (
        JournalLine("合同履约成本" if future_performance_asset else "主营业务成本", debit=value),
        JournalLine("应付账款", credit=value),
    ))


def contractor_software_cost_release_entry(balance: float) -> JournalEntry:
    """Release eligible contract costs consistently with related revenue."""
    value = _amount(balance, "balance", positive=True)
    return JournalEntry("结转软件合同履约成本", (
        JournalLine("主营业务成本", debit=value), JournalLine("合同履约成本", credit=value),
    ))
