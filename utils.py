from numpy.polynomial.polynomial import Polynomial
from scipy.optimize import root_scalar
import numpy as np


def annual_to_monthly(rate: float) -> float:
    """
    Convert an annual rate to a monthly rate.
    """
    return (1 + rate) ** (1 / 12)


def compound_interest(
    initial_balance: float,
    annual_interest_rate: float,
    regular_contribution: float,
    contributions_per_year: int,
    years: int,
) -> float:
    """
    Grow the current balance according to the rate and then add the next contribution.

    See README.md for a derivation.
    """
    K_0 = initial_balance
    r = annual_interest_rate
    m = regular_contribution
    P = contributions_per_year
    N = years

    R = 1 + r
    if 1 - R ** (1 / P) == 0:
        return K_0 + m * P * N
    else:
        return K_0 * R**N + m * (1 - R**N) / (1 - R ** (1 / P))


def compound_interest_rate(
    initial_balance: float,
    final_balance: float,
    regular_contribution: float,
    contributions_per_year: int,
    years: int,
) -> tuple[float, float]:
    """
    The rate needed for `initial_balance` to grow to `final_balance` with the given
    contributions and within the given number of years.

    See README.md for a derivation.
    """
    K_0 = initial_balance
    K_NP = final_balance
    m = regular_contribution
    P = contributions_per_year
    N = years

    # polynomial in S
    coef = np.zeros(N * P + 2)
    coef[0] = m - K_NP
    coef[1] = K_NP
    coef[N * P] = K_0 - m
    coef[N * P + 1] = -K_0
    poly = Polynomial(coef)

    # R = S^P
    R_roots = poly.roots() ** P
    # real roots
    R_roots = R_roots[R_roots.imag < 1e-10].real
    # potential interest rates
    rates = R_roots[R_roots > 1] - 1

    # try to find a suitable root
    for r in rates:
        K_final = compound_interest(
            initial_balance=initial_balance,
            annual_interest_rate=r,
            regular_contribution=regular_contribution,
            contributions_per_year=contributions_per_year,
            years=years,
        )
        error = np.abs(final_balance - K_final)
        if error < 1e-2:
            return r, error
    else:
        # different attempt
        r = root_scalar(poly, x0=1e-4, x1=0.1).root ** P - 1

        K_final = compound_interest(
            initial_balance=initial_balance,
            annual_interest_rate=r,
            regular_contribution=regular_contribution,
            contributions_per_year=contributions_per_year,
            years=years,
        )

        error = np.abs(final_balance - K_final)
        if error >= 1e-2:
            print(
                f"{compound_interest_rate.__name__}(): Did not find a suitable interest"
                f" rate. Returning closest match with balance error {error:.3f}."
            )
        return r, error


def monthly_purchasing_power(
    start_balance: float,
    years_to_consume: int,
    annual_rate_of_return: float,
    annual_rate_of_inflation: float,
) -> float:
    """
    The initial deposit value is `start_balance`.
    It is assumed that money is taken out of the deposit at the
    beginning of each month. The amount is chosen such that (i)
    it can be increased in every month by a factor corresponding
    to the inflation rate and (ii) after `years_to_consume` many
    years the end balance is zero.
    In other words, the purchasing power is the same in every month.
    """
    monthly_inflation = annual_to_monthly(annual_rate_of_inflation)
    monthly_rate = annual_to_monthly(annual_rate_of_return)
    K = years_to_consume * 12
    rs_cum = 0
    for i in range(1, K + 1):
        rs_cum += monthly_inflation ** (K - i) * monthly_rate**i
    return start_balance * monthly_rate**K / rs_cum


def subtract_gains_tax(x):
    """
    25% Kapitalertragssteuer + Soli
    """
    return x * (1 - 0.25 * 1.055)


def value_today(x: float, years: int, annual_rate_of_inflation: float) -> float:
    """
    What does an mount of `x` in `years` years correspond to today
    with the given rate of inflation?
    """
    return x / (1 + annual_rate_of_inflation) ** years
