import utils

TOL = 1e-6  # tolerance


def test_annual_to_monthly():
    """
    Compare growing a value for twelve months to growing it for one year.
    """
    for r in range(1, 10):
        rate = r / 100
        for i in range(4):
            x = 123 * i
            m_rate = utils.annual_to_monthly(rate)
            x1 = x  # grow per month
            for _ in range(12):
                x1 *= m_rate
            x2 = x * (1 + rate)  # grow for one year

            assert abs(x1 - x2) < TOL


def test_end_balance():
    """
    Just a sanity check:
    a) The end balance should be larger than the start balance.
    b) End balance divided by invested months should be larger than the monthly
       investment.
    c) End balance should be larger than the total investment.
    """
    for s in range(4):
        sb = s * 1e6  # start balance
        for m in range(1, 10):
            mc = m * 100  # monthly contribution
            for y in range(1, 30):  # years to grow
                for r in range(1, 10):
                    rate = r / 100  # annual rate of return
                    eb = utils.end_balance(sb, mc, y, rate)
                    ti = sb + mc * 12 * y  # total investment

                    assert eb > sb  # a)
                    assert eb / 12 / y > mc  # b)
                    assert eb > ti  # c)


def test_monthly_purchasing_power():
    """
    We do the actual balance computation of iteratively (i) consuming at the beginning
    of the month followed by (ii) growing the remaining balance. For the computation, we
    take into account that we increase the monthly consumption according to the
    inflation rate. The resulting end balance must be zero.
    """
    for s in range(1, 5):
        sb = s * 1e6  # start balance
        for y in range(1, 30):  # years to consume
            for r in range(0, 10):
                rate = r / 100  # annual rate of return
                for i in range(1, 5):
                    inflation = i / 100  # annual rate of inflation

                    mpp = utils.monthly_purchasing_power(sb, y, rate, inflation)
                    mi = utils.annual_to_monthly(inflation)
                    mr = utils.annual_to_monthly(rate)

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
    for i in range(4):
        x1 = 123 * i  # future value
        for i in range(1, 5):
            inflation = i / 100  # annual rate of inflation
            for years in range(1, 30):
                y = utils.value_today(x1, years, inflation)  # today's value
                x2 = y * (1 + inflation) ** years  # add inflation

                assert abs(x1 - x2) < TOL
