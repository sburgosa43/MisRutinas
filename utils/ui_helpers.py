"""Componentes reutilizables de UI para todos los módulos."""
import streamlit as st
import pandas as pd


def seccion_eliminar(nombre_sheet: str, df: pd.DataFrame, label: str = "registros"):
    """
    Sección para eliminar filas. Requiere columna '_fila_sheets' en df.
    """
    with st.expander(f"🗑️ Eliminar {label}"):
        if df is None or df.empty:
            st.info("No hay registros para eliminar.")
            return

        cols_visibles = [c for c in df.columns if not c.startswith("_") and c != "user_id"]
        df_display = df[cols_visibles].copy()

        st.caption("Selecciona una o varias filas y luego elimina.")
        event = st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=False,
            on_select="rerun",
            selection_mode="multi-row",
            key=f"sel_{nombre_sheet}",
        )
        filas_sel = event.selection.rows

        if filas_sel:
            st.warning(f"⚠️ {len(filas_sel)} fila(s) seleccionada(s). Esta acción no se puede deshacer.")
            if st.button(f"🗑️ Eliminar {len(filas_sel)} registro(s)",
                         type="primary", key=f"del_{nombre_sheet}"):
                from utils.sheets import eliminar_fila_sheets
                # Ordenar de mayor a menor para no desplazar índices
                for idx in sorted(filas_sel, reverse=True):
                    fila_real = int(df.iloc[idx]["_fila_sheets"])
                    eliminar_fila_sheets(nombre_sheet, fila_real)
                st.success("✅ Registros eliminados.")
                st.rerun()
