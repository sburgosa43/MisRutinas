import streamlit as st
import utils.estado as estado
from utils.sheets import get_worksheet

def mostrar():
    estado.cargar_perfil()
    st.title("⚙️ Configuración")

    st.subheader("Tu perfil")
    nombre = st.text_input("Nombre", value=estado.get("nombre_usuario", "Mi Rutina"))

    if st.button("💾 Guardar", type="primary"):
        try:
            ws = get_worksheet("config")
            datos = ws.get_all_records()
            filas = [i+2 for i, r in enumerate(datos) if r.get("clave") == "nombre_usuario"]
            if filas:
                ws.update_cell(filas[0], 2, nombre)
            else:
                ws.append_row(["nombre_usuario", nombre])
            estado.set("nombre_usuario", nombre)
            st.success("✅ Guardado.")
        except Exception as e:
            st.error(f"Error: {e}")

    st.divider()
    if st.button("🔄 Refrescar perfil desde Google Sheets"):
        estado.refrescar()
        st.success("✅ Perfil recargado.")
        st.rerun()
