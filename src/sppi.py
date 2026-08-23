"""IFRS 9 SPPI screening support for financial asset terms.

This module provides a structured preliminary screen. It does not replace a
contract review, quantitative benchmark test, or professional accounting
judgement under the applicable version of IFRS 9.
"""

from dataclasses import dataclass
from typing import Literal

SPPIStatus = Literal["pass", "fail", "review"]


@dataclass(frozen=True)
class SPPIAssessment:
    """Outcome and audit-friendly reasons from an SPPI screen."""

    status: SPPIStatus
    reasons: tuple[str, ...]

    @property
    def passes(self) -> bool:
        """Return True only when the screen concludes that the terms pass."""
        return self.status == "pass"


def assess_sppi(
    *,
    principal_protected: bool = True,
    interest_reflects_basic_lending: bool = True,
    leveraged_returns: bool = False,
    equity_or_commodity_linked: bool = False,
    convertible_to_equity: bool = False,
    modified_time_value_of_money: bool = False,
    modified_time_value_assessed: bool = False,
    modified_time_value_significant: bool = False,
    prepayment_feature: bool = False,
    reasonable_prepayment_compensation: bool = True,
    non_recourse: bool = False,
    contingent_feature: bool = False,
    contingent_related_to_basic_lending: bool = True,
    contingent_cash_flows_significantly_different: bool = False,
    contingent_represents_investment_exposure: bool = False,
) -> SPPIAssessment:
    """Screen contractual features for consistency with the IFRS 9 SPPI test.

    A ``review`` result means that the supplied flags do not support an
    automatic conclusion and a detailed contractual or quantitative assessment
    is required.
    """
    failures: list[str] = []
    reviews: list[str] = []

    if not principal_protected:
        failures.append("principal is not protected from non-lending risks")
    if not interest_reflects_basic_lending:
        failures.append("interest includes a return outside a basic lending arrangement")
    if leveraged_returns:
        failures.append("contractual returns are leveraged")
    if equity_or_commodity_linked:
        failures.append("cash flows are linked to equity or commodity risk")
    if convertible_to_equity:
        failures.append("the holder has exposure through an equity conversion feature")

    if modified_time_value_of_money:
        if not modified_time_value_assessed:
            reviews.append("modified time value of money requires a benchmark assessment")
        elif modified_time_value_significant:
            failures.append("modified time value of money creates significantly different cash flows")

    if prepayment_feature and not reasonable_prepayment_compensation:
        reviews.append("prepayment terms require assessment of compensation and other cash flows")

    if non_recourse:
        reviews.append("non-recourse terms require look-through analysis of underlying assets and risks")

    if contingent_feature:
        if contingent_represents_investment_exposure:
            failures.append("contingent cash flows represent investment exposure")
        elif contingent_cash_flows_significantly_different:
            failures.append("contingent cash flows are significantly different from a basic loan")
        elif not contingent_related_to_basic_lending:
            reviews.append(
                "contingent feature is not directly related to basic lending risks or costs"
            )

    if failures:
        return SPPIAssessment("fail", tuple(failures + reviews))
    if reviews:
        return SPPIAssessment("review", tuple(reviews))
    return SPPIAssessment(
        "pass",
        ("contractual features supplied are consistent with a basic lending arrangement",),
    )

