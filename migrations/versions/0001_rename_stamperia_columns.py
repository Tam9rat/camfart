"""Rename legacy Stamperia columns and add Note column.

Supersedes the one-shot test.py script with a proper versioned migration.

Revision ID: 0001
Revises:
Create Date: 2026-06-09
"""
from __future__ import annotations

from alembic import op
from sqlalchemy import text

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

_RENAMES = [
    ("id_commessa",                  "Id"),
    ("ord_camfart",                  "Ord_cam"),
    ("chr_camfart",                  "Chr_cam"),
    ("num_scheda",                   "Num_scheda"),
    ("specif",                       "Specif"),
    ("dimensioni",                   "Dimensioni"),
    ("pz_richiesti",                 "Pz_richi"),
    ("pz_stamp",                     "Pz_stamp"),
    ("data_stamp",                   "Data_stamp"),
    ("tempo_pesat",                  "Temp_pesa"),
    ("tempo_miscel",                 "Temp_misc"),
    ("tempo_pressat",                "Temp_press"),
    ("tempo_assistenza_pressat",     "Temp_assist_press"),
    ("tempo_totale",                 "Temp_tot"),
    ("matricola_operatore_pesatura", "Mat_op_pesa"),
    ("matricola_operatore_miscelat", "Mat_op_misc"),
    ("matricola_operatore_pressat",  "Mat_op_press"),
    ("flag_convalida",               "Flag"),
    ("data_validazione",             "Data_valid"),
]

_EXISTS_COL = text("""
    SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME='Stamperia' AND COLUMN_NAME=:col
""")


def upgrade() -> None:
    conn = op.get_bind()
    for old, new in _RENAMES:
        if conn.execute(_EXISTS_COL, {"col": old}).fetchone():
            conn.execute(text(f"EXEC sp_rename 'dbo.Stamperia.{old}', '{new}', 'COLUMN'"))
    if not conn.execute(_EXISTS_COL, {"col": "Note"}).fetchone():
        op.execute("ALTER TABLE [Stamperia] ADD [Note] NVARCHAR(500) NULL")


def downgrade() -> None:
    conn = op.get_bind()
    for old, new in _RENAMES:
        if conn.execute(_EXISTS_COL, {"col": new}).fetchone():
            conn.execute(text(f"EXEC sp_rename 'dbo.Stamperia.{new}', '{old}', 'COLUMN'"))
    if conn.execute(_EXISTS_COL, {"col": "Note"}).fetchone():
        op.execute("ALTER TABLE [Stamperia] DROP COLUMN [Note]")
