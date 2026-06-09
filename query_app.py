import io
import os
import base64
import pathlib
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import text
import yaml
from yaml.loader import SafeLoader
import streamlit as st
import streamlit_authenticator as stauth
from db import get_engine, execute_query, get_public_tables, load_table_data
from table_config import TABLE_CONFIG, GROUP_TABLES, REPORT_CONFIG
from queries import QUERIES

def get_base64_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

get_public_tables = st.cache_data(ttl=5)(get_public_tables)


st.set_page_config(
    page_title="Camfart",
    page_icon="Logo_Ca.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Auth ──────────────────────────────────────────────────────────────────────
config_path = pathlib.Path(__file__).parent / "config.yaml"
with open(config_path) as f:
    config = yaml.load(f, Loader=SafeLoader)

# Reset logged_in on every fresh load
if "initialized" not in st.session_state:
    for user in config["credentials"]["usernames"].values():
        user["logged_in"] = False
    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    st.session_state["initialized"] = True

authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"]
)

# ── Login Page Design ─────────────────────────────────────────────────────────
if not st.session_state.get("authentication_status"):



    LOGO = pathlib.Path(__file__).parent / "Logo_Camfart.png"
    img_base64 = get_base64_image(LOGO)

    st.markdown(f"""
    <style>
    [data-testid="stSidebar"] {{display: none !important;}}
    [data-testid="collapsedControl"] {{display: none !important;}}
    #MainMenu {{visibility: hidden !important;}}
    header {{visibility: hidden !important;}}
    footer {{visibility: hidden !important;}}
    [data-testid="stToolbar"] {{display: none !important;}}
    .stApp {{
        background-image: url("data:image/png;base64,{img_base64}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    .stApp::before {{
        content: "";
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background: rgba(0, 0, 0, 0.5);
        z-index: 0;
    }}
    .block-container {{
        position: relative;
        z-index: 1;
    }}
    [data-testid="stForm"] {{
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        background: rgba(255, 255, 255, 0.95) !important;
    }}
    .login-header {{
        text-align: center;
        margin-bottom: 1rem;
    }}
    .login-header h1 {{
        font-size: 2rem;
        font-weight: 700;
        color: white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }}
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="login-header">
        <h1>Camfart Database Query</h1>
    </div>
    """, unsafe_allow_html=True)

    try:
        authenticator.login(location="main", fields={
            "Form name": "Login",
            "Username": "Username",
            "Password": "Password",
            "Login": "Accedi"
        })
    except Exception as e:
        st.error(e)

    if st.session_state.get("authentication_status") is False:
        st.error("Username o password errati")
    elif st.session_state.get("authentication_status") is None:
        st.warning("Inserisci username e password")

    st.stop()

# ── CSS (main app) ────────────────────────────────────────────────────────────
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
[data-testid="stToolbar"] {display: none;}
[data-testid="stDeployButton"] {display: none !important;}
[data-testid="collapsedControl"] {display: none !important;}
[data-testid="stSidebarCollapseButton"] {display: none !important;}
button[kind="header"] {display: none !important;}
.st-emotion-cache-zq5wmm {display: none !important;}
.eyeqlp53 {display: none !important;}
section[data-testid="stSidebar"] > div > div > button {display: none !important;}
section[data-testid="stSidebar"] button[aria-label="Close sidebar"] {display: none !important;}
[data-testid="StyledFullScreenButton"] {display: none !important;}
button[title="View fullscreen"] {display: none !important;}
[data-testid="stFullScreenFrame"] > button {display: none !important;}
.block-container {
    padding-top: 1rem;
    padding-left: 1.5rem;
    padding-right: 1.5rem;
    padding-bottom: 1rem;
}
section[data-testid="stSidebar"] {
    width: 220px !important;
    min-width: 220px !important;
    max-width: 220px !important;
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
try:
    tables = get_public_tables()
except Exception as e:
    st.error(f"Errore connessione DB: {e}")
    tables = []
# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    #LOGO = pathlib.Path(__file__).parent / "Logo_Camfart.png"
    #if LOGO.exists():
        #st.image(str(LOGO), width=120)
    #st.divider()

    def set_active_group(group_name):
        st.session_state["active_group"] = group_name

    for group_name, group_tables in GROUP_TABLES.items():
        st.markdown(f"**{group_name}**")
        available = group_tables if group_name == "Group 2" else [t for t in group_tables if t in tables]
        st.selectbox(
            group_name,
            ["-- Select --"] + available,
            key=f"sel_{group_name}",
            label_visibility="collapsed",
            on_change=set_active_group,
            args=(group_name,)
        )

    st.divider()
    authenticator.logout("Logout", location="sidebar", use_container_width=True)

# ── Determine selected table ──────────────────────────────────────────────────
selected_table = None
active_group = st.session_state.get("active_group")

if active_group:
    val = st.session_state.get(f"sel_{active_group}")
    if val and val != "-- Select --":
        selected_table = val

# Fallback: if active group was reset to default, check others
if not selected_table:
    for group_name in GROUP_TABLES:
        val = st.session_state.get(f"sel_{group_name}")
        if val and val != "-- Select --":
            selected_table = val
            break
if not selected_table:
    LOGO = pathlib.Path(__file__).parent / "Logo_Camfart.png"
    img_base64 = get_base64_image(LOGO)

    st.markdown(f"""
    <style>
    .block-container {{
        display: flex;
        justify-content: center;
        align-items: center;
        height: 80vh;
    }}

    .logo-container {{
        text-align: center;
        animation: fadeIn 1.2s ease-in-out;
    }}

    .logo-container img {{
        width: 1500px;
        opacity: 1.0;
        filter: drop-shadow(0 8px 24px rgba(0, 0, 0, 0.25));
        transition: transform 0.4s ease, filter 0.4s ease;
    }}

    .logo-container img:hover {{
        transform: scale(1.05);
        filter: drop-shadow(0 12px 32px rgba(0, 0, 0, 0.4));
    }}

    .logo-title {{
        margin-top: 1.5rem;
        font-size: 1.2rem;
        color: #555;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        font-family: 'Segoe UI', sans-serif;
    }}

    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(20px); }}
        to   {{ opacity: 1; transform: translateY(0); }}
    }}
    </style>

    <div class="logo-container">
        <img src="data:image/png;base64,{img_base64}">
        <div class="logo-title">Seleziona una tabella dal menu</div>
    </div>
    """, unsafe_allow_html=True)

    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# GROUP 2 — Reports
# ══════════════════════════════════════════════════════════════════════════════
if selected_table in REPORT_CONFIG:
    rcfg = REPORT_CONFIG[selected_table]

    st.markdown(f"###  {selected_table}")
    st.divider()

    params = {}
    run = False

    if "date_range" in rcfg["inputs"]:
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            date_from = st.date_input("Da", value=pd.Timestamp.today())
        with col2:
            date_to = st.date_input("A", value=pd.Timestamp.today())
        with col3:
            st.markdown("<br>", unsafe_allow_html=True)
            run = st.button(" Esegui", use_container_width=True)
        params["date_from"] = date_from
        params["date_to"]   = date_to

    elif "ord_cam" in rcfg["inputs"]:
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            ord_cam_str = st.text_input("Ord. Camfart")
            params["ord_cam"] = float(ord_cam_str) if ord_cam_str else None
        with col2:
            params["chr_cam"] = st.text_input("Chr. Camfart")
        with col3:
            st.markdown("<br>", unsafe_allow_html=True)
            run = st.button(" Esegui", use_container_width=True)
        if not ord_cam_str or not params["chr_cam"]:
            run = False

    else:
        # No inputs — run immediately
        run = True

    # ── Execute & display ─────────────────────────────────────────────────────
# ── Execute & display ─────────────────────────────────────────────────────
    if run:
        try:
            with get_engine().connect() as conn:
                query = QUERIES[rcfg["query"]]

                if "date_from" in params:
                    date_from_str = params["date_from"].strftime("%Y-%m-%d")
                    date_to_str = params["date_to"].strftime("%Y-%m-%d")
                    query = query.replace("@date_from", f"'{date_from_str}'")
                    query = query.replace("@date_to", f"'{date_to_str}'")

                if "ord_cam" in params:
                    query = query.replace("@ord_cam", f"'{params['ord_cam']}'")
                    query = query.replace("@chr_cam", f"'{params['chr_cam']}'")

                df = pd.read_sql(text(query), conn)

            st.dataframe(df, use_container_width=True, height=680)

            col_count, col_export = st.columns([6, 1])
            col_count.caption(f"{len(df)} righe")

        except Exception as e:
            st.error(f"Errore nel report: {e}")

    st.stop()  # ← CRITICAL: stops GROUP 1 code from running for reports

# ══════════════════════════════════════════════════════════════════════════════
# GROUP 1 — Editable tables
# ══════════════════════════════════════════════════════════════════════════════
cfg = TABLE_CONFIG.get(selected_table)

if not cfg:
    st.warning(f"Nessuna configurazione per '{selected_table}'")
    st.stop()

try:
    cache_key = f"df_{selected_table}"

    if cache_key not in st.session_state or st.session_state.get(f"reload_{selected_table}"):
        with st.spinner("Caricamento dati..."):
            st.session_state[cache_key] = load_table_data(selected_table)
            st.session_state[f"reload_{selected_table}"] = False

    df = st.session_state[cache_key]

    # ── Top bar ───────────────────────────────────────────────────────────────
    col_title, col_refresh, col_salva = st.columns([6, 1, 1])
    with col_title:
        st.markdown(f"### {selected_table.replace('_', ' ')}")
    with col_refresh:
        if st.button("Refresh", use_container_width=True):
            msg = execute_query(QUERIES[cfg["refresh_query"]])
            if msg == "ok":
                st.session_state[f"reload_{selected_table}"] = True
                st.rerun()
            else:
                st.error(msg)
    with col_salva:
        save_clicked = st.button("Salva", use_container_width=True)

    # ── Editable table ────────────────────────────────────────────────────────
    edited_df = st.data_editor(
        df,
        column_config={
            "Flag": st.column_config.CheckboxColumn("Flag", default=False),
        },
        use_container_width=True,
        height=720,
        num_rows="fixed",
        disabled=cfg["disabled_cols"]
    )

    # ── Save ──────────────────────────────────────────────────────────────────
    if save_clicked:
        import pandas as pd

        def clean(val):
            if val is None:
                return None
            if isinstance(val, bool):
                return val
            try:
                if pd.isna(val):
                    return None
            except (TypeError, ValueError):
                pass
            return val

        def clean_flag(val):
            try:
                if pd.isna(val):
                    return False
            except (TypeError, ValueError):
                pass
            return bool(val)

        try:
            with get_engine().begin() as conn:
                flagged = edited_df[edited_df["Flag"] == True]
                for _, row in flagged.iterrows():
                    params = {}
                    for col in cfg["editable_cols"]:
                        val = row[col]
                        if col == "Flag":
                            params[col] = clean_flag(val)
                        else:
                            params[col] = clean(val)
                    params[cfg["pk"]] = int(row[cfg["pk"]])
                    conn.execute(text(cfg["update_sql"]), params)
                conn.execute(text(QUERIES[cfg["confirm_query"]]))
            st.success(f"Salvato e confermato ({len(flagged)} righe)")
            st.session_state[f"reload_{selected_table}"] = True
            st.rerun()
        except Exception as e:
            st.error(f"Salvataggio fallito: {e}")

except Exception as e:
    st.error(f"Impossibile caricare la tabella '{selected_table}': {e}")