"""Automated tests for the main FinSight functions."""

import pandas as pd
import pytest

from src.data_loader import normalize_ticker, validate_period
from src.risk_metrics import calculate_risk_metrics

def test_normalize_ticker() -> None:
    """Ticker input should be cleaned and converted to uppercase."""

    result = normalize_ticker("  msft  ")
    assert result == "MSFT"


def test_validate_period() -> None:
    """A supported analysis period should be accepted."""

    result = validate_period("5Y")
    assert result == "5y"


def test_invalid_period() -> None:
    """An unsupported period should produce an error."""

    with pytest.raises(ValueError):
        validate_period("7years")


def test_risk_metrics_output() -> None:
    """Risk analysis should return the expected metrics."""

    prices = [
        float(price)
        for price in range(100, 140)
    ]

    sample_data = pd.DataFrame(
        {
            "Close": prices,
        }
    )

    results = calculate_risk_metrics(
        data=sample_data,
        risk_free_rate=0.0,
    )

    expected_metrics = {
        "annual_return",
        "annual_volatility",
        "maximum_drawdown",
        "sharpe_ratio",
    }

    assert set(results.keys()) == expected_metrics

    for value in results.values():
        assert isinstance(value, float)

def test_missing_close_column() -> None:
    """Risk analysis should reject data without closing prices."""

    sample_data = pd.DataFrame(
        {
            "Open": [100.0, 101.0, 102.0],
        }
    )

    with pytest.raises(ValueError):
        calculate_risk_metrics(sample_data)
