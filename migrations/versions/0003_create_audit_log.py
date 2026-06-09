"""Create audit_log table for row-level change tracking.

Revision ID: 0003
Revises: 0002
Create Date: 2026-06-09
"""
from __future__ import annotations
from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        IF NOT EXISTS (
            SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME='audit_log'
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
            CREATE INDEX ix_audit_log_ts       ON [audit_log] ([ts] DESC);
            CREATE INDEX ix_audit_log_table_pk ON [audit_log] ([table_name],[pk_value]);
            CREATE INDEX ix_audit_log_username ON [audit_log] ([username]);
        END
    """)


def downgrade() -> None:
    op.execute("""
        IF EXISTS (
            SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME='audit_log'
        )
        DROP TABLE [audit_log]
    """)
