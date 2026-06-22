import streamlit as st
import pandas as pd
from datetime import date, timedelta
from utils.sheets import get_worksheet

# ─────────────────────────────────────────────────────────────────────────────
# BASE CIENTÍFICA: FASES DEL CICLO
# Referencia: Sung et al. 2014, Wikström-Frisén 2017, McNulty 2020 (ACSM)
# ─────────────────────────────────────────────────────────────────────────────
FASES = {
    "Menstrual": {
        "rango": (1, 5),
        "emoji": "🔴",
        "color_bg": "#fee2e2",
        "color_badge": "#ef4444",
        "resumen": "El cuerpo se renueva. Escúchate.",
        "hormonas": "Estrógeno y progesterona en su nivel más bajo.",
        "entrenamiento": "Movimiento suave: yoga restaurativo, caminata, estiramientos. Si hay cólicos fuertes, el descanso activo es válido. Evita alta intensidad los primeros 2 días.",
        "ejercicios_ideales": ["Yoga", "Caminata", "Estiramientos", "Respiración y movilidad"],
        "evitar": "Ejercicios de alta intensidad o mucho impacto los primeros 2 días.",
        "nutricion": "Aumenta hierro (espinacas, lentejas, carne roja magra) y magnesio (chocolate negro, almendras) para aliviar cólicos.",
        "coaches": "Yoga with Adriene",
    },
    "Folicular": {
        "rango": (6, 13),
        "emoji": "🟢",
        "color_bg": "#dcfce7",
        "color_badge": "#16a34a",
        "resumen": "¡Tu mejor semana! Energía al máximo.",
        "hormonas": "Estrógeno subiendo. Más fuerza, mejor humor, recuperación más rápida.",
        "entrenamiento": "Ideal para levantar pesado, aprender técnica nueva, HIIT. El cuerpo tolera más volumen y se recupera más rápido que en cualquier otra fase.",
        "ejercicios_ideales": ["Sentadillas", "Hip Thrust", "Peso muerto", "HIIT", "Press", "Nuevos movimientos"],
        "evitar": "Nada en particular — aprovecha esta ventana.",
        "nutricion": "Proteína alta (1.8-2.2g/kg). Carbohidratos complejos pre-entrenamiento. Excelente momento para déficit calórico moderado.",
        "coaches": "Heather Robertson, Bret Contreras, Jeff Nippard",
    },
    "Ovulatoria": {
        "rango": (14, 16),
        "emoji": "🟡",
        "color_bg": "#fef9c3",
        "color_badge": "#ca8a04",
        "resumen": "Pico de rendimiento. Tu momento cumbre.",
        "hormonas": "Pico máximo de estrógeno + pico de LH. Máxima fuerza y motivación.",
        "entrenamiento": "Intenta tus récords personales. Máximo esfuerzo. HIIT de alta intensidad. ⚠️ Mayor laxitud en ligamentos — calienta bien y cuida rodillas.",
        "ejercicios_ideales": ["PR en todos los levantamientos", "Plyo", "Sprints", "Clases grupales intensas"],
        "evitar": "Descuidar el calentamiento. El estrógeno alto relaja ligamentos (riesgo LCA).",
        "nutricion": "Mantén proteína alta. Hidratación extra. No es momento de déficit agresivo.",
        "coaches": "Sydney Cummings, Stephanie Sanzo",
    },
    "Lútea": {
        "rango": (17, 28),
        "emoji": "🟣",
        "color_bg": "#f3e8ff",
        "color_badge": "#9333ea",
        "resumen": "Calma y recuperación. Cuídate.",
        "hormonas": "Progesterona dominante. Posible fatiga, retención de líquidos, SPM en días finales.",
        "entrenamiento": "Fase temprana (17-21): aún buena fuerza, mantén el programa. Fase tardía (22-28): reduce intensidad, prioriza movilidad, yoga y cardio suave. No te fuerces.",
        "ejercicios_ideales": ["Pilates", "Yoga", "Cardio moderado", "Pesas con volumen bajo"],
        "evitar": "Intentar PRs en fase tardía. Exceso de cafeína si hay SPM.",
        "nutricion": "Antioxidantes (arándanos, espinacas). Reduce sodio si hay retención. Magnesio para el SPM. Chocolate negro ✓",
        "coaches": "Yoga with Adriene, Heather Robertson (rutinas suaves)",
    },
}


def calcular_fase(fecha_inicio: date, duracion_promedio: int = 28) -> dict | None:
    hoy = date.today()
    dias_totales = (hoy - fecha_inicio).days
    if dias_totales < 0:
        return None
    dia_ciclo = (dias_totales % duracion_promedio) + 1
    for nombre, info in FASES.items():
        ini, fin = info["rango"]
        fin_real = fin if nombre != "Lútea" else duracion_promedio
        if ini <= dia_ciclo <= fin_real:
            return {**info, "nombre": nombre, "dia_ciclo": dia_ciclo,
                    "dias_restantes": fin_real - dia_ciclo + 1}
    return {**FASES["Lútea"], "nombre": "Lútea", "dia_ciclo": dia_ciclo,
            "dias_restantes": max(duracion_promedio - dia_ciclo + 1, 0)}


def predecir_ciclos(fecha_ultimo: date, duracion: int, n: int = 4) -> list[date]:
    return [fecha_ultimo + timedelta(days=duracion * i) for i in range(1, n + 1)]


def mostrar():
    st.title("🌙 Ciclo Menstrual & Entrenamiento")
    st.caption("Adapta tu entrenamiento a tu ciclo. La ciencia muestra hasta un 12% más de fuerza en fase folicular vs lútea. (McNulty et al., 2020)")
    st.divider()

    # ── Cargar datos ──────────────────────────────────────────────────────
    try:
        ws   = get_worksheet("ciclo")
        data = ws.get_all_records()
        df   = pd.DataFrame(data) if data else pd.DataFrame()
    except Exception as e:
        st.error(f"Error conectando: {e}")
        return

    tiene_datos = not df.empty
    duracion_prom = 28

    if tiene_datos:
        df["fecha_inicio"] = pd.to_datetime(df["fecha_inicio"]).dt.date
        df = df.sort_values("fecha_inicio").reset_index(drop=True)
        if len(df) >= 2:
            diffs = [(df.iloc[i]["fecha_inicio"] - df.iloc[i-1]["fecha_inicio"]).days
                     for i in range(1, len(df))]
            duracion_prom = round(sum(diffs) / len(diffs))

        fecha_ultimo = df.iloc[-1]["fecha_inicio"]
        fase = calcular_fase(fecha_ultimo, duracion_prom)

        # ── Fase actual ───────────────────────────────────────────────────
        if fase:
            st.subheader("📍 Tu fase actual")
            col_card, col_info = st.columns([1, 2], gap="large")

            with col_card:
                st.markdown(f"""
                <div style="background:{fase['color_bg']};border-radius:16px;padding:28px;text-align:center;">
                    <div style="font-size:52px">{fase['emoji']}</div>
                    <div style="font-size:24px;font-weight:700;margin:10px 0">{fase['nombre']}</div>
                    <div style="font-size:15px;color:#374151">Día <b>{fase['dia_ciclo']}</b> de {duracion_prom}</div>
                    <div style="margin-top:8px;font-size:13px;color:#6b7280">{fase['dias_restantes']} días restantes en esta fase</div>
                </div>
                """, unsafe_allow_html=True)

            with col_info:
                st.markdown(f"### {fase['resumen']}")
                st.markdown(f"🔬 **Hormonas:** {fase['hormonas']}")
                st.markdown(f"🏋️ **Entrenamiento:** {fase['entrenamiento']}")
                st.markdown(f"🥗 **Nutrición:** {fase['nutricion']}")
                st.markdown(f"👩‍💻 **Coaches recomendados:** {fase['coaches']}")
                if fase.get("evitar"):
                    st.markdown(f"⚠️ **Cuidado con:** {fase['evitar']}")

        st.divider()

        # ── Predicciones ──────────────────────────────────────────────────
        st.subheader("📅 Próximos ciclos estimados")
        st.caption(f"Ciclo promedio: **{duracion_prom} días** • Basado en {len(df)} registro(s)")

        proximos = predecir_ciclos(fecha_ultimo, duracion_prom, 4)
        cols = st.columns(4)
        for col, fp in zip(cols, proximos):
            dias_falta = (fp - date.today()).days
            label = f"En {dias_falta} días" if dias_falta > 0 else ("¡Esta semana!" if dias_falta >= -3 else "Esta semana")
            col.metric(fp.strftime("%d %b %Y"), label)

        st.divider()

        # ── Historial ─────────────────────────────────────────────────────
        st.subheader("📋 Historial de ciclos")
        df_show = df.copy()
        df_show["fecha_inicio"] = df_show["fecha_inicio"].astype(str)
        if len(df_show) >= 2:
            df_show["duración (días)"] = ["—"] + [
                str((df.iloc[i]["fecha_inicio"] - df.iloc[i-1]["fecha_inicio"]).days)
                for i in range(1, len(df))
            ]
        st.dataframe(df_show.iloc[::-1].reset_index(drop=True), use_container_width=True, hide_index=True)

    else:
        st.info("📋 Registra la fecha de inicio de tu último período para ver tu fase actual y predicciones.")

    # ── Registrar nuevo ciclo ─────────────────────────────────────────────
    st.divider()
    with st.expander("➕ Registrar inicio de ciclo", expanded=not tiene_datos):
        c1, c2 = st.columns(2)
        with c1:
            nueva_fecha = st.date_input("Fecha de inicio del período", value=date.today(), max_value=date.today())
        with c2:
            notas_c = st.text_input("Notas opcionales", placeholder="Ej: cólicos, flujo abundante, estrés...")
        if st.button("💾 Registrar", type="primary"):
            try:
                ws.append_row([str(nueva_fecha), "", notas_c.strip()])
                st.success("✅ Ciclo registrado.")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    # ── Guía completa de fases ────────────────────────────────────────────
    st.divider()
    st.subheader("📖 Guía científica de las 4 fases")
    for nombre, info in FASES.items():
        ini, fin = info["rango"]
        with st.expander(f"{info['emoji']} **{nombre}** — Días {ini}-{fin}"):
            st.markdown(f"**{info['resumen']}**")
            st.markdown(f"🔬 {info['hormonas']}")
            st.markdown(f"🏋️ **Entrenamiento ideal:** {info['entrenamiento']}")
            ejs = ", ".join(info["ejercicios_ideales"])
            st.markdown(f"✅ **Ejercicios recomendados:** {ejs}")
            st.markdown(f"🥗 **Nutrición:** {info['nutricion']}")
