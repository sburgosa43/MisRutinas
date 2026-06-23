import streamlit as st
import utils.estado as estado

def mostrar():
    estado.cargar_perfil()
    st.title("📈 Progreso")
    st.info("🚧 Próximamente — gráficas de evolución de peso, IMC y medidas en el tiempo.")
