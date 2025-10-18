from datetime import datetime
from tabulate import tabulate
import pandas as pd
import pytz
import utils as ut


consume_years = [20, 30, 40]
contribution = 100
contributions_per_year = 12
growth_years = [10, 20, 30]
inflation = 0.03
rates = [0.05, 0.06, 0.07]
start_balances = [0, 100_000, 200_000]

t_dict = {
    "start balance": list(),
    "rate": list(),
    "growth years": list(),
    "end balance": list(),
    "consume years": list(),
    "MPP after 25% tax": list(),
    "MPP today": list(),
}
for sb in start_balances:
    for r in rates:
        for gy in growth_years:
            for cy in consume_years:
                t_dict["start balance"].append(sb)
                t_dict["rate"].append(r)
                t_dict["growth years"].append(gy)
                t_dict["consume years"].append(cy)

                eb = ut.compound_interest(
                    sb, r, contribution, contributions_per_year, gy
                )
                t_dict["end balance"].append(f"{eb:.1e}")

                mpp = ut.monthly_purchasing_power(eb, cy, r, inflation)

                mpp_net = ut.subtract_gains_tax(mpp)
                t_dict["MPP after 25% tax"].append(f"{mpp_net:.0f}")

                mpp_today = ut.value_today(mpp_net, gy, inflation)
                t_dict["MPP today"].append(f"{mpp_today:.0f}")


with open("etf.txt", "w", encoding="utf8") as f:
    f.write(
        f"Generated on {pytz.timezone('Europe/Berlin').localize(datetime.now()).ctime()} (timezone Berlin).\n\n"
    )
    f.write(f"The monthly contribution is {contribution}.\n")
    f.write(f"The annual inflation rate is {inflation}.\n")
    f.write('"MPP" is the monthly purchasing power.\n')
    f.write(
        'That is, "MPP" is the value that can be spent in the first month of the consume years.\n'
    )
    f.write(
        "In every following month, MPP can be increased by an amount corresponding to the inflation rate.\n"
    )
    f.write(
        "At the end of the last consume year, the remaining balance will be zero.\n"
    )
    f.write(
        """"MPP today" is today's "MPP" value taking into account inflation and the number of growth years.\n"""
    )
    f.write("\n")

    df = pd.DataFrame(t_dict)
    table = tabulate(
        df, headers="keys", tablefmt="psql", showindex=False, disable_numparse=True
    )
    f.write(table)
