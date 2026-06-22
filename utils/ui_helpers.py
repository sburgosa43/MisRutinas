"""Componentes reutilizables de UI para todos los módulos."""
import streamlit as st


def seccion_eliminar(nombre_sheet: str, df, label: str = "registros"):
    """
    Sección reutilizable para eliminar filas de cualquier módulo.
    df debe ser el DataFrame completo con índice pandas original.
    """
    with st.expander(f"🗑️ Eliminar {label}"):
        if df is None or df.empty:
            st.info("No hay registros para eliminar.")
            return

        st.caption("Haz clic en una o varias filas para seleccionarlas, luego elimina.")
        event = st.dataframe(
            df,
            use_container_width=True,
            hide_index=False,
            on_select="rerun",
            selection_mode="multi-row",
            key=f"sel_{nombre_sheet}",
        )
        filas = event.selection.rows

        if filas:
            st.warning(f"⚠️ {len(filas)} fila(s) seleccionada(s). Esta acción no se puede deshacer.")
            if st.button(f"🗑️ Eliminar {len(filas)} registro(s)", type="primary", key=f"del_{nombre_sheet}"):
                from utils.sheets import eliminar_fila
                for idx in sorted(filas, reverse=True):
                    eliminar_fila(nombre_sheet, idx)
                st.success("✅ Registros eliminados.")
                st.rerun()
