import streamlit as st
import importlib
import utils.estado as estado

st.set_page_config(page_title="Mis Rutinas", page_icon="🏋️", layout="wide", initial_sidebar_state="expanded")

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

# Cargar perfil del usuario UNA vez al inicio de la sesión
estado.cargar_perfil()

PAGES = [
    ("🏠 Dashboard",        "modules.dashboard"),
    ("🧬 Evaluación",       "modules.evaluacion"),
    ("📊 Mis Medidas",      "modules.medidas"),
    ("📈 Progreso",         "modules.progreso"),
    ("🌙 Ciclo Menstrual",  "modules.ciclo"),
    ("⚡ Calculadoras",     "modules.calculadoras"),
    ("🏋️ Rutinas",         "modules.rutinas"),
    ("⚙️ Configuración",   "modules.configuracion"),
    ("🔧 Diagnóstico",      "modules.diagnostico"),
]

with st.sidebar:
    nombre = estado.get("nombre_usuario", "Mis Rutinas")
    st.markdown(f"### 🏋️ {nombre}")
    st.caption("Fitness & Bienestar Personal")
    st.divider()
    selection = st.radio("nav", [p[0] for p in PAGES], label_visibility="collapsed")
    st.divider()
    st.caption("v1.3")

module_name = next(m for name, m in PAGES if name == selection)
try:
    module = importlib.import_module(module_name)
    module.mostrar()
except Exception as e:
    st.error(f"Error cargando módulo: {e}")
    st.exception(e)
