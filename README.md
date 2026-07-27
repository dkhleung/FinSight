# FinSight

FinSight is a Python-based equity research toolkit that combines financial
statement analysis, valuation, market risk analysis, and explainable investment
insights.

The project demonstrates how public financial and market data can be converted
into structured and decision-useful analysis.

## Planned Features

- Retrieve public financial and stock-market data
- Analyse revenue growth, margins, and profitability
- Calculate financial and valuation ratios
- Measure returns, volatility, and maximum drawdown
- Compare a company with selected peers or market benchmarks
- Generate charts and a concise investment summary
- Extend the analysis with CAPM and regression modelling

## Initial Demonstration

Microsoft Corporation (`MSFT`) will be used as the first demonstration company.

The project will later be designed to accept other stock tickers.

## Technology

- Python
- pandas
- NumPy
- matplotlib
- yfinance
- scikit-learn
- Jupyter Notebook

## Project Structure

```text
FinSight/
├── data/           # Local datasets
├── notebooks/      # Exploratory analysis
├── outputs/        # Generated charts and reports
├── src/            # Reusable Python modules
├── tests/          # Project tests
├── requirements.txt
└── README.md
