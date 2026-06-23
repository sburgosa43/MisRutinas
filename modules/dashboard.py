import streamlit as st
import utils.estado as estado

def mostrar():
    estado.cargar_perfil()
    st.title("⚙️ Configuración")

    st.subheader("Sesión activa")
    uid = estado.get("user_id", "—")
    st.info(f"Usuario: **{estado.get('nombre_usuario', uid)}** · ID: `{uid}`")

    st.divider()
    if st.button("🔄 Refrescar perfil desde Google Sheets", use_container_width=True):
        estado.refrescar()
        st.success("✅ Perfil recargado.")
        st.rerun()

    st.divider()
    if st.button("🔄 Refrescar perfil desde Google Sheets"):
        estado.refrescar()
        st.success("✅ Perfil recargado.")
        st.rerun()
