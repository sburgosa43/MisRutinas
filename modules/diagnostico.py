import streamlit as st

def mostrar():
    st.title("🔧 Diagnóstico de Conexión")
    st.caption("Módulo temporal para verificar acceso a Google Sheets")

    if st.button("🔍 Verificar conexión", type="primary"):
        try:
            from utils.sheets import get_client
            client = get_client()
            st.success("✅ Credenciales OK — autenticación exitosa")

            with st.spinner("Buscando Sheets accesibles..."):
                sheets = client.list_spreadsheet_files()

            if sheets:
                st.info(f"El service account tiene acceso a {len(sheets)} archivo(s):")
                for s in sheets:
                    st.code(f"Nombre: {s['name']}\nID:     {s['id']}")
            else:
                st.warning("⚠️ El service account no tiene ningún Google Sheet compartido.")
                st.markdown("""
                **Solución:**
                1. Abre `MisRutinas_DB` en Google Sheets
                2. Compartir → escribe `rio-veggi-app@rio-veggi-app.iam.gserviceaccount.com`
                3. Rol: **Editor** → desactiva notificación → **Compartir de todas formas**
                """)
        except Exception as e:
            st.error(f"Error: {e}")
            st.exception(e)
