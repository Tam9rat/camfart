"""Create app_users table for DB-backed authentication.

Revision ID: 0002
Revises: 0001
Create Date: 2026-06-09
"""
from __future__ import annotations
import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        IF NOT EXISTS (
            SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME='app_users'
        )
        BEGIN
            CREATE TABLE [app_users] (
                [username]      NVARCHAR(64)  NOT NULL PRIMARY KEY,
                [password_hash] NVARCHAR(256) NOT NULL,
                [role]          NVARCHAR(32)  NOT NULL DEFAULT 'viewer',
                [email]         NVARCHAR(128) NULL,
                [first_name]    NVARCHAR(64)  NULL,
                [last_name]     NVARCHAR(64)  NULL,
                [is_active]     BIT           NOT NULL DEFAULT 1,
                [created_at]    DATETIME2     NOT NULL DEFAULT SYSDATETIME(),
                [last_login]    DATETIME2     NULL
            )
        END
    """)


def downgrade() -> None:
    op.execute("""
        IF EXISTS (
            SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME='app_users'
        )
        DROP TABLE [app_users]
    """)
