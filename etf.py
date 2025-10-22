from datetime import datetime
from tabulate import tabulate
from textwrap import dedent
import pandas as pd
import pytz
import utils as ut


consume_years = [20, 30, 40]
contributions = [0, 500, 1000, 1500, 2000, 2500, 3000]
contributions_per_year = 12
growth_years = [10, 20, 30]
inflation = 0.03
rates = [0.05, 0.06, 0.07]
start_balances = [
    0,
    50_000,
    100_000,
    150_000,
    200_000,
    250_000,
    300_000,
    350_000,
    400_000,
    450_000,
]

t_dict = {
    "contribution": list(),
    "start balance": list(),
    "rate": list(),
    "growth years": list(),
    "end balance": list(),
    # "net interest": list(),
    "net interest (today)": list(),
    "consume years": list(),
    "net MPP": list(),
    "net MPP (today)": list(),
}
for c in contributions:
    for sb in start_balances:
        for r in rates:
            for gy in growth_years:
                for cy in consume_years:
                    t_dict["contribution"].append(c)
                    t_dict["start balance"].append(f"{sb/1e3:.0f} k")
                    t_dict["rate"].append(r)
                    t_dict["growth years"].append(gy)
                    t_dict["consume years"].append(cy)

                    eb = ut.compound_interest(
                        initial_balance=sb,
                        annual_interest_rate=r,
                        regular_contribution=c,
                        contributions_per_year=contributions_per_year,
                        years=gy,
                    )
                    t_dict["end balance"].append(f"{eb/1e3:.0f} k")

                    monthly_rate = ut.annual_to_monthly(r) - 1
                    interest = eb * monthly_rate
                    net_interest = ut.subtract_gains_tax(interest)
                    # t_dict["net interest"].append(f"{net_interest:.0f}")

                    net_interest_today = ut.value_today(
                        x=net_interest, years=gy, annual_rate_of_inflation=inflation
                    )
                    t_dict["net interest (today)"].append(f"{net_interest_today:.0f}")

                    mpp = ut.monthly_purchasing_power(
                        start_balance=eb,
                        years_to_consume=cy,
                        annual_rate_of_return=r,
                        annual_rate_of_inflation=inflation,
                    )

                    net_mpp = ut.subtract_gains_tax(mpp)
                    t_dict["net MPP"].append(f"{net_mpp:.0f}")

                    net_mpp_today = ut.value_today(
                        x=net_mpp, years=gy, annual_rate_of_inflation=inflation
                    )
                    t_dict["net MPP (today)"].append(f"{net_mpp_today:.0f}")


out_file = "etf.txt"
with open(out_file, "w", encoding="utf8") as f:
    f.write(
        dedent(
            f"""
            Generated on {pytz.timezone('Europe/Berlin').localize(datetime.now()).ctime()} (timezone Berlin).

            The annual inflation rate is {inflation}.
            Every "(today)" value takes a future value and computes its value today
            by taking into account inflation and the number of growth years.
            For example, with 0.03 annual inflation, a value of 100 € in 30 years
            corresponds to {ut.value_today(100, 30, 0.03):.2f} € today.

            There are monthly contributions during the growth years. There is no contribution during the consume years.

            Net values are after subtracting 0.25 * 1.055 tax.

            "interest" is the interest that the end balance generates in one month.

            "MPP" is the monthly purchasing power.
            That is, "MPP" is the value that can be spent in the first month of the consume years.
            In every following month, MPP can be increased by an amount corresponding to the inflation rate.
            At the end of the last consume year, the remaining balance will be zero.

            """
        )
    )

    df = pd.DataFrame(t_dict)
    table = tabulate(
        df, headers="keys", tablefmt="grid", showindex=False, disable_numparse=True
    )
    f.write(table)

print(f"Generated {out_file}")
