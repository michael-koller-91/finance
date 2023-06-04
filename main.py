def ci(
    initial_investment,
    annual_interest_rate,
    regular_contribution,
    contributions_per_year,
    years,
):
    """Compound interest."""
    balance = initial_investment
    # convert annual interest rate to interest rate per contribution time interval (+ 1)
    r = (1 + annual_interest_rate) ** (1 / contributions_per_year)
    for _ in range(years):
        for _ in range(contributions_per_year):
            # grow until next contribution
            balance *= r
            # next contribution
            balance += regular_contribution
    return balance


def main():
    balance = ci(
        initial_investment=5000,
        annual_interest_rate=0.03,
        regular_contribution=100,
        contributions_per_year=12,
        years=5,
    )
    print(f"{balance:.2f}")


if __name__ == "__main__":
    main()
