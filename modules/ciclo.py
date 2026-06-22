import streamlit as st
import pandas as pd
from datetime import date, timedelta

import utils.estado as estado
from utils.sheets import get_worksheet, leer_df
from utils.ui_helpers import seccion_eliminar

FASES = {
    "Menstrual":  {"rango":(1,5),   "emoji":"🔴","color":"#fee2e2",
                   "resumen":"El cuerpo se renueva. Escúchate.",
                   "hormonas":"Estrógeno y progesterona en su mínimo.",
                   "entrenamiento":"Yoga restaurativo, caminata, estiramientos. Evita alta intensidad los primeros 2 días.",
                   "nutricion":"Hierro (espinacas, lentejas), magnesio (chocolate negro, almendras).",
                   "coaches":"Yoga with Adriene","evitar":"HIIT y cargas máximas los primeros 2 días."},
    "Folicular":  {"rango":(6,13),  "emoji":"🟢","color":"#dcfce7",
                   "resumen":"¡Tu mejor semana! Energía en ascenso.",
                   "hormonas":"Estrógeno subiendo — fuerza, ánimo y recuperación mejoradas.",
                   "entrenamiento":"Ideal para levantar pesado, aprender técnica nueva, HIIT. El cuerpo tolera más volumen.",
                   "nutricion":"Proteína alta (1.8-2.2g/kg). Carbohidratos complejos pre-entreno.",
                   "coaches":"Heather Robertson, Bret Contreras, Jeff Nippard","evitar":"Nada especial — aprovecha esta ventana."},
    "Ovulatoria": {"rango":(14,16), "emoji":"🟡","color":"#fef9c3",
                   "resumen":"Pico de rendimiento. Tu momento cumbre.",
                   "hormonas":"Pico máximo de estrógeno + pico de LH. Máxima fuerza.",
                   "entrenamiento":"Intenta tus récords personales. HIIT de alta intensidad. ⚠️ Calienta bien — mayor laxitud en ligamentos.",
                   "nutricion":"Proteína alta. Hidratación extra.",
                   "coaches":"Sydney Cummings, Stephanie Sanzo","evitar":"Descuidar el calentamiento (riesgo LCA)."},
    "Lútea":      {"rango":(17,28), "emoji":"🟣","color":"#f3e8ff",
                   "resumen":"Calma y recuperación. Cuídate.",
                   "hormonas":"Progesterona dominante. Posible fatiga, retención de líquidos, SPM.",
                   "entrenamiento":"Fase temprana: mantén el programa. Fase tardía: baja intensidad, movilidad, yoga.",
                   "nutricion":"Antioxidantes, reduce sodio si hay retención. Chocolate negro ✓",
                   "coaches":"Yoga with Adriene, Heather Robertson (rutinas suaves)","evitar":"PRs en fase tardía."},
}


def calcular_fase(fecha_inicio: date, dur: int = 28) -> dict | None:
    dias = (date.today() - fecha_inicio).days
    if dias < 0: return None
    dia = (dias % dur) + 1
    for nombre, info in FASES.items():
        ini, fin = info["rango"]
        fin_real = fin if nombre != "Lútea" else dur
        if ini <= dia <= fin_real:
            return {**info, "nombre": nombre, "dia": dia, "restantes": fin_real - dia + 1}
    return {**FASES["Lútea"], "nombre": "Lútea", "dia": dia, "restantes": max(dur - dia + 1, 0)}


def mostrar():
    estado.cargar_perfil()
    st.title("🌙 Ciclo Menstrual & Entrenamiento")
    st.caption("Adapta tu entrenamiento a tu ciclo. Según McNulty et al. (2020/ACSM): hasta 12% más fuerza en fase folicular.")
    st.divider()

    try:
        ws   = get_worksheet("ciclo")
        df   = leer_df("ciclo")
    except Exception as e:
        st.error(f"Error conectando: {e}")
        return

    tiene = not df.empty
    dur_prom = 28

    if tiene:
        df["fecha_inicio"] = pd.to_datetime(df["fecha_inicio"]).dt.date
        df = df.sort_values("fecha_inicio").reset_index(drop=True)
        if len(df) >= 2:
            diffs = [(df.iloc[i]["fecha_inicio"] - df.iloc[i-1]["fecha_inicio"]).days for i in range(1, len(df))]
            dur_prom = round(sum(diffs) / len(diffs))

        fase = calcular_fase(df.iloc[-1]["fecha_inicio"], dur_prom)

        if fase:
            st.subheader("📍 Tu fase actual")
            col_card, col_info = st.columns([1, 2], gap="large")
            with col_card:
                st.markdown(f"""
                <div style="background:{fase['color']};border-radius:16px;padding:28px;text-align:center;">
                    <div style="font-size:52px">{fase['emoji']}</div>
                    <div style="font-size:24px;font-weight:700;margin:10px 0">{fase['nombre']}</div>
                    <div style="color:#374151">Día <b>{fase['dia']}</b> de {dur_prom}</div>
                    <div style="margin-top:8px;font-size:13px;color:#6b7280">{fase['restantes']} días restantes</div>
                </div>""", unsafe_allow_html=True)
            with col_info:
                st.markdown(f"### {fase['resumen']}")
                st.markdown(f"🔬 **Hormonas:** {fase['hormonas']}")
                st.markdown(f"🏋️ **Entrenamiento:** {fase['entrenamiento']}")
                st.markdown(f"🥗 **Nutrición:** {fase['nutricion']}")
                st.markdown(f"👩‍💻 **Coaches recomendados:** {fase['coaches']}")
                st.markdown(f"⚠️ **Cuidado con:** {fase['evitar']}")

        st.divider()
        st.subheader("📅 Próximos ciclos estimados")
        st.caption(f"Ciclo promedio: **{dur_prom} días** · {len(df)} registro(s)")
        proximos = [df.iloc[-1]["fecha_inicio"] + timedelta(days=dur_prom * i) for i in range(1, 5)]
        cols = st.columns(4)
        for col, fp in zip(cols, proximos):
            dias_falta = (fp - date.today()).days
            label = f"En {dias_falta} días" if dias_falta > 0 else "¡Esta semana!"
            col.metric(fp.strftime("%d %b %Y"), label)

        st.divider()
        st.subheader("📋 Historial")
        df_show = df.copy()
        df_show["fecha_inicio"] = df_show["fecha_inicio"].astype(str)
        if len(df_show) >= 2:
            df_show["duración (días)"] = ["—"] + [
                str((df.iloc[i]["fecha_inicio"] - df.iloc[i-1]["fecha_inicio"]).days)
                for i in range(1, len(df))
            ]
        st.dataframe(df_show.iloc[::-1].reset_index(drop=True), use_container_width=True, hide_index=True)
        st.divider()
        seccion_eliminar("ciclo", df_show, "registros de ciclo")
    else:
        st.info("📋 Registra la fecha de inicio de tu último período para ver tu fase actual y predicciones.")

    st.divider()
    with st.expander("➕ Registrar inicio de ciclo", expanded=not tiene):
        c1, c2 = st.columns(2)
        with c1:
            nueva = st.date_input("Fecha de inicio", value=date.today(), max_value=date.today())
        with c2:
            notas_c = st.text_input("Notas", placeholder="Ej: cólicos, flujo abundante...")
        if st.button("💾 Registrar", type="primary"):
            try:
                ws.append_row([str(nueva), "", notas_c.strip()])
                st.success("✅ Registrado.")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    st.divider()
    st.subheader("📖 Guía científica de las 4 fases")
    for nombre, info in FASES.items():
        ini, fin = info["rango"]
        with st.expander(f"{info['emoji']} **{nombre}** — Días {ini}–{fin}"):
            st.markdown(f"**{info['resumen']}**")
            st.markdown(f"🔬 {info['hormonas']}")
            st.markdown(f"🏋️ **Entrenamiento:** {info['entrenamiento']}")
            st.markdown(f"🥗 **Nutrición:** {info['nutricion']}")
