"""Tests for table_config structure integrity."""
import pytest
from app.config.table_config import TABLE_CONFIG, REPORT_CONFIG, GROUP_TABLES, ROLE_PERMISSIONS


def test_all_group1_tables_in_config() -> None:
    for t in GROUP_TABLES["Group 1"]:
        assert t in TABLE_CONFIG, f"Group 1 table '{t}' missing from TABLE_CONFIG"


def test_all_group2_reports_in_config() -> None:
    for r in GROUP_TABLES["Group 2"]:
        assert r in REPORT_CONFIG, f"Group 2 report '{r}' missing from REPORT_CONFIG"


def test_each_table_has_required_keys() -> None:
    required = {"refresh_query", "confirm_query", "disabled_cols", "editable_cols", "update_sql", "pk"}
    for name, cfg in TABLE_CONFIG.items():
        missing = required - cfg.keys()
        assert not missing, f"TABLE_CONFIG['{name}'] missing keys: {missing}"


def test_each_report_has_required_keys() -> None:
    for name, cfg in REPORT_CONFIG.items():
        assert "inputs" in cfg, f"REPORT_CONFIG['{name}'] missing 'inputs'"
        assert "query"  in cfg, f"REPORT_CONFIG['{name}'] missing 'query'"


def test_role_permissions_cover_all_tables_and_reports() -> None:
    for role, perms in ROLE_PERMISSIONS.items():
        for t in perms.get("tables", []):
            assert t in TABLE_CONFIG, f"Role '{role}' references unknown table '{t}'"
        for r in perms.get("reports", []):
            assert r in REPORT_CONFIG, f"Role '{role}' references unknown report '{r}'"


def test_pk_column_in_disabled_cols() -> None:
    for name, cfg in TABLE_CONFIG.items():
        assert cfg["pk"] in cfg["disabled_cols"], (
            f"TABLE_CONFIG['{name}']: pk '{cfg['pk']}' should be in disabled_cols"
        )
