import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

load_dotenv()

DB_HOST   = os.getenv("DB_HOST")
DB_PORT   = os.getenv("DB_PORT", "1433")
DB_NAME   = os.getenv("DB_NAME")
DB_USER   = os.getenv("DB_USER")
DB_PASS   = os.getenv("DB_PASS")
DB_DRIVER = os.getenv("DB_DRIVER", "ODBC+Driver+17+for+SQL+Server")


def get_engine():
    connection_string = (
        f"mssql+pyodbc://{quote_plus(DB_USER)}:{quote_plus(DB_PASS)}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        f"?driver={DB_DRIVER}"
        f"&TrustServerCertificate=yes"
    )
    return create_engine(connection_string, fast_executemany=True)

def execute_query(sql: str) -> str:
    try:
        engine = get_engine()
        raw_conn = engine.raw_connection()
        try:
            cursor = raw_conn.cursor()
            statements = [s.strip() for s in sql.split(";") if s.strip()]
            for stmt in statements:
                if stmt.upper().startswith("MERGE"):
                    stmt = stmt + ";"
                cursor.execute(stmt)
            raw_conn.commit()
            cursor.close()
        finally:
            raw_conn.close()
        return "ok"
    except Exception as e:
        return str(e)


def get_public_tables() -> list[str]:
    """Return all user table names from the current database."""
    sql = """
        SELECT TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_NAME
    """
    return pd.read_sql(sql, get_engine())["TABLE_NAME"].tolist()


def load_table_data(table_name: str, limit: int = None) -> pd.DataFrame:
    if limit:
        sql = text(f"SELECT TOP {limit} * FROM [{table_name}]")
    else:
        sql = text(f"SELECT * FROM [{table_name}]")
    
    df = pd.read_sql(sql, get_engine())

    if "Id" in df.columns:
        df = df[["Id"] + [c for c in df.columns if c != "Id"]]

    if "Flag" in df.columns:
        df["Flag"] = df["Flag"].fillna(0).astype(bool)

    return df