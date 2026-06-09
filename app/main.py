"""Camfart — main Streamlit entry point."""
from __future__ import annotations

import base64
import logging
import pathlib

import streamlit as st
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth

from app.config.logging_setup import configure_logging
from app.config.table_config import GROUP_TABLES, REPORT_CONFIG, TABLE_CONFIG, ROLE_PERMISSIONS
from app.db.connection import get_public_tables
from app.pages import editable_table, reports

configure_logging()
logger = logging.getLogger(__name__)

_HERE = pathlib.Path(__file__).parent.parent  # project root


def _b64(path: pathlib.Path) -> str:
    return base64.b64encode(path.read_bytes()).decode()


st.set_page_config(
    page_title="Camfart",
    page_icon=str(_HERE / "Logo_Ca.png"),
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Auth ──────────────────────────────────────────────────────────────────────
_config_path = _HERE / "config.yaml"
with open(_config_path) as _f:
    _cfg = yaml.load(_f, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    _cfg["credentials"],
    _cfg["cookie"]["name"],
    _cfg["cookie"]["key"],
    _cfg["cookie"]["expiry_days"],
)

# ── Login page ────────────────────────────────────────────────────────────────
if not st.session_state.get("authentication_status"):
    logo_b64 = _b64(_HERE / "Logo_Camfart.png")

    st.markdown(f"""
    <style>
    [data-testid="stSidebar"] {{display:none!important;}}
    [data-testid="collapsedControl"] {{display:none!important;}}
    #MainMenu {{visibility:hidden!important;}}
    header {{visibility:hidden!important;}}
    footer {{visibility:hidden!important;}}
    [data-testid="stToolbar"] {{display:none!important;}}
    .stApp {{
        background-image: url("data:image/png;base64,{logo_b64}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    .stApp::before {{
        content:"";
        position:fixed;
        top:0;left:0;
        width:100%;height:100%;
        background:rgba(0,0,0,0.55);
        z-index:0;
    }}
    .block-container {{position:relative;z-index:1;}}
    [data-testid="stForm"] {{
        max-width:420px;
        margin:0 auto;
        padding:2.5rem 2rem;
        border-radius:16px;
        box-shadow:0 8px 32px rgba(0,0,0,0.4);
        background:rgba(255,255,255,0.97)!important;
    }}
    .login-header {{text-align:center;margin-bottom:1.5rem;}}
    .login-header h1 {{
        font-size:1.8rem;font-weight:700;
        color:#1a1a2e;letter-spacing:0.05em;
    }}
    .login-header p {{color:#555;font-size:0.9rem;margin-top:0.3rem;}}
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="login-header">
        <h1>Camfart</h1>
        <p>Sistema di gestione produzione</p>
    </div>
    """, unsafe_allow_html=True)

    try:
        authenticator.login(location="main", fields={
            "Form name": "Accesso",
            "Username":  "Username",
            "Password":  "Password",
            "Login":     "Accedi",
        })
    except Exception as exc:
        st.error(str(exc))

    status = st.session_state.get("authentication_status")
    if status is True:
        st.rerun()
    elif status is False:
        st.error("Username o password errati")
    else:
        st.info("Inserisci le tue credenziali per accedere")

    st.stop()

# ── App chrome CSS ────────────────────────────────────────────────────────────
st.markdown("""
<style>
#MainMenu {visibility:hidden;}
header {visibility:hidden;}
footer {visibility:hidden;}
[data-testid="stToolbar"] {display:none;}
[data-testid="stDeployButton"] {display:none!important;}
[data-testid="collapsedControl"] {display:none!important;}
[data-testid="stSidebarCollapseButton"] {display:none!important;}
[data-testid="StyledFullScreenButton"] {display:none!important;}
button[title="View fullscreen"] {display:none!important;}
.block-container {padding:1rem 1.5rem;}
section[data-testid="stSidebar"] {
    width:230px!important;
    min-width:230px!important;
    max-width:230px!important;
}
</style>
""", unsafe_allow_html=True)

# ── Role from config ──────────────────────────────────────────────────────────
username  = st.session_state.get("username", "")
user_role = (
    _cfg.get("credentials", {})
        .get("usernames", {})
        .get(username, {})
        .get("role", "viewer")
)
allowed_tables  = ROLE_PERMISSIONS.get(user_role, {}).get("tables",  [])
allowed_reports = ROLE_PERMISSIONS.get(user_role, {}).get("reports", [])

logger.info("User '%s' (role=%s) active", username, user_role)

# ── Sidebar ───────────────────────────────────────────────────────────────────
try:
    db_tables = get_public_tables()
except Exception as exc:
    logger.error("get_public_tables: %s", exc)
    st.error(f"Errore connessione DB: {exc}")
    db_tables = []

with st.sidebar:
    def _set_group(group: str) -> None:
        st.session_state["active_group"] = group

    if allowed_tables:
        st.markdown("**Tabelle**")
        st.selectbox(
            "Group 1",
            ["-- Seleziona --"] + [t for t in GROUP_TABLES["Group 1"] if t in db_tables and t in allowed_tables],
            key="sel_Group 1",
            label_visibility="collapsed",
            on_change=_set_group,
            args=("Group 1",),
        )

    if allowed_reports:
        st.markdown("**Report**")
        st.selectbox(
            "Group 2",
            ["-- Seleziona --"] + [r for r in GROUP_TABLES["Group 2"] if r in allowed_reports],
            key="sel_Group 2",
            label_visibility="collapsed",
            on_change=_set_group,
            args=("Group 2",),
        )

    st.divider()
    st.caption(f"Utente: **{username}**  |  Ruolo: *{user_role}*")
    authenticator.logout("Logout", location="sidebar", use_container_width=True)

# ── Determine selection ───────────────────────────────────────────────────────
selected = None
active_group = st.session_state.get("active_group")
if active_group:
    val = st.session_state.get(f"sel_{active_group}", "-- Seleziona --")
    if val and val != "-- Seleziona --":
        selected = val

if not selected:
    for g in ["Group 1", "Group 2"]:
        val = st.session_state.get(f"sel_{g}", "-- Seleziona --")
        if val and val != "-- Seleziona --":
            selected = val
            break

# ── Landing ───────────────────────────────────────────────────────────────────
if not selected:
    logo_b64 = _b64(_HERE / "Logo_Camfart.png")
    st.markdown(f"""
    <style>
    .block-container {{display:flex;justify-content:center;align-items:center;height:80vh;}}
    .logo-container {{text-align:center;animation:fadeIn 1.2s ease-in-out;}}
    .logo-container img {{
        width:1200px;opacity:1;
        filter:drop-shadow(0 8px 24px rgba(0,0,0,0.2));
        transition:transform .4s ease,filter .4s ease;
    }}
    .logo-container img:hover {{
        transform:scale(1.04);
        filter:drop-shadow(0 12px 32px rgba(0,0,0,0.35));
    }}
    .logo-subtitle {{
        margin-top:1.2rem;font-size:1rem;color:#777;
        letter-spacing:.18em;text-transform:uppercase;
        font-family:'Segoe UI',sans-serif;
    }}
    @keyframes fadeIn {{
        from {{opacity:0;transform:translateY(16px);}}
        to   {{opacity:1;transform:translateY(0);}}
    }}
    </style>
    <div class="logo-container">
        <img src="data:image/png;base64,{logo_b64}">
        <div class="logo-subtitle">Seleziona una tabella o report dal menu</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Route ─────────────────────────────────────────────────────────────────────
if selected in REPORT_CONFIG:
    if selected not in allowed_reports:
        st.error("Accesso negato a questo report.")
        st.stop()
    reports.render(selected)
elif selected in TABLE_CONFIG:
    if selected not in allowed_tables:
        st.error("Accesso negato a questa tabella.")
        st.stop()
    editable_table.render(selected, username)
else:
    st.warning(f"Selezione non riconosciuta: '{selected}'")
