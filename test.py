import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

load_dotenv()

# ── MSSQL engine (same as your working original) ──────────────────────────────
def get_engine():
    user = quote_plus(os.getenv("DB_USER", ""))
    pwd  = quote_plus(os.getenv("DB_PASS", ""))
    host = os.getenv("DB_HOST")
    name = os.getenv("DB_NAME")
    drv  = os.getenv("DB_DRIVER", "ODBC+Driver+17+for+SQL+Server")
    return create_engine(
        f"mssql+pyodbc://{user}:{pwd}@{host}/{name}"
        f"?driver={drv}&TrustServerCertificate=yes",
        fast_executemany=True
    )

engine = get_engine()

# ── First: check what schema the user actually owns ───────────────────────────
with engine.connect() as conn:
    row = conn.execute(text("SELECT SCHEMA_NAME()")).fetchone()
    print(f"Your default schema is: {row[0]}")

# ── Rename table and columns ──────────────────────────────────────────────────
renames = [
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
with engine.begin() as conn:
    for old, new in renames:
        conn.execute(text(f"EXEC sp_rename 'dbo.Stamperia.{old}', '{new}', 'COLUMN'"))
        print(f"   {old}  →  {new}")

    conn.execute(text("ALTER TABLE [Stamperia] ADD [Note] NVARCHAR(500) NULL"))
    print("✅ Column 'Note' added")

print("\nDone. Preview:")
df = pd.read_sql(text("SELECT TOP 5 * FROM [Stamperia]"), engine)
print(df.to_string(index=False))