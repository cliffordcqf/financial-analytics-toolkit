"""Plain-vanilla fixed-rate bond analytics."""

from math import isfinite


def _terms(
    face_value: float,
    annual_coupon_rate: float,
    years_to_maturity: float,
    payments_per_year: int,
) -> tuple[float, float, int, int]:
    face = float(face_value)
    coupon_rate = float(annual_coupon_rate)
    years = float(years_to_maturity)
    if not all(isfinite(value) for value in (face, coupon_rate, years)):
        raise ValueError("bond inputs must be finite")
    if face <= 0 or years <= 0:
        raise ValueError("face_value and years_to_maturity must be greater than zero")
    if coupon_rate < 0:
        raise ValueError("annual_coupon_rate must be non-negative")
    if not isinstance(payments_per_year, int) or payments_per_year <= 0:
        raise ValueError("payments_per_year must be a positive integer")
    periods_float = years * payments_per_year
    periods = round(periods_float)
    if abs(periods_float - periods) > 1e-9:
        raise ValueError("years_to_maturity must contain whole payment periods")
    coupon = face * coupon_rate / payments_per_year
    return face, coupon, periods, payments_per_year


def bond_price(
    face_value: float,
    annual_coupon_rate: float,
    years_to_maturity: float,
    annual_yield: float,
    payments_per_year: int = 2,
) -> float:
    """Return the clean theoretical price on a coupon payment date."""
    face, coupon, periods, frequency = _terms(
        face_value, annual_coupon_rate, years_to_maturity, payments_per_year
    )
    yield_rate = float(annual_yield)
    if not isfinite(yield_rate) or yield_rate <= -frequency:
        raise ValueError("annual_yield must be finite and greater than -payments_per_year")
    periodic_yield = yield_rate / frequency
    price = sum(coupon / (1 + periodic_yield) ** period for period in range(1, periods + 1))
    return price + face / (1 + periodic_yield) ** periods


def yield_to_maturity(
    market_price: float,
    face_value: float,
    annual_coupon_rate: float,
    years_to_maturity: float,
    payments_per_year: int = 2,
    *,
    tolerance: float = 1e-10,
    max_iterations: int = 300,
) -> float:
    """Estimate nominal annual YTM using a bisection root search."""
    target = float(market_price)
    if not isfinite(target) or target <= 0:
        raise ValueError("market_price must be finite and greater than zero")
    if tolerance <= 0 or not isfinite(tolerance) or max_iterations <= 0:
        raise ValueError("tolerance and max_iterations must be greater than zero")
    _terms(face_value, annual_coupon_rate, years_to_maturity, payments_per_year)

    low, high = -0.999 * payments_per_year, 10.0
    for _ in range(max_iterations):
        midpoint = (low + high) / 2
        calculated = bond_price(
            face_value,
            annual_coupon_rate,
            years_to_maturity,
            midpoint,
            payments_per_year,
        )
        if abs(calculated - target) <= tolerance:
            return midpoint
        if calculated > target:
            low = midpoint
        else:
            high = midpoint
    raise ValueError("yield_to_maturity did not converge")


def macaulay_duration(
    face_value: float,
    annual_coupon_rate: float,
    years_to_maturity: float,
    annual_yield: float,
    payments_per_year: int = 2,
) -> float:
    """Return Macaulay duration in years."""
    face, coupon, periods, frequency = _terms(
        face_value, annual_coupon_rate, years_to_maturity, payments_per_year
    )
    price = bond_price(
        face, annual_coupon_rate, years_to_maturity, annual_yield, frequency
    )
    periodic_yield = annual_yield / frequency
    weighted_value = 0.0
    for period in range(1, periods + 1):
        cash_flow = coupon + (face if period == periods else 0.0)
        present_value = cash_flow / (1 + periodic_yield) ** period
        weighted_value += (period / frequency) * present_value
    return weighted_value / price


def modified_duration(
    face_value: float,
    annual_coupon_rate: float,
    years_to_maturity: float,
    annual_yield: float,
    payments_per_year: int = 2,
) -> float:
    """Return modified duration for a nominal annual yield."""
    macaulay = macaulay_duration(
        face_value,
        annual_coupon_rate,
        years_to_maturity,
        annual_yield,
        payments_per_year,
    )
    return macaulay / (1 + annual_yield / payments_per_year)


def convexity(
    face_value: float,
    annual_coupon_rate: float,
    years_to_maturity: float,
    annual_yield: float,
    payments_per_year: int = 2,
) -> float:
    """Return standard discrete bond convexity in years squared."""
    face, coupon, periods, frequency = _terms(
        face_value, annual_coupon_rate, years_to_maturity, payments_per_year
    )
    price = bond_price(
        face, annual_coupon_rate, years_to_maturity, annual_yield, frequency
    )
    periodic_yield = annual_yield / frequency
    numerator = 0.0
    for period in range(1, periods + 1):
        cash_flow = coupon + (face if period == periods else 0.0)
        numerator += (
            cash_flow
            * period
            * (period + 1)
            / (1 + periodic_yield) ** (period + 2)
        )
    return numerator / (price * frequency**2)

