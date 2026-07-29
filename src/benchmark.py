"""Compare a stock with a selected market benchmark."""

from math import sqrt
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from src.data_loader import download_stock_data

TRADING_DAYS_PER_YEAR: int = 252

def compare_with_benchmark(
    ticker: str,
    benchmark: str = "^GSPC",
    period: str = "5y",
) -> tuple[pd.DataFrame, dict[str, float]]:
    """Compare stock performance with a market benchmark."""

    stock_data = download_stock_data(
        ticker=ticker,
        period=period,
    )

    benchmark_data = download_stock_data(
        ticker=benchmark,
        period=period,
    )

    # Keep only the date and closing price.
    stock_data = stock_data[
        ["Date", "Close"]
    ].copy()

    benchmark_data = benchmark_data[
        ["Date", "Close"]
    ].copy()

    # Remove timezone differences before combining the datasets.
    stock_data["Date"] = pd.to_datetime(
        stock_data["Date"],
        utc=True,
    ).dt.tz_convert(None)

    benchmark_data["Date"] = pd.to_datetime(
        benchmark_data["Date"],
        utc=True,
    ).dt.tz_convert(None)

    stock_data = stock_data.rename(
        columns={"Close": "stock_close"}
    )

    benchmark_data = benchmark_data.rename(
        columns={"Close": "benchmark_close"}
    )

    # Keep only dates available for both the stock and benchmark.
    comparison_data = pd.merge(
        stock_data,
        benchmark_data,
        on="Date",
        how="inner",
    ).dropna()

    if len(comparison_data) < 30:
        raise ValueError("At least 30 shared observations are required.")

    comparison_data["stock_return"] = (comparison_data["stock_close"].pct_change())

    comparison_data["benchmark_return"] = (comparison_data["benchmark_close"].pct_change())

    comparison_data["stock_cumulative_return"] = ((1 + comparison_data["stock_return"].fillna(0)).cumprod() - 1)

    comparison_data["benchmark_cumulative_return"] = ((1 + comparison_data["benchmark_return"].fillna(0)).cumprod() - 1)

    return_data = comparison_data[["stock_return", "benchmark_return"]].dropna()

    number_of_returns = len(return_data)

    stock_total_growth = (1 + return_data["stock_return"]).prod()

    benchmark_total_growth = (1 + return_data["benchmark_return"]).prod()

    stock_annualized_return = (
        stock_total_growth
        ** (
            TRADING_DAYS_PER_YEAR
            / number_of_returns
        )
        - 1
    )

    benchmark_annualized_return = (
        benchmark_total_growth
        ** (
            TRADING_DAYS_PER_YEAR
            / number_of_returns
        )
        - 1
    )

    stock_volatility = (
        return_data["stock_return"].std()
        * sqrt(TRADING_DAYS_PER_YEAR)
    )

    benchmark_volatility = (
        return_data["benchmark_return"].std()
        * sqrt(TRADING_DAYS_PER_YEAR)
    )

    benchmark_variance = (
        return_data["benchmark_return"].var()
    )

    if benchmark_variance == 0:
        beta = 0.0
    else:
        beta = (
            return_data["stock_return"].cov(
                return_data["benchmark_return"]
            )
            / benchmark_variance
        )

    correlation = return_data["stock_return"].corr(
        return_data["benchmark_return"]
    )

    relative_return = (
        stock_annualized_return
        - benchmark_annualized_return
    )

    benchmark_results: dict[str, float] = {
        "stock_annualized_return": float(
            stock_annualized_return
        ),
        "benchmark_annualized_return": float(
            benchmark_annualized_return
        ),
        "relative_annualized_return": float(
            relative_return
        ),
        "stock_volatility": float(
            stock_volatility
        ),
        "benchmark_volatility": float(
            benchmark_volatility
        ),
        "beta": float(beta),
        "correlation": float(correlation),
    }

    return comparison_data, benchmark_results

def create_benchmark_chart(
    comparison_data: pd.DataFrame,
    ticker: str,
    benchmark_name: str = "S&P 500",
    output_folder: str = "outputs",
) -> str:
    """Create a cumulative-return comparison chart."""

    required_columns = {
        "Date",
        "stock_cumulative_return",
        "benchmark_cumulative_return",
    }

    if not required_columns.issubset(comparison_data.columns):
        raise ValueError(
            "The comparison dataset is missing required columns."
        )

    clean_ticker = str(ticker).strip().upper()

    output_path = Path(output_folder)
    output_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    chart_file = (
        output_path
        / f"{clean_ticker}_vs_sp500.png"
    )

    plt.figure(figsize=(10, 5))

    plt.plot(
        comparison_data["Date"],
        comparison_data["stock_cumulative_return"],
        label=clean_ticker,
    )

    plt.plot(
        comparison_data["Date"],
        comparison_data["benchmark_cumulative_return"],
        label=benchmark_name,
    )

    plt.title(
        f"{clean_ticker} versus {benchmark_name}"
    )

    plt.xlabel("Date")
    plt.ylabel("Cumulative Return")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(chart_file)
    plt.close()

    return str(chart_file)
