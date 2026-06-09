"""Input validation for editable table rows before saving."""
from __future__ import annotations

import pandas as pd

# Columns that represent time in hours — must be numeric >= 0
_TIME_COLS = {
    "Temp_pesa", "Temp_misc", "Temp_press", "Temp_assist_press",
    "Temp_spian", "Temp_lapid", "Temp_ffi", "Temp_rett", "Temp_prof", "Temp_resin",
    "Temp_sabb", "Temp_pul_sof", "Temp_bilanc", "Temp_velo", "Temp_marca",
    "Temp_flang", "Temp_imball", "Temp_chius",
}

# Columns that represent piece counts — must be integer >= 0
_PIECE_COLS = {"Pz_inforna"}

# Reasonable upper bounds
_MAX_HOURS  = 999.0
_MAX_PIECES = 99_999


def validate_flagged_rows(
    flagged: pd.DataFrame,
    editable_cols: list[str],
    pk_col: str,
) -> list[str]:
    """Return a list of human-readable error messages; empty list means valid."""
    errors: list[str] = []

    for _, row in flagged.iterrows():
        pk = row[pk_col]
        label = f"Riga {pk}"

        for col in editable_cols:
            if col == "Flag":
                continue

            val = row.get(col)

            # Treat NaN as None (allowed — means "not filled in yet")
            try:
                if pd.isna(val):
                    val = None
            except (TypeError, ValueError):
                pass

            if col in _TIME_COLS and val is not None:
                try:
                    fval = float(val)
                except (TypeError, ValueError):
                    errors.append(f"{label} — {col}: deve essere un numero (trovato: {val!r})")
                    continue
                if fval < 0:
                    errors.append(f"{label} — {col}: non può essere negativo ({fval})")
                elif fval > _MAX_HOURS:
                    errors.append(f"{label} — {col}: valore irrealistico ({fval} h > {_MAX_HOURS})")

            elif col in _PIECE_COLS and val is not None:
                try:
                    ival = int(val)
                except (TypeError, ValueError):
                    errors.append(f"{label} — {col}: deve essere un numero intero (trovato: {val!r})")
                    continue
                if ival < 0:
                    errors.append(f"{label} — {col}: non può essere negativo ({ival})")
                elif ival > _MAX_PIECES:
                    errors.append(f"{label} — {col}: valore troppo alto ({ival} > {_MAX_PIECES})")

    return errors
