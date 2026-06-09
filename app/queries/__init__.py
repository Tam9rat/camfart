from __future__ import annotations

import pathlib

_SQL_DIR = pathlib.Path(__file__).parent / "sql"

_BASE_LAVORAZIONI = (_SQL_DIR / "_base_lavorazioni.sql").read_text(encoding="utf-8")
_BASE_SINGOLA     = (_SQL_DIR / "_base_singola.sql").read_text(encoding="utf-8")

_DATE_REPORTS = {
    "report_quadratura",
    "report_pezzi_discordanti",
    "report_infornature_parziali",
    "report_riepilogo_commesse",
}
_SINGOLA_REPORTS = {"report_singola_commessa"}


def load(name: str) -> str:
    """Return the full SQL text for *name*, prepending the correct CTE base when needed."""
    raw = (_SQL_DIR / f"{name}.sql").read_text(encoding="utf-8")
    if name in _DATE_REPORTS:
        return _BASE_LAVORAZIONI + raw
    if name in _SINGOLA_REPORTS:
        return _BASE_SINGOLA + raw
    return raw
