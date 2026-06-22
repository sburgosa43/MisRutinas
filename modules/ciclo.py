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


def preparar_df(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia el DataFrame y calcula duraciones reales."""
    if df.empty:
        return df

    df = df.copy()
    df["fecha_inicio"] = pd.to_datetime(df["fecha_inicio"], errors="coerce").dt.date
    df["fecha_fin"]    = pd.to_datetime(df["fecha_fin"],    errors="coerce").dt.date
    df = df.dropna(subset=["fecha_inicio"]).sort_values("fecha_inicio").reset_index(drop=True)

    # Duración del período (sangrado): fecha_fin - fecha_inicio
    df["días período"] = df.apply(
        lambda r: (r["fecha_fin"] - r["fecha_inicio"]).days
        if pd.notna(r["fecha_fin"]) else "—", axis=1
    )

    # Duración del ciclo: inicio[i] - inicio[i-1]
    ciclos = ["—"]
    for i in range(1, len(df)):
        diff = (df.iloc[i]["fecha_inicio"] - df.iloc[i-1]["fecha_inicio"]).days
        ciclos.append(diff)
    df["días ciclo"] = ciclos

    return df


def mostrar():
    estado.cargar_perfil()
    st.title("🌙 Ciclo Menstrual & Entrenamiento")
    st.caption("Registra tus ciclos históricos para pronósticos personalizados. McNulty et al. (2020/ACSM): hasta 12% más fuerza en fase folicular.")
    st.divider()

    try:
        ws = get_worksheet("ciclo")
        df_raw = leer_df("ciclo")
    except Exception as e:
        st.error(f"Error conectando: {e}")
        return

    # Asegurar que existen las columnas necesarias
    for col in ["fecha_inicio","fecha_fin","notas"]:
        if col not in df_raw.columns:
            df_raw[col] = ""

    df = preparar_df(df_raw)
    tiene = not df.empty

    # ── Calcular estadísticas del ciclo personal ──────────────────────────
    dur_prom_ciclo   = 28
    dur_prom_periodo = 5

    if tiene:
        ciclos_reales = [c for c in df["días ciclo"] if isinstance(c, int)]
        if ciclos_reales:
            dur_prom_ciclo = round(sum(ciclos_reales) / len(ciclos_reales))

        periodos_reales = [p for p in df["días período"] if isinstance(p, int)]
        if periodos_reales:
            dur_prom_periodo = round(sum(periodos_reales) / len(periodos_reales))

    # ── Fase actual ───────────────────────────────────────────────────────
    if tiene:
        fase = calcular_fase(df.iloc[-1]["fecha_inicio"], dur_prom_ciclo)
        if fase:
            st.subheader("📍 Tu fase actual")
            col_card, col_info = st.columns([1, 2], gap="large")
            with col_card:
                st.markdown(f"""
                <div style="background:{fase['color']};border-radius:16px;padding:28px;text-align:center;">
                    <div style="font-size:52px">{fase['emoji']}</div>
                    <div style="font-size:24px;font-weight:700;margin:10px 0">{fase['nombre']}</div>
                    <div style="color:#374151">Día <b>{fase['dia']}</b> de {dur_prom_ciclo}</div>
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

        # ── Estadísticas personales ───────────────────────────────────────
        st.subheader("📊 Tu ciclo personal")
        e1, e2, e3 = st.columns(3)
        e1.metric("Duración promedio del ciclo",   f"{dur_prom_ciclo} días",
                  help="Días desde el inicio de un período hasta el siguiente")
        e2.metric("Duración promedio del período",  f"{dur_prom_periodo} días",
                  help="Días de sangrado promedio")
        e3.metric("Ciclos registrados", len(df))

        st.divider()

        # ── Predicciones ──────────────────────────────────────────────────
        st.subheader("📅 Próximos ciclos estimados")
        st.caption(f"Basado en tu ciclo promedio personal de **{dur_prom_ciclo} días**")

        ultimo_inicio = df.iloc[-1]["fecha_inicio"]
        proximos = [ultimo_inicio + timedelta(days=dur_prom_ciclo * i) for i in range(1, 5)]
        cols = st.columns(4)
        for col, fp in zip(cols, proximos):
            dias_falta = (fp - date.today()).days
            if dias_falta < 0:
                label = "Ya pasó"
            elif dias_falta == 0:
                label = "¡Hoy!"
            elif dias_falta <= 7:
                label = f"¡En {dias_falta} días!"
            else:
                label = f"En {dias_falta} días"
            col.metric(fp.strftime("%d %b %Y"), label)

        st.divider()

        # ── Historial ─────────────────────────────────────────────────────
        st.subheader("📋 Historial de ciclos")
        df_show = df[["fecha_inicio","fecha_fin","días período","días ciclo","notas"]].copy()
        df_show["fecha_inicio"] = df_show["fecha_inicio"].astype(str)
        df_show["fecha_fin"]    = df_show["fecha_fin"].apply(lambda x: str(x) if pd.notna(x) and x != "" else "—")
        st.dataframe(df_show.iloc[::-1].reset_index(drop=True), use_container_width=True, hide_index=True)

        st.divider()
        seccion_eliminar("ciclo", df_show, "registros de ciclo")
    else:
        st.info("📋 Registra tus ciclos anteriores para ver tu fase actual y pronósticos personalizados.")

    # ── Registrar ciclo ───────────────────────────────────────────────────
    st.divider()
    with st.expander("➕ Registrar ciclo", expanded=not tiene):
        st.caption("Puedes ingresar ciclos pasados para mejorar el pronóstico. La fecha de fin es opcional si el período aún no ha terminado.")

        c1, c2 = st.columns(2)
        with c1:
            nueva_inicio = st.date_input(
                "📅 Fecha de INICIO del período",
                value=date.today(),
                max_value=date.today(),
                key="ci_inicio"
            )
        with c2:
            tiene_fin = st.checkbox("¿Ya terminó el período?", value=True)
            if tiene_fin:
                nueva_fin = st.date_input(
                    "📅 Fecha de FIN del período",
                    value=min(nueva_inicio + timedelta(days=4), date.today()),
                    min_value=nueva_inicio,
                    max_value=date.today(),
                    key="ci_fin"
                )
            else:
                nueva_fin = None

        notas_c = st.text_input("Notas opcionales", placeholder="Ej: cólicos, flujo abundante, estrés...")

        # Preview de duración
        if tiene_fin and nueva_fin:
            dur_preview = (nueva_fin - nueva_inicio).days
            st.info(f"📌 Duración del período: **{dur_preview} días**")

        if st.button("💾 Guardar ciclo", type="primary", use_container_width=True):
            try:
                ws.append_row([
                    str(nueva_inicio),
                    str(nueva_fin) if nueva_fin else "",
                    notas_c.strip()
                ])
                st.success("✅ Ciclo registrado.")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    # ── Carga masiva de histórico ─────────────────────────────────────────
    with st.expander("📦 Ingresar múltiples ciclos históricos de una vez"):
        st.caption("Ingresa fechas de inicio de ciclos pasados separadas por comas o una por línea. Si no conoces las fechas exactas de fin, las dejamos en blanco.")
        st.markdown("**Formato:** `DD/MM/AAAA` — una fecha por línea o separadas por coma")

        fechas_texto = st.text_area(
            "Fechas de inicio de períodos anteriores",
            placeholder="15/01/2025\n12/02/2025\n11/03/2025\n09/04/2025",
            height=120
        )

        if st.button("📥 Importar fechas", type="secondary"):
            if fechas_texto.strip():
                lineas = [l.strip() for l in fechas_texto.replace(",", "\n").split("\n") if l.strip()]
                exitosos, errores = 0, []
                for linea in lineas:
                    try:
                        for fmt in ["%d/%m/%Y", "%Y-%m-%d", "%m/%d/%Y"]:
                            try:
                                f = pd.to_datetime(linea, format=fmt).date()
                                break
                            except Exception:
                                continue
                        ws.append_row([str(f), "", "Importado históricamente"])
                        exitosos += 1
                    except Exception:
                        errores.append(linea)

                if exitosos:
                    st.success(f"✅ {exitosos} ciclo(s) importado(s).")
                if errores:
                    st.warning(f"⚠️ No se pudieron importar: {', '.join(errores)}")
                if exitosos:
                    st.rerun()
            else:
                st.warning("Ingresa al menos una fecha.")

    # ── Guía científica ───────────────────────────────────────────────────
    st.divider()
    st.subheader("📖 Guía científica de las 4 fases")
    for nombre, info in FASES.items():
        ini, fin = info["rango"]
        with st.expander(f"{info['emoji']} **{nombre}** — Días {ini}–{fin}"):
            st.markdown(f"**{info['resumen']}**")
            st.markdown(f"🔬 {info['hormonas']}")
            st.markdown(f"🏋️ **Entrenamiento:** {info['entrenamiento']}")
            st.markdown(f"🥗 **Nutrición:** {info['nutricion']}")
