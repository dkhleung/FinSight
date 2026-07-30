"""Command-line interface for the FinSight project."""

import pandas as pd

from src.data_loader import (
    VALID_PERIODS,
    download_stock_data,
    resolve_ticker,
)
from src.financial_metrics import calculate_financial_metrics
from src.risk_metrics import calculate_risk_metrics
from src.visualization import create_stock_charts

def calculate_price_summary(
    data: pd.DataFrame,
) -> tuple[int, float, float, float]:
    """Calculate basic descriptive statistics for closing prices."""

    closing_prices: list[float] = [
        float(price)
        for price in data["Close"].dropna()
    ]

    if len(closing_prices) == 0:
        raise ValueError("No valid closing prices were found.")

    number_of_prices: int = len(closing_prices)
    average_close: float = sum(closing_prices) / number_of_prices
    minimum_close: float = min(closing_prices)
    maximum_close: float = max(closing_prices)

    return (
        number_of_prices,
        average_close,
        minimum_close,
        maximum_close,
    )


def print_stock_summary(
    ticker: str,
    data: pd.DataFrame,
) -> None:
    """Print a simple summary of the downloaded stock data."""

    (
        number_of_prices,
        average_close,
        minimum_close,
        maximum_close,
    ) = calculate_price_summary(data)

    print("\nFinSight Stock Summary")
    print("----------------------")
    print(f"Ticker: {str(ticker).upper()}")
    print(f"Number of observations: {number_of_prices}")
    print(f"Average closing price: {average_close:.2f}")
    print(f"Minimum closing price: {minimum_close:.2f}")
    print(f"Maximum closing price: {maximum_close:.2f}")

    print("\nFirst five observations:")
    print(data.head())


def main() -> None:
    """Run the interactive FinSight program."""

    continue_program: bool = True

    print("Welcome to FinSight.")
    print("Enter 'quit' when you want to close the program.")

    while continue_program:
        company_input: str = input(
            "\nEnter a company name or ticker "
            "(for example, Apple or AAPL): "
        ).strip()
        
        if company_input.lower() == "quit":
            continue_program = False
        else:
            ticker_input, company_name = resolve_ticker(
                company_input
            )
            
            print(
                f"Selected company: "
                f"{company_name} ({ticker_input})"
            )
            
            print(
                "Available periods:",
                ", ".join(VALID_PERIODS),
            )

            period_input: str = input(
                "Enter a period, or press Enter for 1y: "
            ).strip()

            if len(period_input) == 0:
                period_input = "1y"

            try:
                stock_data = download_stock_data(
                    ticker=ticker_input,
                    period=period_input,
                    auto_adjust=False,
                )

                print_stock_summary(
                    ticker=ticker_input,
                    data=stock_data,
                )
                
                risk_results = calculate_risk_metrics(
                    data=stock_data, 
                    risk_free_rate=0.0,
                )
                
                print("\nRisk Metrics")
                print("------------")
                print(
                    f"Annual return: "
                    f"{risk_results['annual_return']:.2%}"
                )
                print(
                    f"Annual volatility: "
                    f"{risk_results['annual_volatility']:.2%}"
                )
                print(
                    f"Maximum drawdown: "
                    f"{risk_results['maximum_drawdown']:.2%}"
                )
                print(
                    f"Sharpe ratio: "
                    f"{risk_results['sharpe_ratio']:.2f}"
                )
                
                financial_results = calculate_financial_metrics(
                    ticker=ticker_input
                )
                
                print("\nFinancial Metrics")
                print("-----------------")
                print(
                    f"Latest revenue: "
                    f"{financial_results['latest_revenue'] / 1_000_000_000:,.2f} billion"
                )
                print(
                    f"Latest net income: "
                    f"{financial_results['latest_net_income'] / 1_000_000_000:,.2f} billion"
                )
                print(
                    f"Revenue growth: "
                    f"{financial_results['revenue_growth']:.2%}"
                )
                print(
                    f"Net income growth: "
                    f"{financial_results['net_income_growth']:.2%}"
                )
                print(
                    f"Net profit margin: "
                    f"{financial_results['net_profit_margin']:.2%}"
                )
                
                chart_files = create_stock_charts(
                    data=stock_data,
                    ticker=ticker_input,
                )
                
                print("\nCharts")
                print("------")
                
                for file_name in chart_files:
                    print(f"Saved: {file_name}")

            except ValueError as error:
                print(f"Input error: {error}")

            except Exception as error:
                print(
                    "Unexpected error:",
                    type(error).__name__,
                    str(error),
                )

            else:
                accepted_answers: set[str] = {
                    "y",
                    "yes",
                }

                answer: str = input(
                    "\nAnalyse another ticker? (yes/no): "
                ).strip().lower()

                continue_program = answer in accepted_answers

    print("FinSight has been closed.")


if __name__ == "__main__":
    main()
