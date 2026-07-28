"""Calculate investment risk and return metrics for FinSight."""

"""Basic risk and return calculations for FinSight."""

from math import sqrt
import pandas as pd

def calculate_risk_metrics(
    data: pd.DataFrame, 
    risk_free_rate: float = 0.0,
) -> dict[str, float]:
    """Calculate basic investment risk metrics."""

    if "Close" not in data.columns:
        raise ValueError("The dataset must contain a Close column.")

    prices = data["Close"].dropna()

    if len(prices) < 2:
        raise ValueError("At least two prices are required.")

    # Calculate daily returns
    daily_returns = prices.pct_change().dropna()

    # Calculate compounded annual return
    total_growth = (1 + daily_returns).prod()
    annual_return = (total_growth ** (252 / len(daily_returns))) - 1

    # Calculate annual volatility
    annual_volatility = (daily_returns.std() * sqrt(252))

    # Calculate maximum drawdown
    running_peak = prices.cummax()
    drawdowns = (prices / running_peak) - 1
    maximum_drawdown = drawdowns.min()

    # Calculate Sharpe ratio
    if annual_volatility == 0:
        sharpe_ratio = 0.0
    else:
        sharpe_ratio = (annual_return - risk_free_rate) / annual_volatility

    return {
        "annual_return": float(annual_return),
        "annual_volatility": float(annual_volatility),
        "maximum_drawdown": float(maximum_drawdown),
        "sharpe_ratio": float(sharpe_ratio),
    }
