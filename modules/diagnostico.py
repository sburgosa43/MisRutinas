import streamlit as st

def mostrar():
    st.title("🔧 Diagnóstico de Conexión")
    if st.button("🔍 Verificar conexión", type="primary"):
        try:
            from utils.sheets import get_client
            client = get_client()
            st.success("✅ Credenciales OK")
            sheets = client.list_spreadsheet_files()
            if sheets:
                st.info(f"El service account tiene acceso a {len(sheets)} archivo(s):")
                for s in sheets:
                    st.code(f"Nombre: {s['name']}\nID:     {s['id']}")
            else:
                st.warning("⚠️ El service account no tiene ningún Sheet compartido.")
        except Exception as e:
            st.error(f"Error: {e}")
            st.exception(e)
