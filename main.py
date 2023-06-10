import numpy as np
import pandas as pd
from tabulate import tabulate
from matplotlib import pyplot as plt
from numpy.polynomial.polynomial import Polynomial


def ci(
    initial_balance,
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
    balance = initial_balance
    balance_after_each_contribution = [balance]
    # convert annual interest rate to interest rate per contribution time interval (+ 1)
    if contributions_per_year > 0:
        r = (1 + annual_interest_rate) ** (1 / contributions_per_year)
    else:
        r = annual_interest_rate
    for _ in range(years):
        for _ in range(contributions_per_year):
            # grow until next contribution
            balance *= r
            # next contribution
            balance += regular_contribution

            balance_after_each_contribution.append(balance)
    return balance, balance_after_each_contribution


def ci_formula(
    initial_balance,
    annual_interest_rate,
    regular_contribution,
    contributions_per_year,
    years,
):
    K_0 = initial_balance
    r = annual_interest_rate
    m = regular_contribution
    P = contributions_per_year
    N = years

    R = 1 + r
    return K_0 * R**N + m * (1 - R**N) / (1 - R ** (1 / P))


def ci_to_rate(
    initial_balance,
    final_balance,
    regular_contribution,
    contributions_per_year,
    years,
):
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
    for r in rates[::-1]:
        K_NP_r = ci_formula(
            initial_balance=initial_balance,
            annual_interest_rate=r,
            regular_contribution=regular_contribution,
            contributions_per_year=contributions_per_year,
            years=years,
        )
        if np.abs(final_balance - K_NP_r) < 1e-3:
            return r
    else:
        print("ci_to_rate(): Did not find a suitable interest rate.")


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
    Small unit tests.
    """
    #
    # compare compound interest to reference
    #
    b0 = ci(
        initial_balance=5_000,
        annual_interest_rate=0.03,
        regular_contribution=100,
        contributions_per_year=12,
        years=5,
    )[0]
    assert abs(b0 - 12_254.47) < 0.01, "Compound interest is not correct."

    #
    # check compound interest formula
    #
    b1 = ci_formula(
        initial_balance=5_000,
        annual_interest_rate=0.03,
        regular_contribution=100,
        contributions_per_year=12,
        years=5,
    )
    assert abs(b1 - 12_254.47) < 0.01, "Compound interest (formula) is not correct."

    #
    # compare repayment to formula
    #
    months = rep(
        loan_balance=10_000,
        annual_interest_rate=0.1,
        regular_installment=200,
        installments_per_year=12,
    )
    assert abs(months[0] - (5 * 12 + 5)) < 0.1, "Repayment is not correct."

    #
    # test conversion from compound interest to rate
    #
    initial_balance = 5_000
    annual_interest_rate = 0.03521
    regular_contribution = 100
    contributions_per_year = 12
    years = 5

    # compute a final balance
    K_NP = ci_formula(
        initial_balance=initial_balance,
        annual_interest_rate=annual_interest_rate,
        regular_contribution=regular_contribution,
        contributions_per_year=contributions_per_year,
        years=years,
    )

    # find the corresponding interest rate
    r = ci_to_rate(
        initial_balance=initial_balance,
        final_balance=K_NP,
        regular_contribution=regular_contribution,
        contributions_per_year=contributions_per_year,
        years=years,
    )
    assert abs(r - annual_interest_rate) < 1e-5, "Computed interest rate is not correct."


def repay():
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


def etf_growth():
    interest_rates = [0.05, 0.06, 0.065, 0.07, 0.075]
    initial_balance = 100_000
    regular_contributions = [2_000, 2_500, 3_000]
    contributions_per_year = 12
    years = 40
    filename = "etf_growth"

    x_axis = [x for x in range(years + 1)]
    # dictionary to print a table in the end
    t_dict = {"year": list(), "rate": list(), "contribution": list(), "balance": list()}

    fig, ax = plt.subplots(2, 1)
    for rate in interest_rates:
        for contribution in regular_contributions:
            y_axis = ci(
                initial_balance=initial_balance,
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
            ax[0].plot(
                x_axis[:26],
                y_axis[:26],
                label=f"r = {rate * 100:.1f}%, c = {contribution / 1e3:.1f}k€",
            )
            ax[1].plot(
                x_axis[26:],
                y_axis[26:],
                label=f"r = {rate * 100:.1f}%, c = {contribution / 1e3:.1f}k€",
            )

    # for table
    with open(filename + ".txt", "w", encoding="utf8") as f:
        df = pd.DataFrame(t_dict)
        table = tabulate(df, headers="keys", tablefmt="psql", showindex=False)
        f.write(table)

    fig.suptitle("ETF growth")
    ax[0].set(ylabel="k€")
    ax[0].grid(which="major", linestyle="-")
    ax[0].grid(which="minor", linestyle="--")
    ax[0].minorticks_on()
    ax[1].legend(bbox_to_anchor=(1.04, 0), loc="lower left")
    ax[1].set(xlabel="years", ylabel="k€")
    ax[1].grid(which="major", linestyle="-")
    ax[1].grid(which="minor", linestyle="--")
    ax[1].minorticks_on()
    fig.savefig(filename + ".png", bbox_inches="tight")
    plt.close()


def house_growth():
    interest_rates = [0.02, 0.03, 0.04, 0.05, 0.08]
    initial_balances = [500_000, 650_000, 800_000]
    regular_contribution = 0
    contributions_per_year = 1
    years = 40
    filename = "house_growth"

    x_axis = [x for x in range(years + 1)]
    # dictionary to print a table in the end
    t_dict = {
        "year": list(),
        "rate": list(),
        "initial_balance": list(),
        "balance": list(),
    }

    fig, ax = plt.subplots(2, 1)
    for rate in interest_rates:
        for initial_balance in initial_balances:
            y_axis = ci(
                initial_balance=initial_balance,
                annual_interest_rate=rate,
                regular_contribution=regular_contribution,
                contributions_per_year=contributions_per_year,
                years=years,
            )[1]

            # convert to k€
            y_axis = [y / 1e3 for y in y_axis]

            # for table
            t_dict["year"].extend(x_axis)
            t_dict["rate"].extend([rate] * (years + 1))
            t_dict["initial_balance"].extend([initial_balance] * (years + 1))
            t_dict["balance"].extend(y_axis)

            # for plot
            ax[0].plot(
                x_axis[:26],
                y_axis[:26],
                label=f"r = {rate * 100:.1f}%, p = {initial_balance / 1e3:.0f}k€",
            )
            ax[1].plot(
                x_axis[26:],
                y_axis[26:],
                label=f"r = {rate * 100:.1f}%, p = {initial_balance / 1e3:.0f}k€",
            )

    # for table
    with open(filename + ".txt", "w", encoding="utf8") as f:
        df = pd.DataFrame(t_dict)
        table = tabulate(df, headers="keys", tablefmt="psql", showindex=False)
        f.write(table)

    fig.suptitle("House growth")
    ax[0].set(ylabel="k€")
    ax[0].grid(which="major", linestyle="-")
    ax[0].grid(which="minor", linestyle="--")
    ax[0].minorticks_on()
    ax[1].legend(bbox_to_anchor=(1.04, 0), loc="lower left")
    ax[1].set(xlabel="years", ylabel="k€")
    ax[1].grid(which="major", linestyle="-")
    ax[1].grid(which="minor", linestyle="--")
    ax[1].minorticks_on()
    fig.savefig(filename + ".png", bbox_inches="tight")
    plt.close()


def main():
    # repay()
    etf_growth()
    house_growth()


if __name__ == "__main__":
    test()
    # main()
