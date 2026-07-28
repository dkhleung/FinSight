"""Create charts for the FinSight project."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

def create_stock_charts(
    data: pd.DataFrame,
    ticker: str,
    output_folder: str = "outputs",
) -> list[str]:
    """Create price, cumulative-return, and drawdown charts."""

    required_columns = {"Date", "Close"}

    if not required_columns.issubset(data.columns):
        raise ValueError(
            "The dataset must contain Date and Close columns."
        )

    chart_data = data[["Date", "Close"]].copy()

    chart_data["Date"] = pd.to_datetime(
        chart_data["Date"]
    )

    chart_data["Close"] = pd.to_numeric(
        chart_data["Close"],
        errors="coerce",
    )

    chart_data = chart_data.dropna()

    if len(chart_data) < 2:
        raise ValueError(
            "At least two observations are required."
        )

    clean_ticker = str(ticker).strip().upper()

    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)

    saved_files: list[str] = []

    # Closing-price chart
    price_file = output_path / f"{clean_ticker}_price.png"

    plt.figure(figsize=(10, 5))
    plt.plot(
        chart_data["Date"],
        chart_data["Close"],
    )
    plt.title(f"{clean_ticker} Historical Closing Price")
    plt.xlabel("Date")
    plt.ylabel("Closing Price")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(price_file)
    plt.close()

    saved_files.append(str(price_file))

    # Cumulative-return chart
    daily_returns = chart_data["Close"].pct_change()
    cumulative_returns = (1 + daily_returns).cumprod() - 1

    cumulative_file = (
        output_path
        / f"{clean_ticker}_cumulative_return.png"
    )

    plt.figure(figsize=(10, 5))
    plt.plot(
        chart_data["Date"],
        cumulative_returns,
    )
    plt.title(f"{clean_ticker} Cumulative Return")
    plt.xlabel("Date")
    plt.ylabel("Cumulative Return")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(cumulative_file)
    plt.close()

    saved_files.append(str(cumulative_file))

    # Drawdown chart
    running_peak = chart_data["Close"].cummax()

    drawdown = (
        chart_data["Close"] / running_peak
    ) - 1

    drawdown_file = (
        output_path
        / f"{clean_ticker}_drawdown.png"
    )

    plt.figure(figsize=(10, 5))
    plt.plot(
        chart_data["Date"],
        drawdown,
    )
    plt.title(f"{clean_ticker} Drawdown")
    plt.xlabel("Date")
    plt.ylabel("Drawdown")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(drawdown_file)
    plt.close()

    saved_files.append(str(drawdown_file))

    return saved_files
