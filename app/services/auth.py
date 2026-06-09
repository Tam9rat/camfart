"""DB-backed user authentication service.

Users are stored in the [app_users] table, not config.yaml.
Password hashes use bcrypt (same scheme as streamlit-authenticator).
"""
from __future__ import annotations

import logging

import bcrypt
import pandas as pd
from sqlalchemy import text

from app.db.connection import get_engine

logger = logging.getLogger(__name__)

_CREATE_TABLE_SQL = """
IF NOT EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_NAME = 'app_users'
)
BEGIN
    CREATE TABLE [app_users] (
        [username]     NVARCHAR(64)  NOT NULL PRIMARY KEY,
        [password_hash] NVARCHAR(256) NOT NULL,
        [role]         NVARCHAR(32)  NOT NULL DEFAULT 'viewer',
        [email]        NVARCHAR(128) NULL,
        [first_name]   NVARCHAR(64)  NULL,
        [last_name]    NVARCHAR(64)  NULL,
        [is_active]    BIT           NOT NULL DEFAULT 1,
        [created_at]   DATETIME2     NOT NULL DEFAULT SYSDATETIME(),
        [last_login]   DATETIME2     NULL
    )
END
"""


def ensure_users_table() -> None:
    """Create [app_users] if it doesn't exist yet. Safe to call on every startup."""
    with get_engine().begin() as conn:
        conn.execute(text(_CREATE_TABLE_SQL))
    logger.info("app_users table verified")


def load_users_for_authenticator() -> dict:
    """Return a credentials dict compatible with streamlit-authenticator."""
    df = pd.read_sql(
        text("SELECT * FROM [app_users] WHERE [is_active] = 1"),
        get_engine(),
    )
    usernames: dict = {}
    for _, row in df.iterrows():
        usernames[row["username"]] = {
            "email":      row["email"] or "",
            "first_name": row["first_name"] or "",
            "last_name":  row["last_name"] or "",
            "name":       f"{row['first_name'] or ''} {row['last_name'] or ''}".strip(),
            "password":   row["password_hash"],
            "logged_in":  False,
            "role":       row["role"],
        }
    return {"usernames": usernames}


def get_user_role(username: str) -> str:
    with get_engine().connect() as conn:
        row = conn.execute(
            text("SELECT [role] FROM [app_users] WHERE [username] = :u AND [is_active] = 1"),
            {"u": username},
        ).fetchone()
    return row[0] if row else "viewer"


def record_login(username: str) -> None:
    with get_engine().begin() as conn:
        conn.execute(
            text("UPDATE [app_users] SET [last_login] = SYSDATETIME() WHERE [username] = :u"),
            {"u": username},
        )
    logger.info("Login recorded for '%s'", username)


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def create_user(
    username: str,
    plain_password: str,
    role: str = "viewer",
    email: str = "",
    first_name: str = "",
    last_name: str = "",
) -> None:
    pw_hash = hash_password(plain_password)
    with get_engine().begin() as conn:
        conn.execute(
            text("""
                MERGE [app_users] AS tgt
                USING (VALUES (:u, :ph, :r, :e, :fn, :ln)) AS src
                    (username, password_hash, role, email, first_name, last_name)
                ON tgt.[username] = src.username
                WHEN MATCHED THEN UPDATE SET
                    [password_hash]=src.password_hash,[role]=src.role,
                    [email]=src.email,[first_name]=src.first_name,[last_name]=src.last_name
                WHEN NOT MATCHED THEN INSERT
                    ([username],[password_hash],[role],[email],[first_name],[last_name])
                VALUES (src.username,src.password_hash,src.role,src.email,src.first_name,src.last_name);
            """),
            {"u": username, "ph": pw_hash, "r": role, "e": email, "fn": first_name, "ln": last_name},
        )
    logger.info("User '%s' created/updated (role=%s)", username, role)
