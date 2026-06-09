from __future__ import annotations

import logging
import os
from urllib.parse import quote_plus

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import Engine, create_engine, text

load_dotenv()

logger = logging.getLogger(__name__)

_engine: Engine | None = None


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        user   = quote_plus(os.environ["DB_USER"])
        pwd    = quote_plus(os.environ["DB_PASS"])
        host   = os.environ["DB_HOST"]
        port   = os.getenv("DB_PORT", "1433")
        name   = os.environ["DB_NAME"]
        driver = os.getenv("DB_DRIVER", "ODBC+Driver+17+for+SQL+Server")
        trust  = os.getenv("DB_TRUST_SERVER_CERT", "no")
        dsn = (
            f"mssql+pyodbc://{user}:{pwd}@{host}:{port}/{name}"
            f"?driver={driver}&TrustServerCertificate={trust}"
        )
        _engine = create_engine(dsn, fast_executemany=True, pool_pre_ping=True)
        logger.info("DB engine created → %s:%s/%s", host, port, name)
    return _engine


def execute_query(sql: str) -> str:
    """Run one or more semicolon-separated T-SQL statements. Returns 'ok' or error string."""
    try:
        engine = get_engine()
        raw = engine.raw_connection()
        try:
            cur = raw.cursor()
            for stmt in (s.strip() for s in sql.split(";") if s.strip()):
                if stmt.upper().startswith("MERGE"):
                    stmt += ";"
                cur.execute(stmt)
            raw.commit()
            cur.close()
        finally:
            raw.close()
        logger.debug("execute_query OK (%d chars)", len(sql))
        return "ok"
    except Exception as exc:
        logger.error("execute_query failed: %s", exc)
        return str(exc)


def get_public_tables() -> list[str]:
    sql = """
        SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_TYPE = 'BASE TABLE' ORDER BY TABLE_NAME
    """
    result = pd.read_sql(sql, get_engine())["TABLE_NAME"].tolist()
    logger.debug("get_public_tables → %d tables", len(result))
    return result


def load_table_data(table_name: str) -> pd.DataFrame:
    df = pd.read_sql(text(f"SELECT * FROM [{table_name}]"), get_engine())
    if "Id" in df.columns:
        df = df[["Id"] + [c for c in df.columns if c != "Id"]]
    if "Flag" in df.columns:
        df["Flag"] = df["Flag"].fillna(0).astype(bool)
    logger.debug("load_table_data '%s' → %d rows", table_name, len(df))
    return df
