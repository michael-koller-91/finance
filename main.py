import numpy as np
import pandas as pd
from tabulate import tabulate
from matplotlib import pyplot as plt


def ci(
    initial_investment,
    annual_interest_rate,
    regular_contribution,
    contributions_per_year,
    years,
):
    """
    Calculate compound interest.

    Note:
        It is assumed that `regular_contribution` is added at the end of each
        contribution period. For example, choosing `contributions_per_year = 12`
        means that at the end of each month `regular_contribution` is added to
        the total balance.

    Reference:
        https://www.calculator.net/investment-calculator.html
    """
    balance = initial_investment
    balance_after_each_contribution = [balance]
    # convert annual interest rate to interest rate per contribution time interval (+ 1)
    r = (1 + annual_interest_rate) ** (1 / contributions_per_year)
    for _ in range(years):
        for _ in range(contributions_per_year):
            # grow until next contribution
            balance *= r
            # next contribution
            balance += regular_contribution

            balance_after_each_contribution.append(balance)
    return balance, balance_after_each_contribution


def rep(loan_balance, annual_interest_rate, regular_installment, installments_per_year):
    """
    Calculate repayment.

    Reference:
        https://www.calculator.net/repayment-calculator.html
    """
    if (
        regular_installment * installments_per_year
        < loan_balance * annual_interest_rate
    ):
        raise ValueError(
            f"You need to repay at least {loan_balance * annual_interest_rate} in the first year."
        )
    installments = 0
    owed = loan_balance
    owed_after_each_installment = [owed]
    # convert annual interest rate to interest rate per contribution time interval
    r = (1 + annual_interest_rate) ** (1 / installments_per_year) - 1
    while True:
        for _ in range(installments_per_year):
            installments += 1
            interest = r * owed
            owed -= regular_installment - interest

            owed_after_each_installment.append(owed)
            if owed < 0:
                months = installments / installments_per_year * 12
                return months, owed_after_each_installment


def test():
    """
    Compare to reference.
    """
    balance = ci(
        initial_investment=5_000,
        annual_interest_rate=0.03,
        regular_contribution=100,
        contributions_per_year=12,
        years=5,
    )
    assert abs(balance[0] - 12_254.47) < 0.01, "Compound interest is not correct."

    months = rep(
        loan_balance=10_000,
        annual_interest_rate=0.1,
        regular_installment=200,
        installments_per_year=12,
    )
    assert abs(months[0] - (5 * 12 + 5)) < 0.1, "Repayment is not correct."


def etf():
    interest_rates = [0.06, 0.07, 0.08]
    initial_investment = 100_000
    regular_contributions = [1_500, 2_000, 2_500]
    contributions_per_year = 12
    years = 25

    x_axis = [x for x in range(years + 1)]
    # dictionary to print a table in the end
    t_dict = {"year": list(), "rate": list(), "contribution": list(), "balance": list()}
    for rate in interest_rates:
        for contribution in regular_contributions:
            y_axis = ci(
                initial_investment=initial_investment,
                annual_interest_rate=rate,
                regular_contribution=contribution,
                contributions_per_year=contributions_per_year,
                years=years,
            )[1]

            # only the initial investment and the 12th month of every year
            y_axis = [y_axis[0], *y_axis[12::12]]
            # convert to k€
            y_axis = [y / 1e3 for y in y_axis]

            # for table
            t_dict["year"].extend(x_axis)
            t_dict["rate"].extend([rate] * (years + 1))
            t_dict["contribution"].extend([contribution] * (years + 1))
            t_dict["balance"].extend(y_axis)

            # for plot
            plt.plot(x_axis, y_axis, label=f"rate = {rate}, contr. = {contribution}")

    # for table
    with open("etf.txt", "w", encoding="utf8") as f:
        df = pd.DataFrame(t_dict)
        table = tabulate(df, headers="keys", tablefmt="psql", showindex=False)
        f.write(table)

    # for plot
    plt.legend()
    plt.xlabel("years")
    plt.ylabel("k€")
    plt.title("ETF")
    plt.savefig("etf.png")
    plt.close()


def house():
    interest_rates = [0.02, 0.03, 0.04]
    loan_balance = 500_000
    regular_installments = [2_000, 2_500, 3_000]
    installments_per_year = 12

    # dictionary to print a table in the end
    t_dict = {"year": list(), "rate": list(), "installment": list(), "owed": list()}
    for rate in interest_rates:
        for installment in regular_installments:
            y_axis = rep(
                loan_balance=loan_balance,
                annual_interest_rate=rate,
                regular_installment=installment,
                installments_per_year=installments_per_year,
            )[1]
            # only the 12th month of every year and the last month
            y_axis = [*y_axis[::12], y_axis[-1]]

            years = len(y_axis)
            x_axis = [x for x in range(1, years + 1)]
            # convert to k€
            y_axis = [y / 1e3 for y in y_axis]

            # for table
            t_dict["year"].extend(x_axis)
            t_dict["rate"].extend([rate] * years)
            t_dict["installment"].extend([installment] * years)
            t_dict["owed"].extend(y_axis)

            # for plot
            plt.plot(x_axis, y_axis, label=f"rate = {rate}, inst. = {installment}")

    # for table
    with open("house.txt", "w", encoding="utf8") as f:
        df = pd.DataFrame(t_dict)
        table = tabulate(df, headers="keys", tablefmt="psql", showindex=False)
        f.write(table)

    # for plot
    plt.legend()
    plt.xlabel("years")
    plt.ylabel("k€")
    plt.title("House")
    plt.savefig("house.png")
    plt.close()


def main():
    etf()
    house()


if __name__ == "__main__":
    test()
    main()
