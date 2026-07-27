"""Functions for loading financial and market data."""

import pandas as pd
import yfinance as yf


def download_stock_data(
    ticker: str,
    period: str = "5y",
) -> pd.DataFrame:
    """Download historical stock-price data for one ticker."""

    clean_ticker = ticker.strip().upper()

    if not clean_ticker:
        raise ValueError("Ticker must not be empty.")

    data = yf.Ticker(clean_ticker).history(
        period=period,
        auto_adjust=False,
    )

    if data.empty:
        raise ValueError(
            f"No market data found for ticker: {clean_ticker}"
        )

    data = data.reset_index()

    return data
