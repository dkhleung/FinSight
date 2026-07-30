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
