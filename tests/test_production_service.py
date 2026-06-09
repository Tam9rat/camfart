"""Tests for the production service layer (mocked DB)."""
from __future__ import annotations

import io
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from app.services.production import to_excel_bytes


def test_to_excel_bytes_returns_valid_xlsx() -> None:
    df = pd.DataFrame({"A": [1, 2], "B": ["x", "y"]})
    data = to_excel_bytes(df)
    assert isinstance(data, bytes)
    assert len(data) > 0
    # XLSX magic bytes
    assert data[:4] == b"PK\x03\x04"


def test_to_excel_bytes_empty_df() -> None:
    df = pd.DataFrame()
    data = to_excel_bytes(df)
    assert isinstance(data, bytes)
    assert len(data) > 0


@patch("app.services.production.get_engine")
def test_run_report_substitutes_date_params(mock_engine: MagicMock) -> None:
    mock_conn = MagicMock()
    mock_conn.__enter__ = lambda s: s
    mock_conn.__exit__ = MagicMock(return_value=False)
    mock_engine.return_value.connect.return_value = mock_conn

    with patch("app.services.production.pd.read_sql") as mock_read:
        mock_read.return_value = pd.DataFrame({"col": [1]})
        with patch("app.services.production.load_sql") as mock_load:
            mock_load.return_value = "SELECT * WHERE d BETWEEN @date_from AND @date_to"
            from app.services.production import run_report
            df = run_report("report_quadratura", {"date_from": "2024-01-01", "date_to": "2024-12-31"})

    assert len(df) == 1
    call_sql = mock_read.call_args[0][0]
    assert "@date_from" not in str(call_sql)
    assert "2024-01-01" in str(call_sql)
