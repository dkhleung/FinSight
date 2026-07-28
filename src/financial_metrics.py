"""Functions for calculating financial and valuation metrics."""
"""Basic financial statement calculations for FinSight."""

import pandas as pd
import yfinance as yf

def calculate_financial_metrics(
    ticker: str,
) -> dict[str, float]:
    """Calculate basic annual financial metrics for a company."""

    clean_ticker = ticker.strip().upper()

    if len(clean_ticker) == 0:
        raise ValueError("Ticker must not be empty.")

    company = yf.Ticker(clean_ticker)
    income_statement = company.income_stmt

    if income_statement.empty:
        raise ValueError(f"No income statement was found for {clean_ticker}.")

    # Arrange the newest financial year first
    income_statement = income_statement.reindex(
        sorted(income_statement.columns, reverse=True),
        axis=1,
    )

    if "Total Revenue" not in income_statement.index:
        raise ValueError("Total Revenue was not found.")

    if "Net Income" not in income_statement.index:
        raise ValueError("Net Income was not found.")

    revenues = pd.to_numeric(
        income_statement.loc["Total Revenue"],
        errors="coerce",
    ).dropna()

    net_incomes = pd.to_numeric(
        income_statement.loc["Net Income"],
        errors="coerce",
    ).dropna()

    if len(revenues) < 2 or len(net_incomes) < 2:
        raise ValueError("At least two years of financial data are required.")

    latest_revenue = float(revenues.iloc[0])
    previous_revenue = float(revenues.iloc[1])

    latest_net_income = float(net_incomes.iloc[0])
    previous_net_income = float(net_incomes.iloc[1])

    if (
        previous_revenue == 0
        or previous_net_income == 0
        or latest_revenue == 0
    ):
        raise ValueError(
            "Financial values cannot be zero for these calculations."
        )

    revenue_growth = (latest_revenue / previous_revenue) - 1

    net_income_growth = (latest_net_income / previous_net_income) - 1

    net_profit_margin = (latest_net_income / latest_revenue)

    return {
        "latest_revenue": latest_revenue,
        "latest_net_income": latest_net_income,
        "revenue_growth": revenue_growth,
        "net_income_growth": net_income_growth,
        "net_profit_margin": net_profit_margin,
    }
