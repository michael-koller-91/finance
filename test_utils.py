import utils as ut
import sys

TOL = 1e-6  # tolerance

INFLATIONS = [i / 100 for i in range(1, 5)]
MONTHLY_CONTRIBUTIONS = [i * 100 for i in range(1, 31)]
RATES = [i / 100 for i in range(10)]
START_BALANCES = [i * 100_000 for i in range(5)]
YEARS = list(range(1, 31))


def test_annual_to_monthly():
    """
    Compare growing a value for twelve months to growing it for one year.
    """
    for rate in RATES:
        for x in START_BALANCES:
            m_rate = ut.annual_to_monthly(rate)
            x1 = x  # grow per month
            for _ in range(12):
                x1 *= m_rate
            x2 = x * (1 + rate)  # grow for one year

            assert abs(x1 - x2) < TOL


def test_compound_interest():
    """
    Compare the compound interest formula to a manual computation.
    """
    for y in YEARS:
        for rate in RATES:
            for sb in START_BALANCES:
                for mc in MONTHLY_CONTRIBUTIONS:  # regular contributions
                    for cpy in [2, 4, 12]:  # contributions per year
                        ci = ut.compound_interest(sb, rate, mc, cpy, y)

                        # compute the compount interest "manually"
                        regular_rate = (1 + rate) ** (1 / cpy)
                        m = sb
                        for _ in range(y * cpy):
                            m *= regular_rate
                            m += mc

                        assert abs(ci - m) < TOL


def test_compound_interest_rate():
    """
    Compute a compound interest final balance and use compound_interest_rate to get the
    rate that was used. Compare the true rate to the computed rate.
    """
    for y in [1, 10, 20, 30]:  # years
        for rate in [0, 0.04, 0.05]:
            for sb in [0, 100_000]:  # start balance
                for mc in [100, 500]:  # regular contributions
                    for cpy in [2, 4, 12]:  # contributions per year
                        ci = ut.compound_interest(sb, rate, mc, cpy, y)
                        cir = ut.compound_interest_rate(sb, ci, mc, cpy, y)

                        assert abs(rate - cir[0]) < TOL


def test_monthly_purchasing_power():
    """
    We do the actual balance computation of iteratively (i) consuming at the beginning
    of the month followed by (ii) growing the remaining balance. For the computation, we
    take into account that we increase the monthly consumption according to the
    inflation rate. The resulting end balance must be zero.
    """
    for sb in START_BALANCES:
        for y in YEARS:  # years to consume
            for rate in RATES:
                for inflation in INFLATIONS:

                    mpp = ut.monthly_purchasing_power(sb, y, rate, inflation)
                    mi = ut.annual_to_monthly(inflation)
                    mr = ut.annual_to_monthly(rate)

                    # consume the whole start balance
                    balance = sb  # track what remains of the start balance
                    balance -= mpp  # consume first month
                    balance *= mr  # grow what remains after first month
                    for _ in range(12 * y - 1):
                        # new month: maintain purchasing power = combat inflation
                        mpp *= mi
                        # consume this month
                        balance -= mpp
                        # grow what remains
                        balance *= mr

                    assert abs(balance) < TOL


def test_value_today():
    """
    Add inflation to today's value to see if that yields the original future value.
    """
    for sb in START_BALANCES:  # future value
        for inflation in INFLATIONS:
            for y in YEARS:
                vt = ut.value_today(sb, y, inflation)  # today's value
                x = vt * (1 + inflation) ** y  # add inflation

                assert abs(sb - x) < TOL
