def annual_to_monthly(rate: float) -> float:
    """
    Convert an annual rate to a monthly rate.
    """
    return (1 + rate) ** (1 / 12)


def end_balance(
    start_balance: float,
    monthly_contribution: float,
    years_to_grow: int,
    annual_rate_of_return: float,
) -> float:
    """
    The annual rate of return is converted into a monthly rate.
    The contribution is invested at the beginning of each month
    and the resulting total balance then grows at the end of every
    month.
    """
    monthly_rate = annual_to_monthly(annual_rate_of_return)
    v = start_balance
    for _ in range(years_to_grow * 12):
        v += monthly_contribution
        v *= monthly_rate
    return v


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


def value_today(x: float, years: int, annual_rate_of_inflation: float) -> float:
    """
    What does an mount of `x` in `years` years correspond to today
    with the given rate of inflation?
    """
    return x / (1 + annual_rate_of_inflation) ** years
