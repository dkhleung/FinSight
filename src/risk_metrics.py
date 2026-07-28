"""Calculate investment risk and return metrics for FinSight."""

from math import sqrt

import pandas as pd


TRADING_DAYS_PER_YEAR: int = 252


def calculate_daily_returns(
    data: pd.DataFrame,
    price_column: str = "Close",
) -> pd.Series:
    """Calculate daily percentage returns from historical prices."""

    if price_column not in data.columns:
        raise ValueError(
            f"Column '{price_column}' was not found in the dataset."
        )

    closing_prices = pd.to_numeric(
        data[price_column],
        errors="coerce",
    ).dropna()

    if len(closing_prices) < 2:
        raise ValueError(
            "At least two valid prices are required."
        )

    daily_returns = closing_prices.pct_change().dropna()

    return daily_returns


def calculate_annualized_return(
    daily_returns: pd.Series,
    trading_days: int = TRADING_DAYS_PER_YEAR,
) -> float:
    """Calculate the compounded annualized return."""

    if len(daily_returns) == 0:
        raise ValueError("Daily returns must not be empty.")

    compounded_growth: float = float(
        (1 + daily_returns).prod()
    )

    number_of_observations: int = len(daily_returns)

    annualized_return: float = (
        compounded_growth
        ** (trading_days / number_of_observations)
    ) - 1

    return annualized_return


def calculate_annualized_volatility(
    daily_returns: pd.Series,
    trading_days: int = TRADING_DAYS_PER_YEAR,
) -> float:
    """Calculate annualized volatility from daily returns."""

    if len(daily_returns) < 2:
        raise ValueError(
            "At least two daily returns are required."
        )

    daily_volatility: float = float(
        daily_returns.std(ddof=1)
    )

    annualized_volatility: float = (
        daily_volatility * sqrt(trading_days)
    )

    return annualized_volatility


def calculate_maximum_drawdown(
    data: pd.DataFrame,
    price_column: str = "Close",
) -> float:
    """Calculate the largest peak-to-trough price decline."""

    if price_column not in data.columns:
        raise ValueError(
            f"Column '{price_column}' was not found."
        )

    closing_prices = pd.to_numeric(
        data[price_column],
        errors="coerce",
    ).dropna()

    if len(closing_prices) == 0:
        raise ValueError("No valid closing prices were found.")

    wealth_index = closing_prices / closing_prices.iloc[0]
    running_peak = wealth_index.cummax()
    drawdowns = (wealth_index / running_peak) - 1

    maximum_drawdown: float = float(drawdowns.min())

    return maximum_drawdown


def calculate_sharpe_ratio(
    annualized_return: float,
    annualized_volatility: float,
    risk_free_rate: float = 0.0,
) -> float:
    """Calculate the annualized Sharpe ratio."""

    if annualized_volatility <= 0:
        raise ValueError(
            "Annualized volatility must be greater than zero."
        )

    sharpe_ratio: float = (
        annualized_return - risk_free_rate
    ) / annualized_volatility

    return sharpe_ratio


def build_risk_summary(
    data: pd.DataFrame,
    price_column: str = "Close",
    risk_free_rate: float = 0.0,
) -> dict[str, float]:
    """Calculate and return the main risk and return metrics."""

    daily_returns = calculate_daily_returns(
        data=data,
        price_column=price_column,
    )

    annualized_return = calculate_annualized_return(
        daily_returns
    )

    annualized_volatility = calculate_annualized_volatility(
        daily_returns
    )

    maximum_drawdown = calculate_maximum_drawdown(
        data=data,
        price_column=price_column,
    )

    sharpe_ratio = calculate_sharpe_ratio(
        annualized_return=annualized_return,
        annualized_volatility=annualized_volatility,
        risk_free_rate=risk_free_rate,
    )

    risk_summary: dict[str, float] = {
        "annualized_return": annualized_return,
        "annualized_volatility": annualized_volatility,
        "maximum_drawdown": maximum_drawdown,
        "sharpe_ratio": sharpe_ratio,
    }

    return risk_summary
