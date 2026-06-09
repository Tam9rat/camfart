"""Tests for the input validation service."""
import pandas as pd
import pytest
from app.services.validation import validate_flagged_rows

_EDITABLE_STAMPERIA = ["Temp_pesa", "Temp_misc", "Temp_press", "Temp_assist_press", "Flag"]
_EDITABLE_FORNO     = ["Pz_inforna", "Flag"]


def _make_row(**kwargs) -> pd.DataFrame:
    base = {"Id": 1, "Flag": True, "Temp_pesa": None, "Temp_misc": None,
            "Temp_press": None, "Temp_assist_press": None}
    base.update(kwargs)
    return pd.DataFrame([base])


def test_valid_row_no_errors() -> None:
    df = _make_row(Temp_pesa=1.5, Temp_misc=0.5, Temp_press=2.0, Temp_assist_press=0.0)
    assert validate_flagged_rows(df, _EDITABLE_STAMPERIA, "Id") == []


def test_none_values_are_allowed() -> None:
    df = _make_row(Temp_pesa=None, Temp_misc=None)
    assert validate_flagged_rows(df, _EDITABLE_STAMPERIA, "Id") == []


def test_negative_time_raises_error() -> None:
    df = _make_row(Temp_pesa=-1.0)
    errors = validate_flagged_rows(df, _EDITABLE_STAMPERIA, "Id")
    assert any("negativo" in e for e in errors)


def test_excessive_time_raises_error() -> None:
    df = _make_row(Temp_pesa=10000.0)
    errors = validate_flagged_rows(df, _EDITABLE_STAMPERIA, "Id")
    assert any("irrealistico" in e for e in errors)


def test_non_numeric_time_raises_error() -> None:
    df = _make_row(Temp_pesa="abc")
    errors = validate_flagged_rows(df, _EDITABLE_STAMPERIA, "Id")
    assert any("numero" in e for e in errors)


def test_valid_piece_count() -> None:
    df = pd.DataFrame([{"Id": 1, "Flag": True, "Pz_inforna": 100}])
    assert validate_flagged_rows(df, _EDITABLE_FORNO, "Id") == []


def test_negative_piece_count_raises_error() -> None:
    df = pd.DataFrame([{"Id": 1, "Flag": True, "Pz_inforna": -5}])
    errors = validate_flagged_rows(df, _EDITABLE_FORNO, "Id")
    assert any("negativo" in e for e in errors)


def test_non_integer_piece_count_raises_error() -> None:
    df = pd.DataFrame([{"Id": 1, "Flag": True, "Pz_inforna": "xyz"}])
    errors = validate_flagged_rows(df, _EDITABLE_FORNO, "Id")
    assert any("intero" in e for e in errors)


def test_multiple_rows_multiple_errors() -> None:
    df = pd.DataFrame([
        {"Id": 1, "Flag": True, "Temp_pesa": -1.0, "Temp_misc": None, "Temp_press": None, "Temp_assist_press": None},
        {"Id": 2, "Flag": True, "Temp_pesa": "bad", "Temp_misc": None, "Temp_press": None, "Temp_assist_press": None},
    ])
    errors = validate_flagged_rows(df, _EDITABLE_STAMPERIA, "Id")
    assert len(errors) == 2
