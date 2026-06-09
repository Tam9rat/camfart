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

_PAGE_SIZE_OPTIONS = [25, 50, 100, 200]


def render(table_name: str, username: str) -> None:
    cfg = TABLE_CONFIG.get(table_name)
    if not cfg:
        st.warning(f"Nessuna configurazione per '{table_name}'")
        return

    cache_key  = f"df_{table_name}"
    reload_key = f"reload_{table_name}"

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
    col_title, col_search, col_page, col_refresh, col_save = st.columns([3, 3, 2, 1, 1])
    with col_title:
        st.markdown(f"### {table_name.replace('_', ' ')}")
    with col_search:
        search = st.text_input(
            "Cerca",
            placeholder="Cerca in tutte le colonne...",
            label_visibility="collapsed",
            key=f"search_{table_name}",
        )
    with col_page:
        page_size = st.selectbox(
            "Righe per pagina",
            _PAGE_SIZE_OPTIONS,
            index=0,
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

    # ── Search filter across full dataset ─────────────────────────────────────
    search_cache_key = f"search_result_{table_name}"
    last_search_key  = f"last_search_{table_name}"

    if search:
        if st.session_state.get(last_search_key) != search:
            mask = df.astype(str).apply(
                lambda col: col.str.contains(search, case=False, na=False)
            ).any(axis=1)
            st.session_state[search_cache_key] = df[mask]
            st.session_state[last_search_key]  = search
            st.session_state[f"page_{table_name}"] = 1
        filtered_df = st.session_state[search_cache_key]
    else:
        st.session_state.pop(search_cache_key, None)
        st.session_state.pop(last_search_key, None)
        filtered_df = df

    # ── Pagination ─────────────────────────────────────────────────────────────
    total_rows  = len(filtered_df)
    total_pages = max(1, (total_rows + page_size - 1) // page_size)
    page_key    = f"page_{table_name}"
    if page_key not in st.session_state:
        st.session_state[page_key] = 1

    page_num = min(st.session_state[page_key], total_pages)
    st.session_state[page_key] = page_num
    start   = (page_num - 1) * page_size
    page_df = filtered_df.iloc[start : start + page_size].copy()

    # ── Editable table ─────────────────────────────────────────────────────────
    edited_df = st.data_editor(
        page_df,
        column_config={"Flag": st.column_config.CheckboxColumn("Flag", default=False)},
        use_container_width=True,
        height=680,
        num_rows="fixed",
        disabled=cfg["disabled_cols"],
        key=f"editor_{table_name}_p{page_num}_{search}",
    )

    # Write edits back into the full cached df so they survive page navigation
    pk_col = cfg["pk"]
    for _, row in edited_df.iterrows():
        idx = st.session_state[cache_key][st.session_state[cache_key][pk_col] == row[pk_col]].index
        if not idx.empty:
            for col in cfg["editable_cols"]:
                st.session_state[cache_key].at[idx[0], col] = row[col]

    # Pagination controls
    p_col1, p_col2, p_col3 = st.columns([2, 1, 2])
    with p_col1:
        st.markdown(f"<div style='text-align:right;padding-top:8px;color:#666;font-size:0.85rem;'>Pagina</div>", unsafe_allow_html=True)
    with p_col2:
        jump = st.number_input(
            "p", min_value=1, max_value=total_pages,
            value=page_num, step=1,
            label_visibility="collapsed",
            key=f"jump_{table_name}",
        )
        if jump != page_num:
            st.session_state[page_key] = int(jump)
            st.rerun()
    with p_col3:
        st.markdown(f"<div style='padding-top:8px;color:#666;font-size:0.85rem;'>di {total_pages} &nbsp;|&nbsp; {total_rows} righe</div>", unsafe_allow_html=True)

    # ── Save directly — no confirm step ───────────────────────────────────────
    if save_clicked:
        full_df = st.session_state[cache_key]
        flagged = full_df[full_df["Flag"] == True]
        if flagged.empty:
            st.warning("Nessuna riga contrassegnata con Flag.")
            return

        errors = validate_flagged_rows(flagged, cfg["editable_cols"], pk_col)
        if errors:
            st.error("Correggere i seguenti errori prima di salvare:")
            for e in errors:
                st.markdown(f"- {e}")
            return

        try:
            count = save_flagged_rows(table_name, full_df, username)
            st.success(f"Salvato ({count} righe)")
            st.session_state[reload_key] = True
            st.rerun()
        except Exception as exc:
            logger.error("save_flagged_rows '%s': %s", table_name, exc)
            st.error(f"Salvataggio fallito: {exc}")
