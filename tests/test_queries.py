"""Tests for the SQL query loader and CTE builder."""
import pathlib
import pytest

SQL_DIR = pathlib.Path(__file__).parent.parent / "app" / "queries" / "sql"

DATE_REPORTS = [
    "report_quadratura",
    "report_pezzi_discordanti",
    "report_infornature_parziali",
    "report_riepilogo_commesse",
    "report_non_pesati",
    "report_non_miscelati",
]
SINGOLA_REPORTS = ["report_singola_commessa"]
PLAIN_REPORTS   = [
    "report_imballate_non_evase",
    "report_date_tornitura",
    "report_marcate_non_imballate",
]
EDIT_QUERIES = [
    "stamperia_refresh", "stamperia_confirm",
    "forno_cottura_refresh", "forno_cottura_confirm",
    "tornitura_refresh", "tornitura_confirm",
    "collaudo_refresh", "collaudo_confirm",
]


@pytest.mark.parametrize("name", DATE_REPORTS + SINGOLA_REPORTS + PLAIN_REPORTS + EDIT_QUERIES)
def test_sql_file_exists(name: str) -> None:
    assert (SQL_DIR / f"{name}.sql").exists(), f"Missing SQL file: {name}.sql"


@pytest.mark.parametrize("name", DATE_REPORTS)
def test_date_report_loads_with_base_cte(name: str) -> None:
    from app.queries import load
    sql = load(name)
    assert "WITH lav AS" in sql
    assert "@date_from" in sql
    assert "@date_to" in sql


@pytest.mark.parametrize("name", SINGOLA_REPORTS)
def test_singola_report_loads_with_base_cte(name: str) -> None:
    from app.queries import load
    sql = load(name)
    assert "WITH lav AS" in sql
    assert "@ord_cam" in sql
    assert "@chr_cam" in sql


@pytest.mark.parametrize("name", PLAIN_REPORTS)
def test_plain_report_loads_without_cte(name: str) -> None:
    from app.queries import load
    sql = load(name)
    assert sql.strip() != ""
    assert "WITH lav AS" not in sql


@pytest.mark.parametrize("name", EDIT_QUERIES)
def test_edit_query_loads(name: str) -> None:
    from app.queries import load
    sql = load(name)
    assert sql.strip() != ""
