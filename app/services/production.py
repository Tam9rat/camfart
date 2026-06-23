"""Business logic layer — sits between the UI pages and the DB/query modules."""
from __future__ import annotations

import io
import logging

import pandas as pd
from sqlalchemy import text

from app.db.connection import get_engine, execute_query
from app.queries import load as load_sql
from app.config.table_config import TABLE_CONFIG

logger = logging.getLogger(__name__)


def refresh_table(table_name: str) -> str:
    """Sync staging table from source tables via MERGE. Returns 'ok' or error."""
    cfg = TABLE_CONFIG[table_name]
    logger.info("Refresh %s", table_name)
    return execute_query(load_sql(cfg["refresh_query"]))


def save_flagged_rows(table_name: str, edited_df: pd.DataFrame, username: str) -> int:
    """Persist flagged rows and confirm them. Returns count of saved rows."""
    cfg = TABLE_CONFIG[table_name]
    flagged = edited_df[edited_df["Flag"] == True]
    if flagged.empty:
        return 0

    def _clean(val: object) -> object:
        if val is None or isinstance(val, bool):
            return val
        try:
            if pd.isna(val):
                return None
        except (TypeError, ValueError):
            pass
        return val

    pk_col = cfg["pk"]

    with get_engine().begin() as conn:
        for _, row in flagged.iterrows():
            params: dict[str, object] = {}
            for col in cfg["editable_cols"]:
                val = row[col]
                params[col] = bool(val) if col == "Flag" else _clean(val)
            params[pk_col] = int(row[pk_col])
            conn.execute(text(cfg["update_sql"]), params)

        conn.execute(text(load_sql(cfg["confirm_query"])))

    count = len(flagged)
    logger.info("Saved %d rows in %s by %s", count, table_name, username)
    return count


def run_report(query_name: str, params: dict[str, object]) -> pd.DataFrame:
    """Execute a report query, substituting named @params, with 5-minute caching."""
    sql = load_sql(query_name)

    if "date_from" in params:
        sql = sql.replace("@date_from", f"'{params['date_from']}'")
        sql = sql.replace("@date_to",   f"'{params['date_to']}'")
    if "ord_cam" in params:
        sql = sql.replace("@ord_cam", f"'{params['ord_cam']}'")
        sql = sql.replace("@chr_cam", f"'{params['chr_cam']}'")

    with get_engine().connect() as conn:
        df = pd.read_sql(text(sql), conn)
    logger.info("Report '%s' returned %d rows", query_name, len(df))
    return df


def to_excel_bytes(df: pd.DataFrame) -> bytes:
    """Serialize a DataFrame to an Excel file in memory and return raw bytes."""
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Report")
    return buf.getvalue()
