import streamlit as st
import importlib

st.set_page_config(page_title="Mis Rutinas", page_icon="🏋️",
                   layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
/* ── FONDO GLOBAL ─────────────────────────────────────────── */
.stApp { background-color: #0e1009; }

/* ── SIDEBAR ──────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background-color: #080a05 !important;
    border-right: 2px solid rgba(196,228,56,0.25) !important;
}
[data-testid="stSidebar"] * { color: #c8d4a0 !important; }

/* Nombre en sidebar */
[data-testid="stSidebar"] h3 {
    color: #c4e438 !important;
    text-transform: uppercase !important;
    letter-spacing: 3px !important;
    font-size: 15px !important;
}
[data-testid="stSidebar"] hr { border-color: rgba(196,228,56,0.2) !important; }
[data-testid="stSidebar"] small { color: #5a6240 !important; }

/* Item activo del nav */
[data-testid="stSidebar"] [aria-checked="true"] + div p {
    color: #c4e438 !important;
    font-weight: 700 !important;
}

/* ── TÍTULOS ──────────────────────────────────────────────── */
h1 {
    text-transform: uppercase !important;
    letter-spacing: 2px !important;
    color: #f0f0f0 !important;
    font-weight: 700 !important;
}
h2, h3 { color: #e8f0c0 !important; }

/* ── MÉTRICAS ─────────────────────────────────────────────── */
div[data-testid="stMetric"] {
    background-color: #141708 !important;
    border: 1px solid rgba(196,228,56,0.35) !important;
    border-radius: 8px !important;
    padding: 14px 18px !important;
}
div[data-testid="stMetric"] label {
    color: #7a8a50 !important;
    text-transform: uppercase !important;
    font-size: 11px !important;
    letter-spacing: 1px !important;
}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #c4e438 !important;
    font-weight: 700 !important;
}
div[data-testid="stMetric"] [data-testid="stMetricDelta"] {
    color: #8ab030 !important;
}

/* ── BOTONES ──────────────────────────────────────────────── */
button[kind="primary"] {
    background-color: #c4e438 !important;
    color: #0e1009 !important;
    font-weight: 800 !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    border: none !important;
    border-radius: 4px !important;
}
button[kind="primary"]:hover {
    background-color: #d4f448 !important;
    transform: translateY(-1px);
}
button[kind="secondary"] {
    background-color: transparent !important;
    color: #c4e438 !important;
    border: 1px solid rgba(196,228,56,0.5) !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
}

/* ── INPUTS ───────────────────────────────────────────────── */
.stTextInput input, .stNumberInput input,
.stTextArea textarea, .stSelectbox select {
    background-color: #141708 !important;
    border: 1px solid rgba(196,228,56,0.2) !important;
    color: #f0f0f0 !important;
    border-radius: 4px !important;
}
.stTextInput input:focus, .stNumberInput input:focus {
    border-color: #c4e438 !important;
    box-shadow: 0 0 0 1px rgba(196,228,56,0.3) !important;
}

/* ── EXPANDERS ────────────────────────────────────────────── */
.streamlit-expanderHeader {
    background-color: #141708 !important;
    border: 1px solid rgba(196,228,56,0.15) !important;
    border-radius: 6px !important;
    color: #c8d4a0 !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    font-size: 12px !important;
    letter-spacing: 1px !important;
}
.streamlit-expanderContent {
    background-color: #0f1208 !important;
    border: 1px solid rgba(196,228,56,0.1) !important;
    border-top: none !important;
}

/* ── TABS ─────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background-color: #141708 !important;
    border-radius: 6px !important;
    padding: 4px !important;
    gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    color: #7a8a50 !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    font-size: 12px !important;
}
.stTabs [aria-selected="true"] {
    background-color: #c4e438 !important;
    color: #0e1009 !important;
    border-radius: 4px !important;
}

/* ── DATAFRAME ────────────────────────────────────────────── */
.stDataFrame { border: 1px solid rgba(196,228,56,0.15) !important; }
.stDataFrame thead tr th {
    background-color: #1a1e0a !important;
    color: #c4e438 !important;
    text-transform: uppercase !important;
    font-size: 11px !important;
    letter-spacing: 1px !important;
}
.stDataFrame tbody tr:hover { background-color: #1a1e0a !important; }

/* ── DIVIDER ──────────────────────────────────────────────── */
hr { border-color: rgba(196,228,56,0.15) !important; }

/* ── ALERTS / INFO ────────────────────────────────────────── */
.stAlert { border-radius: 4px !important; }
div[data-baseweb="notification"] {
    background-color: #1a1e0a !important;
    border-left: 3px solid #c4e438 !important;
}

/* ── SELECTBOX ────────────────────────────────────────────── */
[data-baseweb="select"] > div {
    background-color: #141708 !important;
    border-color: rgba(196,228,56,0.2) !important;
}

/* ── SIDEBAR BOTÓN CERRAR SESIÓN ──────────────────────────── */
[data-testid="stSidebar"] button {
    background-color: transparent !important;
    color: #5a6240 !important;
    border: 1px solid rgba(196,228,56,0.2) !important;
    font-size: 12px !important;
}
[data-testid="stSidebar"] button:hover {
    color: #c4e438 !important;
    border-color: rgba(196,228,56,0.5) !important;
}
</style>
""", unsafe_allow_html=True)

# ── Importar estado ───────────────────────────────────────────────────────────
try:
    import utils.estado as estado
except Exception as e:
    st.error(f"❌ Error importando utils.estado: {type(e).__name__}: {e}")
    st.stop()

# ── Autenticación ─────────────────────────────────────────────────────────────
autenticado = st.session_state.get("autenticado", False)
user_id     = st.session_state.get("user_id", "")

if not autenticado or not user_id:
    if autenticado and not user_id:
        st.session_state.clear()
    try:
        from modules.login import mostrar_login
        mostrar_login()
    except Exception as e:
        st.error(f"❌ Error en login: {type(e).__name__}: {e}")
        st.exception(e)
    st.stop()

# ── Cargar perfil ─────────────────────────────────────────────────────────────
estado.cargar_perfil()
genero = estado.get("genero", "Mujer")
nombre = st.session_state.get("nombre_usuario", "MIS RUTINAS")

PAGES = [
    ("📊 Mis Medidas",      "modules.medidas"),
    ("🏠 Dashboard",        "modules.dashboard"),
    ("🧬 Evaluación",       "modules.evaluacion"),
    ("⚡ Calculadoras",     "modules.calculadoras"),
    ("🏋️ Rutinas",         "modules.rutinas"),
    ("📈 Progreso",         "modules.progreso"),
]
if genero == "Mujer":
    PAGES.append(("🌙 Ciclo Menstrual", "modules.ciclo"))
PAGES += [
    ("⚙️ Configuración",   "modules.configuracion"),
    ("🔧 Diagnóstico",      "modules.diagnostico"),
]

with st.sidebar:
    st.markdown(f"### 🏋️ {nombre.upper()}")
    st.caption("fitness & bienestar personal")
    st.divider()
    selection = st.radio("nav", [p[0] for p in PAGES], label_visibility="collapsed")
    st.divider()
    if st.button("🚪 Cerrar sesión", use_container_width=True):
        st.session_state.clear()
        st.rerun()
    st.caption("v1.7")

module_name = next(m for name, m in PAGES if name == selection)
try:
    module = importlib.import_module(module_name)
    module.mostrar()
except Exception as e:
    st.error(f"Error cargando módulo: {e}")
    st.exception(e)
