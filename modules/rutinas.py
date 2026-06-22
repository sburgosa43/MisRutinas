import streamlit as st
import utils.estado as estado

def mostrar():
    estado.cargar_perfil()
    st.title("🏋️ Rutinas de Ejercicio")
    obj = estado.get("eval_objetivo", "")
    nivel = estado.get("eval_nivel", "")
    if obj:
        st.info(f"📋 Perfil cargado: **{obj}** · {nivel}")
    st.info("🚧 Próximamente — programa personalizado según tu evaluación y fase del ciclo, con links a los mejores coaches.")
