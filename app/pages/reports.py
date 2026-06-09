"""Reports page (Group 2) — read-only analytics with date/order inputs and Excel export."""
from __future__ import annotations

import logging

import pandas as pd
import streamlit as st

from app.config.table_config import REPORT_CONFIG
from app.services.production import run_report, to_excel_bytes

logger = logging.getLogger(__name__)


@st.cache_data(ttl=300, show_spinner=False)
def _cached_report(query_name: str, params_key: str, **params: object) -> pd.DataFrame:
    return run_report(query_name, params)


def render(report_name: str) -> None:
    rcfg = REPORT_CONFIG.get(report_name)
    if not rcfg:
        st.warning(f"Report non trovato: '{report_name}'")
        return

    st.markdown(f"### {report_name}")
    st.divider()

    params: dict[str, object] = {}
    run = False

    if "date_range" in rcfg["inputs"]:
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            raw_from = st.date_input("Da", value=pd.Timestamp.today(), key=f"df_{report_name}")
        with col2:
            raw_to = st.date_input("A",  value=pd.Timestamp.today(), key=f"dt_{report_name}")
        with col3:
            st.markdown("<br>", unsafe_allow_html=True)
            run = st.button("Esegui", use_container_width=True, key=f"run_{report_name}")

        if raw_from > raw_to:
            st.error("La data 'Da' non può essere successiva alla data 'A'.")
            return

        params["date_from"] = raw_from.strftime("%Y-%m-%d")
        params["date_to"]   = raw_to.strftime("%Y-%m-%d")

    elif "ord_cam" in rcfg["inputs"]:
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            ord_str = st.text_input("Ord. Camfart", key=f"oc_{report_name}")
        with col2:
            chr_str = st.text_input("Chr. Camfart", key=f"cc_{report_name}")
        with col3:
            st.markdown("<br>", unsafe_allow_html=True)
            run = st.button("Esegui", use_container_width=True, key=f"run_{report_name}")

        if not ord_str or not chr_str:
            run = False
        else:
            try:
                params["ord_cam"] = float(ord_str)
            except ValueError:
                st.error("Ord. Camfart deve essere un numero.")
                return
            params["chr_cam"] = chr_str

    else:
        run = True

    if not run:
        return

    params_key = str(sorted(params.items()))
    try:
        with st.spinner("Esecuzione report..."):
            df = _cached_report(rcfg["query"], params_key, **params)
    except Exception as exc:
        logger.error("Report '%s' failed: %s", report_name, exc)
        st.error(f"Errore nel report: {exc}")
        return

    st.dataframe(df, use_container_width=True, height=650)

    row_col, export_col = st.columns([6, 1])
    row_col.caption(f"{len(df)} righe")

    # Excel export (#17)
    with export_col:
        excel_bytes = to_excel_bytes(df)
        st.download_button(
            label="Excel",
            data=excel_bytes,
            file_name=f"{report_name.replace(' ', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
