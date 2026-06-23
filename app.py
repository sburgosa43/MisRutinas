import streamlit as st
import importlib

st.set_page_config(page_title="Mis Rutinas", page_icon="🏋️",
                   layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
[data-testid="stSidebar"] { background-color: #0f172a; }
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stRadio p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] small { color: #e2e8f0 !important; }
[data-testid="stSidebar"] hr { border-color: #334155; }
div[data-testid="stMetric"] {
    background-color: #f8fafc; border: 1px solid #e2e8f0;
    border-radius: 10px; padding: 14px 18px;
}
</style>
""", unsafe_allow_html=True)

# ── Importar estado con diagnóstico ───────────────────────────────────────────
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
    except ImportError as e:
        st.error(f"❌ ImportError en modules.login: {type(e).__name__}: {e}")
        st.exception(e)
    except Exception as e:
        st.error(f"❌ Error en login: {type(e).__name__}: {e}")
        st.exception(e)
    st.stop()

# ── Cargar perfil ─────────────────────────────────────────────────────────────
estado.cargar_perfil()
genero = estado.get("genero", "Mujer")
nombre = st.session_state.get("nombre_usuario", "Mis Rutinas")

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
    st.markdown(f"### 🏋️ {nombre}")
    st.caption("Fitness & Bienestar Personal")
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
