"""Web application for the FinSight equity research toolkit."""

import streamlit as st

from src.benchmark import (
    compare_with_benchmark,
    create_benchmark_chart,
)
from src.data_loader import (
    download_stock_data,
    resolve_ticker,
)
from src.financial_metrics import calculate_financial_metrics
from src.risk_metrics import calculate_risk_metrics
from src.visualization import create_stock_charts


st.set_page_config(
    page_title="FinSight",
    page_icon="📊",
    layout="wide",
)

st.title("FinSight")
st.subheader("Python Equity Research Toolkit")

st.write(
    "Enter a listed company name or ticker to generate "
    "market, financial, risk and benchmark analysis."
)

company_input: str = st.text_input(
    "Company name or ticker",
    placeholder="For example: Apple, Microsoft, AAPL or MSFT",
)

period_options: dict[str, dict[str, str]] = {
    "1 day": {
        "period": "1d",
        "interval": "5m",
    },
    "5 days": {
        "period": "5d",
        "interval": "30m",
    },
    "1 month": {
        "period": "1mo",
        "interval": "1d",
    },
    "3 months": {
        "period": "3mo",
        "interval": "1d",
    },
    "6 months": {
        "period": "6mo",
        "interval": "1d",
    },
    "Year to date": {
        "period": "ytd",
        "interval": "1d",
    },
    "1 year": {
        "period": "1y",
        "interval": "1d",
    },
    "2 years": {
        "period": "2y",
        "interval": "1d",
    },
    "5 years": {
        "period": "5y",
        "interval": "1d",
    },
    "10 years": {
        "period": "10y",
        "interval": "1d",
    },
    "Maximum available": {
        "period": "max",
        "interval": "1d",
    },
}

selected_period_label: str = st.selectbox(
    "Analysis period",
    options=list(period_options.keys()),
    index=8,
)

analyse_button: bool = st.button(
    "Analyse company",
    type="primary",
)


if analyse_button:
    if len(company_input.strip()) == 0:
        st.warning(
            "Please enter a company name or ticker."
        )

    else:
        try:
            with st.spinner(
                "Retrieving data and calculating results..."
            ):
                ticker, company_name = resolve_ticker(
                    company_input
                )

                selected_period = period_options[
                    selected_period_label
                ]

                selected_period = selected_settings["period"]
                selected_interval = selected_settings["interval"]

                stock_data = download_stock_data(
                    ticker=ticker,
                    period=selected_period,
                    interval=selected_interval,
                )

                risk_results = calculate_risk_metrics(
                    data=stock_data
                )

                financial_results = (
                    calculate_financial_metrics(
                        ticker=ticker
                    )
                )

                chart_files = create_stock_charts(
                    data=stock_data,
                    ticker=ticker,
                )

                (
                    comparison_data,
                    benchmark_results,
                ) = compare_with_benchmark(
                    ticker=ticker,
                    benchmark="^GSPC",
                    period=selected_period,
                )

                benchmark_chart = (
                    create_benchmark_chart(
                        comparison_data=comparison_data,
                        ticker=ticker,
                        benchmark_name="S&P 500",
                    )
                )

            st.success(
                f"Analysis completed for "
                f"{company_name} ({ticker})."
            )

            st.header("Risk and Return")

            risk_column_1, risk_column_2 = st.columns(2)
            risk_column_3, risk_column_4 = st.columns(2)

            risk_column_1.metric(
                "Annualized return",
                f"{risk_results['annual_return']:.2%}",
            )

            risk_column_2.metric(
                "Annualized volatility",
                f"{risk_results['annual_volatility']:.2%}",
            )

            risk_column_3.metric(
                "Maximum drawdown",
                f"{risk_results['maximum_drawdown']:.2%}",
            )

            risk_column_4.metric(
                "Sharpe ratio",
                f"{risk_results['sharpe_ratio']:.2f}",
            )

            st.header("Financial Performance")

            financial_column_1, financial_column_2 = (
                st.columns(2)
            )

            financial_column_3, financial_column_4 = (
                st.columns(2)
            )

            financial_column_1.metric(
                "Latest revenue",
                (
                    f"USD "
                    f"{financial_results['latest_revenue'] / 1_000_000_000:,.2f}B"
                ),
            )

            financial_column_2.metric(
                "Latest net income",
                (
                    f"USD "
                    f"{financial_results['latest_net_income'] / 1_000_000_000:,.2f}B"
                ),
            )

            financial_column_3.metric(
                "Revenue growth",
                f"{financial_results['revenue_growth']:.2%}",
            )

            financial_column_4.metric(
                "Net profit margin",
                (
                    f"{financial_results['net_profit_margin']:.2%}"
                ),
            )

            st.header("S&P 500 Benchmark Comparison")

            benchmark_column_1, benchmark_column_2 = (
                st.columns(2)
            )

            benchmark_column_3, benchmark_column_4 = (
                st.columns(2)
            )

            benchmark_column_1.metric(
                "Relative annualized return",
                (
                    f"{benchmark_results['relative_annualized_return']:.2%}"
                ),
            )

            benchmark_column_2.metric(
                "Beta",
                f"{benchmark_results['beta']:.2f}",
            )

            benchmark_column_3.metric(
                "Return correlation",
                f"{benchmark_results['correlation']:.2f}",
            )

            benchmark_column_4.metric(
                "S&P 500 annualized return",
                (
                    f"{benchmark_results['benchmark_annualized_return']:.2%}"
                ),
            )

            st.image(
                benchmark_chart,
                caption=(
                    f"{company_name} versus S&P 500"
                ),
            )

            st.header("Market Visualisations")

            chart_captions: list[str] = [
                f"{company_name} historical price",
                f"{company_name} cumulative return",
                f"{company_name} drawdown",
            ]

            for chart_file, chart_caption in zip(
                chart_files,
                chart_captions,
            ):
                st.image(
                    chart_file,
                    caption=chart_caption,
                )

            st.header("Recent Market Data")

            st.dataframe(
                stock_data.tail(10),
                use_container_width=True,
            )

            st.caption(
                "FinSight is an educational research "
                "tool and does not provide investment advice."
            )

        except Exception as error:
            st.error(
                f"FinSight could not complete the analysis: "
                f"{error}"
            )
