"""Audit trail service — records every row edit to [audit_log]."""
from __future__ import annotations

import logging

import pandas as pd
from sqlalchemy import text

from app.db.connection import get_engine

logger = logging.getLogger(__name__)

_CREATE_AUDIT_TABLE_SQL = """
IF NOT EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_NAME = 'audit_log'
)
BEGIN
    CREATE TABLE [audit_log] (
        [id]          BIGINT        NOT NULL IDENTITY(1,1) PRIMARY KEY,
        [ts]          DATETIME2     NOT NULL DEFAULT SYSDATETIME(),
        [username]    NVARCHAR(64)  NOT NULL,
        [table_name]  NVARCHAR(64)  NOT NULL,
        [pk_value]    NVARCHAR(64)  NOT NULL,
        [column_name] NVARCHAR(64)  NOT NULL,
        [old_value]   NVARCHAR(MAX) NULL,
        [new_value]   NVARCHAR(MAX) NULL
    );
    CREATE INDEX ix_audit_log_ts         ON [audit_log] ([ts] DESC);
    CREATE INDEX ix_audit_log_table_pk   ON [audit_log] ([table_name],[pk_value]);
    CREATE INDEX ix_audit_log_username   ON [audit_log] ([username]);
END
"""


def ensure_audit_table() -> None:
    """Create [audit_log] if it doesn't exist yet. Safe to call on every startup."""
    with get_engine().begin() as conn:
        conn.execute(text(_CREATE_AUDIT_TABLE_SQL))
    logger.info("audit_log table verified")


def write_audit_entries(
    conn,  # open SQLAlchemy connection (same transaction as the save)
    username: str,
    table_name: str,
    pk_col: str,
    original_row: pd.Series,
    edited_row: pd.Series,
    editable_cols: list[str],
) -> int:
    """Insert one audit row per changed column. Returns number of entries written."""
    pk_value = str(original_row[pk_col])
    entries = 0
    for col in editable_cols:
        if col == "Flag":
            continue  # Flag changes are structural, not data edits worth auditing individually
        old_val = original_row.get(col)
        new_val = edited_row.get(col)

        # Normalise NaN → None for comparison
        try:
            if pd.isna(old_val):
                old_val = None
        except (TypeError, ValueError):
            pass
        try:
            if pd.isna(new_val):
                new_val = None
        except (TypeError, ValueError):
            pass

        if old_val == new_val:
            continue

        conn.execute(
            text("""
                INSERT INTO [audit_log]
                    ([username],[table_name],[pk_value],[column_name],[old_value],[new_value])
                VALUES (:u, :t, :pk, :c, :ov, :nv)
            """),
            {
                "u":  username,
                "t":  table_name,
                "pk": pk_value,
                "c":  col,
                "ov": str(old_val) if old_val is not None else None,
                "nv": str(new_val) if new_val is not None else None,
            },
        )
        entries += 1

    if entries:
        logger.info(
            "Audit: %s edited %s pk=%s → %d column(s) changed",
            username, table_name, pk_value, entries,
        )
    return entries
