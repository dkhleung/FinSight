"""Load and validate historical market data for FinSight."""

import pandas as pd
import yfinance as yf


# A tuple is suitable because the accepted periods should not change
# while the program is running.
VALID_PERIODS: tuple[str, ...] = (
    "1d",
    "5d",
    "1mo",
    "3mo"，
    "6mo",
    "1y",
    "2y",
    "5y",
    "10y",
    "ytd",
    "max",
)


def normalize_ticker(ticker: str) -> str:
    """Clean and validate a stock ticker."""

    clean_ticker = str(ticker).strip().upper()

    if len(clean_ticker) == 0:
        raise ValueError("Ticker must not be empty.")

    return clean_ticker


def validate_period(period: str) -> str:
    """Clean and validate the requested data period."""

    clean_period = str(period).strip().lower()

    if clean_period not in VALID_PERIODS:
        accepted_periods = ", ".join(VALID_PERIODS)
        raise ValueError(
            f"Invalid period '{clean_period}'. "
            f"Choose from: {accepted_periods}."
        )

    return clean_period


def download_stock_data(
    ticker: str,
    period: str = "5y",
    auto_adjust: bool = False,
) -> pd.DataFrame:
    """Download historical stock-price data for one ticker."""

    clean_ticker = normalize_ticker(ticker)
    clean_period = validate_period(period)

    stock = yf.Ticker(clean_ticker)

    data = stock.history(
        period=clean_period,
        auto_adjust=bool(auto_adjust),
    )

    if data.empty:
        raise ValueError(
            f"No market data was found for ticker '{clean_ticker}'."
        )

    cleaned_data = data.reset_index()

    required_columns: list[str] = [
        "Date",
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
    ]

    available_columns = [
        column
        for column in required_columns
        if column in cleaned_data.columns
    ]

    return cleaned_data[available_columns]
