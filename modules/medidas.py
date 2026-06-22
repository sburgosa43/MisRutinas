import streamlit as st
import pandas as pd
from datetime import date

import utils.estado as estado
from utils.sheets import get_worksheet, leer_df
from utils.ui_helpers import seccion_eliminar
from utils.calculos import (calcular_imc, clasificar_imc,
                             calcular_rcc, clasificar_rcc_mujer,
                             calcular_rel_hombros_cintura)

LBS_A_KG = 0.453592


def mostrar():
    estado.cargar_perfil()

    st.title("📊 Mis Medidas")
    st.caption("Los campos se pre-llenan con tu último registro guardado.")
    st.divider()

    # ── Formulario ────────────────────────────────────────────────────────
    st.subheader("Nuevo registro")
    col_izq, col_der = st.columns(2, gap="large")

    with col_izq:
        st.markdown("**Datos generales**")
        fecha    = st.date_input("Fecha", value=date.today())
        edad     = st.number_input("Edad (años)", 10, 100, estado.get("med_edad", 25), 1)
        peso_lbs = st.number_input("Peso (lbs)", 66.0, 440.0, estado.get("med_peso", 132.0), 0.5, format="%.1f")
        altura   = st.number_input("Altura (cm)", 100.0, 220.0, estado.get("med_altura", 165.0), 0.5, format="%.1f")
        notas    = st.text_area("Notas", placeholder="Observaciones opcionales...", height=80)

    with col_der:
        st.markdown("**Medidas corporales (cm)**")
        cintura   = st.number_input("Cintura",          40.0,  200.0, estado.get("med_cintura",   75.0),  0.5, format="%.1f")
        cadera    = st.number_input("Cadera",            50.0,  200.0, estado.get("med_cadera",    95.0),  0.5, format="%.1f")
        hombros   = st.number_input("Hombros",           50.0,  200.0, estado.get("med_hombros",  100.0),  0.5, format="%.1f")
        muslo_der = st.number_input("Muslo derecho",     20.0,  100.0, estado.get("med_muslo_der", 55.0),  0.5, format="%.1f")
        muslo_izq = st.number_input("Muslo izquierdo",   20.0,  100.0, estado.get("med_muslo_izq", 55.0),  0.5, format="%.1f")
        brazo_der = st.number_input("Brazo derecho",     15.0,   60.0, estado.get("med_brazo_der", 28.0),  0.5, format="%.1f")
        brazo_izq = st.number_input("Brazo izquierdo",   15.0,   60.0, estado.get("med_brazo_izq", 28.0),  0.5, format="%.1f")

    # ── Cálculos en tiempo real ───────────────────────────────────────────
    peso_kg = peso_lbs * LBS_A_KG
    imc     = calcular_imc(peso_kg, altura)
    rcc     = calcular_rcc(cintura, cadera)
    rel_hc  = calcular_rel_hombros_cintura(hombros, cintura)

    st.divider()
    st.subheader("Cálculos automáticos")
    m1, m2, m3 = st.columns(3, gap="medium")

    with m1:
        if imc:
            cat, _ = clasificar_imc(imc)
            st.metric("IMC", f"{imc}", cat)
    with m2:
        if rcc:
            cat, _ = clasificar_rcc_mujer(rcc)
            st.metric("Relación Cintura-Cadera (RCC)", f"{rcc}", cat)
    with m3:
        if rel_hc:
            ref = "✅ Figura atlética" if rel_hc >= 1.4 else "Por mejorar"
            st.metric("Hombros / Cintura", f"{rel_hc}", ref)

    st.divider()

    # ── Guardar ───────────────────────────────────────────────────────────
    if st.button("💾 Guardar registro", type="primary", use_container_width=True):
        with st.spinner("Guardando..."):
            try:
                ws = get_worksheet("medidas")
                ws.append_row([str(fecha), int(edad), float(peso_lbs), float(altura),
                               float(cintura), float(cadera), float(muslo_der), float(muslo_izq),
                               float(brazo_der), float(brazo_izq), float(hombros),
                               imc, rcc, rel_hc, notas.strip()])
                # Actualizar estado de sesión
                estado.set("med_peso",     peso_lbs)
                estado.set("med_altura",   altura)
                estado.set("med_edad",     int(edad))
                estado.set("med_cintura",  cintura)
                estado.set("med_cadera",   cadera)
                estado.set("med_hombros",  hombros)
                estado.set("med_muslo_der", muslo_der)
                estado.set("med_muslo_izq", muslo_izq)
                estado.set("med_brazo_der", brazo_der)
                estado.set("med_brazo_izq", brazo_izq)
                st.success("✅ Registro guardado correctamente.")
                st.balloons()
            except Exception as e:
                st.error(f"Error al guardar: {e}")
                st.exception(e)

    # ── Historial ─────────────────────────────────────────────────────────
    st.divider()
    st.subheader("Registros recientes")
    try:
        df = leer_df("medidas")
        if not df.empty:
            st.dataframe(df.iloc[::-1].reset_index(drop=True),
                         use_container_width=True, hide_index=True)
            st.divider()
            seccion_eliminar("medidas", df, "registros de medidas")
        else:
            st.info("Aún no hay registros. ¡Agrega el primero arriba! 💪")
    except Exception as e:
        st.error(f"Error al cargar historial: {e}")
        st.exception(e)
