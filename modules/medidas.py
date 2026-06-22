import streamlit as st
import pandas as pd
from datetime import date, timedelta

import streamlit.components.v1 as components
import utils.estado as estado
from utils.sheets import get_worksheet, leer_df
from utils.ui_helpers import seccion_eliminar
from utils.calculos import (calcular_imc, clasificar_imc,
                             calcular_rcc, clasificar_rcc_mujer,
                             calcular_rel_hombros_cintura)

LBS_A_KG = 0.453592


# ──────────────────────────────────────────────────────────────────────────────
# SILHOUETA SVG
# ──────────────────────────────────────────────────────────────────────────────

def silhoueta_svg(genero: str) -> str:
    c  = "#cbd5e1"   # color cuerpo
    lc = "#818cf8"   # color líneas de medición

    if genero == "Mujer":
        cuerpo = f"""
        <ellipse cx="80" cy="24"  rx="20" ry="22" fill="{c}"/>
        <ellipse cx="80" cy="54"  rx="10" ry="13" fill="{c}"/>
        <ellipse cx="80" cy="80"  rx="36" ry="18" fill="{c}"/>
        <ellipse cx="80" cy="108" rx="29" ry="23" fill="{c}"/>
        <ellipse cx="80" cy="137" rx="22" ry="18" fill="{c}"/>
        <ellipse cx="80" cy="160" rx="34" ry="20" fill="{c}"/>
        <ellipse cx="80" cy="178" rx="33" ry="15" fill="{c}"/>
        <ellipse cx="35"  cy="115" rx="9"  ry="42" fill="{c}"/>
        <ellipse cx="125" cy="115" rx="9"  ry="42" fill="{c}"/>
        <ellipse cx="60"  cy="225" rx="18" ry="46" fill="{c}"/>
        <ellipse cx="100" cy="225" rx="18" ry="46" fill="{c}"/>
        <ellipse cx="58"  cy="293" rx="12" ry="35" fill="{c}"/>
        <ellipse cx="102" cy="293" rx="12" ry="35" fill="{c}"/>"""
        puntos = [(80,"Hombros"),(115,"Brazos"),(137,"Cintura"),(163,"Cadera"),(225,"Muslos")]
        emoji = "👩 Mujer"

    else:  # Hombre
        cuerpo = f"""
        <ellipse cx="80" cy="24"  rx="20" ry="22" fill="{c}"/>
        <ellipse cx="80" cy="54"  rx="12" ry="13" fill="{c}"/>
        <ellipse cx="80" cy="80"  rx="43" ry="19" fill="{c}"/>
        <ellipse cx="80" cy="110" rx="35" ry="26" fill="{c}"/>
        <ellipse cx="80" cy="143" rx="29" ry="20" fill="{c}"/>
        <ellipse cx="80" cy="163" rx="28" ry="17" fill="{c}"/>
        <ellipse cx="80" cy="178" rx="28" ry="13" fill="{c}"/>
        <ellipse cx="30"  cy="116" rx="11" ry="44" fill="{c}"/>
        <ellipse cx="130" cy="116" rx="11" ry="44" fill="{c}"/>
        <ellipse cx="58"  cy="225" rx="21" ry="47" fill="{c}"/>
        <ellipse cx="102" cy="225" rx="21" ry="47" fill="{c}"/>
        <ellipse cx="56"  cy="293" rx="14" ry="35" fill="{c}"/>
        <ellipse cx="104" cy="293" rx="14" ry="35" fill="{c}"/>"""
        puntos = [(80,"Hombros"),(110,"Pecho"),(116,"Brazos"),(143,"Cintura"),(163,"Cadera"),(225,"Muslos")]
        emoji = "👨 Hombre"

    lineas = ""
    for y, label in puntos:
        lineas += f"""
        <line x1="6" y1="{y}" x2="154" y2="{y}"
              stroke="{lc}" stroke-width="1.2" stroke-dasharray="4,3" opacity="0.9"/>
        <circle cx="6"   cy="{y}" r="2.5" fill="{lc}"/>
        <circle cx="154" cy="{y}" r="2.5" fill="{lc}"/>"""

    return f"""
    <div style="background:#f1f5f9;border-radius:12px;padding:12px 6px;
                text-align:center;border:1px solid #e2e8f0;">
      <p style="font-size:12px;font-weight:600;color:#475569;margin:0 0 6px 0;">
        {emoji} — Puntos de medición</p>
      <svg viewBox="0 0 160 340" xmlns="http://www.w3.org/2000/svg"
           style="width:100%;max-width:150px;height:auto;">
        {cuerpo}
        {lineas}
      </svg>
      <p style="font-size:10px;color:#94a3b8;margin:6px 0 0 0;">
        Las líneas muestran dónde medir</p>
    </div>"""


# ──────────────────────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────────────────────

def calcular_edad(fecha_nac: date) -> int:
    hoy = date.today()
    return hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))


# ──────────────────────────────────────────────────────────────────────────────
# MÓDULO PRINCIPAL
# ──────────────────────────────────────────────────────────────────────────────

def mostrar():
    estado.cargar_perfil()

    st.title("📊 Mis Medidas")
    st.caption("Los campos se pre-llenan con tu último registro. Las líneas en la silueta indican dónde tomar cada medida.")
    st.divider()

    # ── 1. Datos generales (fila completa) ───────────────────────────────
    st.subheader("Datos generales")
    g1, g2, g3, g4 = st.columns([1, 1, 1, 1])

    with g1:
        genero = st.radio("Género", ["Mujer", "Hombre"],
                          index=0 if estado.get("genero","Mujer") == "Mujer" else 1,
                          horizontal=True)
        estado.set("genero", genero)

    with g2:
        hoy = date.today()
        fn_default = estado.get("fecha_nacimiento", None)
        if fn_default and isinstance(fn_default, str):
            try:
                fn_default = date.fromisoformat(fn_default)
            except Exception:
                fn_default = None
        fn_default = fn_default or date(hoy.year - 25, hoy.month, hoy.day)
        fecha_nac = st.date_input("Fecha de nacimiento",
                                   value=fn_default,
                                   max_value=hoy - timedelta(days=365*10),
                                   format="DD/MM/YYYY")
        edad_calc = calcular_edad(fecha_nac)
        st.caption(f"Edad calculada: **{edad_calc} años**")

    with g3:
        peso_lbs = st.number_input("Peso (lbs)", 66.0, 440.0,
                                    estado.get("med_peso", 132.0), 0.5, format="%.1f")

    with g4:
        altura = st.number_input("Altura (cm)", 100.0, 220.0,
                                  estado.get("med_altura", 165.0), 0.5, format="%.1f")

    st.divider()

    # ── 2. Silueta + Medidas corporales ───────────────────────────────────
    col_sil, col_med = st.columns([1, 1], gap="large")

    with col_sil:
        st.subheader("Guía visual")
        components.html(silhoueta_svg(genero), height=380, scrolling=False)

    with col_med:
        st.subheader("Medidas corporales (cm)")

        hombros = st.number_input("Hombros",
            min_value=50.0, max_value=200.0,
            value=estado.get("med_hombros", 100.0), step=0.5, format="%.1f")

        # Pecho — mostrar para ambos pero con label contextual
        label_pecho = "Pecho / Busto" if genero == "Mujer" else "Pecho"
        pecho = st.number_input(label_pecho,
            min_value=50.0, max_value=200.0,
            value=estado.get("med_pecho", 90.0), step=0.5, format="%.1f")

        col_b1, col_b2 = st.columns(2)
        with col_b1:
            brazo_der = st.number_input("Brazo derecho",
                min_value=15.0, max_value=60.0,
                value=estado.get("med_brazo_der", 28.0), step=0.5, format="%.1f")
        with col_b2:
            brazo_izq = st.number_input("Brazo izquierdo",
                min_value=15.0, max_value=60.0,
                value=estado.get("med_brazo_izq", 28.0), step=0.5, format="%.1f")

        cintura = st.number_input("Cintura",
            min_value=40.0, max_value=200.0,
            value=estado.get("med_cintura", 75.0), step=0.5, format="%.1f")

        cadera = st.number_input("Cadera",
            min_value=50.0, max_value=200.0,
            value=estado.get("med_cadera", 95.0), step=0.5, format="%.1f")

        col_m1, col_m2 = st.columns(2)
        with col_m1:
            muslo_der = st.number_input("Muslo derecho",
                min_value=20.0, max_value=100.0,
                value=estado.get("med_muslo_der", 55.0), step=0.5, format="%.1f")
        with col_m2:
            muslo_izq = st.number_input("Muslo izquierdo",
                min_value=20.0, max_value=100.0,
                value=estado.get("med_muslo_izq", 55.0), step=0.5, format="%.1f")

        notas = st.text_area("Notas", placeholder="Observaciones opcionales...", height=68)

    # ── 3. Cálculos automáticos ───────────────────────────────────────────
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

    # ── 4. Guardar ────────────────────────────────────────────────────────
    fecha_registro = date.today()
    if st.button("💾 Guardar registro", type="primary", use_container_width=True):
        with st.spinner("Guardando..."):
            try:
                ws = get_worksheet("medidas")
                ws.append_row([
                    str(fecha_registro), genero, str(fecha_nac), edad_calc,
                    float(peso_lbs), float(altura),
                    float(hombros), float(pecho),
                    float(cintura), float(cadera),
                    float(muslo_der), float(muslo_izq),
                    float(brazo_der), float(brazo_izq),
                    imc, rcc, rel_hc,
                    notas.strip()
                ])
                # Actualizar estado de sesión
                estado.set("genero",         genero)
                estado.set("fecha_nacimiento", str(fecha_nac))
                estado.set("med_peso",       peso_lbs)
                estado.set("med_altura",     altura)
                estado.set("med_hombros",    hombros)
                estado.set("med_pecho",      pecho)
                estado.set("med_cintura",    cintura)
                estado.set("med_cadera",     cadera)
                estado.set("med_muslo_der",  muslo_der)
                estado.set("med_muslo_izq",  muslo_izq)
                estado.set("med_brazo_der",  brazo_der)
                estado.set("med_brazo_izq",  brazo_izq)
                st.success("✅ Registro guardado correctamente.")
                st.balloons()
            except Exception as e:
                st.error(f"Error al guardar: {e}")
                st.exception(e)

    # ── 5. Historial ──────────────────────────────────────────────────────
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
