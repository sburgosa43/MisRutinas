import streamlit as st
import pandas as pd
from datetime import date

from utils.sheets import get_worksheet
from utils.calculos import (
    calcular_imc, clasificar_imc,
    calcular_rcc, clasificar_rcc_mujer,
    calcular_rel_hombros_cintura,
)

LBS_A_KG = 0.453592

def mostrar():
    st.title("📊 Mis Medidas")
    st.caption("Registra tus medidas corporales y observa tus cálculos en tiempo real.")
    st.divider()

    st.subheader("Nuevo registro")

    col_izq, col_der = st.columns(2, gap="large")

    with col_izq:
        st.markdown("**Datos generales**")
        fecha  = st.date_input("Fecha", value=date.today())
        edad   = st.number_input("Edad (años)", min_value=10, max_value=100, value=25, step=1)
        peso_lbs = st.number_input("Peso (lbs)", min_value=66.0, max_value=440.0, value=132.0, step=0.5, format="%.1f")
        altura = st.number_input("Altura (cm)", min_value=100.0, max_value=220.0, value=165.0, step=0.5, format="%.1f")
        notas  = st.text_area("Notas", placeholder="Observaciones opcionales...", height=80)

    with col_der:
        st.markdown("**Medidas corporales (cm)**")
        cintura   = st.number_input("Cintura",        min_value=40.0,  max_value=200.0, value=75.0,  step=0.5, format="%.1f")
        cadera    = st.number_input("Cadera",          min_value=50.0,  max_value=200.0, value=95.0,  step=0.5, format="%.1f")
        hombros   = st.number_input("Hombros",         min_value=50.0,  max_value=200.0, value=100.0, step=0.5, format="%.1f")
        muslo_der = st.number_input("Muslo derecho",   min_value=20.0,  max_value=100.0, value=55.0,  step=0.5, format="%.1f")
        muslo_izq = st.number_input("Muslo izquierdo", min_value=20.0,  max_value=100.0, value=55.0,  step=0.5, format="%.1f")
        brazo_der = st.number_input("Brazo derecho",   min_value=15.0,  max_value=60.0,  value=28.0,  step=0.5, format="%.1f")
        brazo_izq = st.number_input("Brazo izquierdo", min_value=15.0,  max_value=60.0,  value=28.0,  step=0.5, format="%.1f")

    # Convertir lbs a kg solo para el cálculo de IMC
    peso_kg = peso_lbs * LBS_A_KG

    st.divider()
    st.subheader("Cálculos automáticos")

    imc    = calcular_imc(peso_kg, altura)
    rcc    = calcular_rcc(cintura, cadera)
    rel_hc = calcular_rel_hombros_cintura(hombros, cintura)

    m1, m2, m3 = st.columns(3, gap="medium")

    with m1:
        if imc is not None:
            cat_imc, _ = clasificar_imc(imc)
            st.metric("Índice de Masa Corporal (IMC)", f"{imc}", cat_imc)
        else:
            st.metric("IMC", "—")

    with m2:
        if rcc is not None:
            cat_rcc, _ = clasificar_rcc_mujer(rcc)
            st.metric("Relación Cintura-Cadera (RCC)", f"{rcc}", cat_rcc)
        else:
            st.metric("RCC", "—")

    with m3:
        if rel_hc is not None:
            referencia = "✅ Figura atlética" if rel_hc >= 1.4 else "Por mejorar"
            st.metric("Relación Hombros-Cintura", f"{rel_hc}", referencia)
        else:
            st.metric("Hombros / Cintura", "—")

    st.divider()

    if st.button("💾 Guardar registro", type="primary", use_container_width=True):
        with st.spinner("Guardando en Google Sheets..."):
            try:
                ws = get_worksheet("medidas")
                ws.append_row([
                    str(fecha), int(edad),
                    float(peso_lbs), float(altura),
                    float(cintura), float(cadera),
                    float(muslo_der), float(muslo_izq),
                    float(brazo_der), float(brazo_izq),
                    float(hombros),
                    imc, rcc, rel_hc,
                    notas.strip(),
                ])
                st.success("✅ Registro guardado correctamente.")
                st.balloons()
            except Exception as e:
                st.error(f"Error al guardar: {e}")
                st.exception(e)

    st.divider()
    st.subheader("Registros recientes")

    try:
        ws = get_worksheet("medidas")
        datos = ws.get_all_records()
        if datos:
            df = pd.DataFrame(datos)
            st.dataframe(
                df.tail(10).iloc[::-1].reset_index(drop=True),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("Aún no hay registros. ¡Agrega el primero arriba! 💪")
    except Exception as e:
        st.error(f"Error al cargar historial: {e}")
        st.exception(e)
