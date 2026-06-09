"""Editable table page (Group 1) — Stamperia, Forno_cottura, Tornitura, Collaudo."""
from __future__ import annotations

import logging
import pathlib
import sys

_ROOT = pathlib.Path(__file__).parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st

from app.config.table_config import TABLE_CONFIG
from app.db.connection import load_table_data
from app.services.production import refresh_table, save_flagged_rows
from app.services.validation import validate_flagged_rows

logger = logging.getLogger(__name__)

_PAGE_SIZE_OPTIONS = [50, 100, 200, 500]


def render(table_name: str, username: str) -> None:
    cfg = TABLE_CONFIG.get(table_name)
    if not cfg:
        st.warning(f"Nessuna configurazione per '{table_name}'")
        return

    cache_key   = f"df_{table_name}"
    reload_key  = f"reload_{table_name}"

    if cache_key not in st.session_state or st.session_state.get(reload_key):
        with st.spinner("Caricamento dati..."):
            try:
                st.session_state[cache_key] = load_table_data(table_name)
            except Exception as exc:
                logger.error("load_table_data '%s': %s", table_name, exc)
                st.error(f"Impossibile caricare la tabella '{table_name}': {exc}")
                return
        st.session_state[reload_key] = False

    df = st.session_state[cache_key]

    # ── Top bar ───────────────────────────────────────────────────────────────
    col_title, col_page, col_refresh, col_save = st.columns([4, 2, 1, 1])
    with col_title:
        st.markdown(f"### {table_name.replace('_', ' ')}")
    with col_page:
        page_size = st.selectbox(
            "Righe per pagina",
            _PAGE_SIZE_OPTIONS,
            index=1,
            label_visibility="collapsed",
            key=f"page_size_{table_name}",
        )
    with col_refresh:
        if st.button("Refresh", use_container_width=True, key=f"btn_refresh_{table_name}"):
            msg = refresh_table(table_name)
            if msg == "ok":
                st.session_state[reload_key] = True
                st.rerun()
            else:
                st.error(msg)
    with col_save:
        save_clicked = st.button("Salva", use_container_width=True, key=f"btn_save_{table_name}")

    # ── Pagination (#18) ─────────────────────────────────────────────────────
    total_rows = len(df)
    total_pages = max(1, (total_rows + page_size - 1) // page_size)
    page_key = f"page_{table_name}"
    if page_key not in st.session_state:
        st.session_state[page_key] = 1

    page_num = st.session_state[page_key]
    start    = (page_num - 1) * page_size
    page_df  = df.iloc[start : start + page_size]

    # ── Editable table ────────────────────────────────────────────────────────
    edited_df = st.data_editor(
        page_df,
        column_config={"Flag": st.column_config.CheckboxColumn("Flag", default=False)},
        use_container_width=True,
        height=680,
        num_rows="fixed",
        disabled=cfg["disabled_cols"],
        key=f"editor_{table_name}_p{page_num}",
    )

    # Pagination controls
    p_col1, p_col2, p_col3 = st.columns([1, 4, 1])
    with p_col1:
        if st.button("← Prec.", disabled=page_num <= 1, key=f"prev_{table_name}"):
            st.session_state[page_key] -= 1
            st.rerun()
    with p_col2:
        st.caption(f"Pagina {page_num} / {total_pages}  |  {total_rows} righe totali")
    with p_col3:
        if st.button("Succ. →", disabled=page_num >= total_pages, key=f"next_{table_name}"):
            st.session_state[page_key] += 1
            st.rerun()

    # ── Save with validation + diff preview ──────────────────────────────────
    if save_clicked:
        flagged = edited_df[edited_df["Flag"] == True]
        if flagged.empty:
            st.warning("Nessuna riga contrassegnata con Flag.")
            return

        # Validate before showing confirm
        errors = validate_flagged_rows(flagged, cfg["editable_cols"], cfg["pk"])
        if errors:
            st.error("Correggere i seguenti errori prima di salvare:")
            for e in errors:
                st.markdown(f"- {e}")
            return

        # Show preview of what will be saved
        with st.expander(f"Anteprima modifiche ({len(flagged)} righe)", expanded=True):
            st.dataframe(flagged[cfg["editable_cols"]], use_container_width=True)

        confirm_key = f"confirm_save_{table_name}"
        if st.button("Conferma salvataggio", type="primary", key=confirm_key):
            try:
                count = save_flagged_rows(table_name, edited_df, username)
                st.success(f"Salvato e confermato ({count} righe)")
                st.session_state[reload_key] = True
                st.rerun()
            except Exception as exc:
                logger.error("save_flagged_rows '%s': %s", table_name, exc)
                st.error(f"Salvataggio fallito: {exc}")
