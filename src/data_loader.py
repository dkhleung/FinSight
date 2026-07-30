"""Load and validate historical market data for FinSight."""

import pandas as pd
import yfinance as yf


# A tuple is suitable because the accepted periods should not change
# while the program is running.
VALID_PERIODS: tuple[str, ...] = (
    "1d",
    "5d",
    "1mo",
    "3mo",
    "6mo",
    "1y",
    "2y",
    "5y",
    "10y",
    "ytd",
    "max",
)

def resolve_ticker(
    company_input: str,
) -> tuple[str, str]:
    """Resolve a company name or ticker into a market symbol."""

    clean_input = str(company_input).strip()

    if len(clean_input) == 0:
        raise ValueError(
            "Company name or ticker must not be empty."
        )

    search_results = yf.Search(
        query=clean_input,
        max_results=8,
        news_count=0,
        lists_count=0,
        enable_fuzzy_query=True,
        recommended=0,
    )

    accepted_types: set[str] = {
        "EQUITY",
    }

    matches: list[dict] = []

    for result in search_results.quotes:
        symbol = result.get("symbol")

        quote_type = str(
            result.get("quoteType", "")
        ).upper()

        if symbol and quote_type in accepted_types:
            matches.append(result)

    if len(matches) == 0:
        raise ValueError(
            f"No company or ticker was found for '{clean_input}'."
        )

    selected_match = matches[0]

    # Prefer an exact ticker match when one exists.
    for result in matches:
        result_symbol = str(
            result.get("symbol", "")
        ).upper()

        if result_symbol == clean_input.upper():
            selected_match = result
            break

    ticker = str(
        selected_match["symbol"]
    ).upper()

    company_name = str(
        selected_match.get("longname")
        or selected_match.get("shortname")
        or ticker
    )

    return ticker, company_name

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
    interval: str = "1d",
) -> pd.DataFrame:
    """Download and validate historical market data."""

    clean_ticker = normalize_ticker(ticker)
    selected_period = validate_period(period)

    stock = yf.Ticker(clean_ticker)

    data = stock.history(
        period=selected_period,
        interval=interval,
        auto_adjust=auto_adjust,
    )

    if data.empty:
        raise ValueError(
            f"No market data was returned for {clean_ticker}."
        )

    data = data.reset_index()

    # Intraday data uses "Datetime" instead of "Date".
    if "Datetime" in data.columns:
        data = data.rename(
            columns={"Datetime": "Date"}
        )

    required_columns: set[str] = {
        "Date",
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
    }

    missing_columns = required_columns.difference(
        data.columns
    )

    if missing_columns:
        raise ValueError(
            "Downloaded data is missing required columns: "
            f"{sorted(missing_columns)}"
        )

    return data
