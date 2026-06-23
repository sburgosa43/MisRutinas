import streamlit as st
import importlib
import sys

st.set_page_config(page_title="Mis Rutinas", page_icon="🏋️",
                   layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
.stApp { background-color: #0e1009; }
[data-testid="stSidebar"] { background-color: #080a05 !important; border-right: 2px solid rgba(196,228,56,0.25) !important; }
[data-testid="stSidebar"] * { color: #c8d4a0 !important; }
[data-testid="stSidebar"] h3 { color: #c4e438 !important; text-transform: uppercase !important; letter-spacing: 3px !important; font-size: 15px !important; }
[data-testid="stSidebar"] hr { border-color: rgba(196,228,56,0.2) !important; }
[data-testid="stSidebar"] small { color: #5a6240 !important; }
[data-testid="stSidebar"] [aria-checked="true"] + div p { color: #c4e438 !important; font-weight: 700 !important; }
[data-testid="stSidebar"] button { background-color: transparent !important; color: #5a6240 !important; border: 1px solid rgba(196,228,56,0.2) !important; font-size: 12px !important; }
[data-testid="stSidebar"] button:hover { color: #c4e438 !important; border-color: rgba(196,228,56,0.5) !important; }
h1 { text-transform: uppercase !important; letter-spacing: 2px !important; color: #f0f0f0 !important; font-weight: 700 !important; }
h2, h3 { color: #e8f0c0 !important; }
div[data-testid="stMetric"] { background-color: #141708 !important; border: 1px solid rgba(196,228,56,0.35) !important; border-radius: 8px !important; padding: 14px 18px !important; }
div[data-testid="stMetric"] label { color: #7a8a50 !important; text-transform: uppercase !important; font-size: 11px !important; letter-spacing: 1px !important; }
div[data-testid="stMetric"] [data-testid="stMetricValue"] { color: #c4e438 !important; font-weight: 700 !important; }
button[kind="primary"] { background-color: #c4e438 !important; color: #0e1009 !important; font-weight: 800 !important; text-transform: uppercase !important; letter-spacing: 1px !important; border: none !important; border-radius: 4px !important; }
button[kind="secondary"] { background-color: transparent !important; color: #c4e438 !important; border: 1px solid rgba(196,228,56,0.5) !important; font-weight: 600 !important; text-transform: uppercase !important; letter-spacing: 1px !important; }
.stTextInput input, .stNumberInput input, .stTextArea textarea { background-color: #141708 !important; border: 1px solid rgba(196,228,56,0.2) !important; color: #f0f0f0 !important; border-radius: 4px !important; }
.stTextInput input:focus, .stNumberInput input:focus { border-color: #c4e438 !important; }
.streamlit-expanderHeader { background-color: #141708 !important; border: 1px solid rgba(196,228,56,0.15) !important; border-radius: 6px !important; color: #c8d4a0 !important; font-weight: 600 !important; text-transform: uppercase !important; font-size: 12px !important; letter-spacing: 1px !important; }
.streamlit-expanderContent { background-color: #0f1208 !important; border: 1px solid rgba(196,228,56,0.1) !important; border-top: none !important; }
.stTabs [data-baseweb="tab-list"] { background-color: transparent !important; border-bottom: 2px solid rgba(196,228,56,0.2) !important; gap: 6px !important; padding: 0 !important; }
.stTabs [data-baseweb="tab"] { color: #7a8a50 !important; font-weight: 600 !important; text-transform: uppercase !important; letter-spacing: 0.8px !important; font-size: 11px !important; padding: 10px 18px !important; border: 1px solid rgba(196,228,56,0.15) !important; border-bottom: none !important; border-radius: 6px 6px 0 0 !important; background-color: #0f1208 !important; white-space: nowrap !important; }
.stTabs [data-baseweb="tab"]:hover { color: #c4e438 !important; border-color: rgba(196,228,56,0.4) !important; background-color: #141708 !important; }
.stTabs [aria-selected="true"] { background-color: #141708 !important; color: #c4e438 !important; border-color: #c4e438 !important; }
.stTabs [data-baseweb="tab-panel"] { background-color: #141708 !important; border: 1px solid rgba(196,228,56,0.15) !important; border-top: none !important; border-radius: 0 0 8px 8px !important; padding: 20px 16px !important; }
hr { border-color: rgba(196,228,56,0.15) !important; }
[data-baseweb="select"] > div { background-color: #141708 !important; border-color: rgba(196,228,56,0.2) !important; }
</style>
""", unsafe_allow_html=True)

# ── Estado ────────────────────────────────────────────────────────────────────
try:
    import utils.estado as estado
except Exception as e:
    st.error(f"❌ Error cargando estado: {e}")
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

# ── Perfil ────────────────────────────────────────────────────────────────────
estado.cargar_perfil()
genero = estado.get("genero", "Mujer")
nombre = st.session_state.get("nombre_usuario", "MIS RUTINAS")

# ── Páginas ───────────────────────────────────────────────────────────────────
PAGES = [
    ("📊 Mis Medidas",    "modules.medidas"),
    ("🏠 Dashboard",      "modules.dashboard"),
    ("🧬 Evaluación",     "modules.evaluacion"),
    ("⚡ Calculadoras",   "modules.calculadoras"),
    ("🏋️ Rutinas",       "modules.rutinas"),
    ("📈 Progreso",       "modules.progreso"),
]
if genero == "Mujer":
    PAGES.append(("🌙 Ciclo Menstrual", "modules.ciclo"))
PAGES += [
    ("⚙️ Configuración", "modules.configuracion"),
    ("🔧 Diagnóstico",    "modules.diagnostico"),
]

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"### 🏋️ {nombre.upper()}")
    st.caption("fitness & bienestar personal")
    st.divider()
    selection = st.radio("nav", [p[0] for p in PAGES], label_visibility="collapsed")
    st.divider()
    if st.button("🚪 Cerrar sesión", use_container_width=True):
        st.session_state.clear()
        st.rerun()
    st.caption("v1.8")

# ── Cargar módulo ─────────────────────────────────────────────────────────────
try:
    module_name = next((m for name, m in PAGES if name == selection), None)
    if not module_name:
        st.error(f"Módulo no encontrado para: {selection}")
        st.stop()
    # Limpiar caché para evitar módulos desactualizados
    for key in list(sys.modules.keys()):
        if key.startswith("modules."):
            del sys.modules[key]
    module = importlib.import_module(module_name)
    module.mostrar()
except Exception as e:
    st.error(f"Error cargando módulo: {e}")
    st.exception(e)
