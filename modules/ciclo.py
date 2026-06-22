import streamlit as st
import pandas as pd
from datetime import date, timedelta

import utils.estado as estado
from utils.sheets import get_worksheet, leer_df_usuario, guardar_fila_usuario
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


def calcular_inicio_ciclo_actual(ultimo_registrado: date, dur: int) -> date:
    """
    Proyecta hacia adelante desde el último ciclo REGISTRADO para encontrar
    el inicio del ciclo ACTUAL (el más reciente antes de hoy o igual a hoy).
    No rellena ni muestra ciclos del pasado — solo encuentra el ancla actual.
    """
    hoy = date.today()
    if ultimo_registrado >= hoy:
        return ultimo_registrado
    dias = (hoy - ultimo_registrado).days
    ciclos_completos = dias // dur
    return ultimo_registrado + timedelta(days=dur * ciclos_completos)


def calcular_fase(inicio_ciclo_actual: date, dur: int) -> dict | None:
    """Calcula la fase basada en cuántos días han pasado desde el inicio del ciclo actual."""
    dia = (date.today() - inicio_ciclo_actual).days + 1
    if dia < 1 or dia > dur:
        dia = 1
    for nombre, info in FASES.items():
        ini, fin = info["rango"]
        fin_real = fin if nombre != "Lútea" else dur
        if ini <= dia <= fin_real:
            return {**info, "nombre": nombre, "dia": dia, "restantes": fin_real - dia + 1}
    return {**FASES["Lútea"], "nombre": "Lútea", "dia": dia, "restantes": max(dur - dia + 1, 0)}


def calcular_proximos(inicio_ciclo_actual: date, dur: int, n: int = 4) -> list[date]:
    """
    Proyecta los próximos N ciclos hacia el FUTURO desde el ciclo actual.
    Siempre son fechas futuras — no toca el pasado.
    """
    return [inicio_ciclo_actual + timedelta(days=dur * i) for i in range(1, n + 1)]


def preparar_df(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    df = df.copy()
    # Compatibilidad con columna antigua "duracion_dias"
    if "duracion_dias" in df.columns and "fecha_fin" not in df.columns:
        df = df.rename(columns={"duracion_dias": "fecha_fin"})
    if "fecha_fin" not in df.columns:
        df["fecha_fin"] = ""

    df["fecha_inicio"] = pd.to_datetime(df["fecha_inicio"], errors="coerce").dt.date
    df["fecha_fin"]    = pd.to_datetime(df["fecha_fin"],    errors="coerce").dt.date
    df = df.dropna(subset=["fecha_inicio"]).sort_values("fecha_inicio").reset_index(drop=True)

    # Duración del período: incluye día inicio y día fin (fin - inicio + 1)
    df["días período"] = df.apply(
        lambda r: (r["fecha_fin"] - r["fecha_inicio"]).days + 1
        if pd.notna(r["fecha_fin"]) else "—", axis=1
    )

    # Duración del ciclo: días entre inicio de un ciclo y el siguiente
    ciclos = ["—"]
    for i in range(1, len(df)):
        ciclos.append((df.iloc[i]["fecha_inicio"] - df.iloc[i-1]["fecha_inicio"]).days)
    df["días ciclo"] = ciclos

    return df


def mostrar():
    estado.cargar_perfil()
    st.title("🌙 Ciclo Menstrual & Entrenamiento")
    st.caption("Los datos históricos calculan tu promedio personal. Las predicciones siempre apuntan al futuro.")
    st.divider()

    try:
        ws     = get_worksheet("ciclo")
        uid    = estado.get("user_id", "")
        df_raw = leer_df_usuario("ciclo", uid)
    except Exception as e:
        st.error(f"Error conectando: {e}")
        return

    df    = preparar_df(df_raw)
    tiene = not df.empty

    # ── Calcular promedios del historial ──────────────────────────────────
    dur_prom_ciclo   = 28
    dur_prom_periodo = 5

    if tiene:
        ciclos_reales = [c for c in df["días ciclo"] if isinstance(c, int) and c > 0]
        if ciclos_reales:
            dur_prom_ciclo = round(sum(ciclos_reales) / len(ciclos_reales))

        periodos_reales = [p for p in df["días período"] if isinstance(p, int) and p > 0]
        if periodos_reales:
            dur_prom_periodo = round(sum(periodos_reales) / len(periodos_reales))

        # Inicio del ciclo actual (proyectado desde el último registrado)
        inicio_ciclo_actual = calcular_inicio_ciclo_actual(
            df.iloc[-1]["fecha_inicio"], dur_prom_ciclo
        )

    # ── Fase actual ───────────────────────────────────────────────────────
    if tiene:
        fase = calcular_fase(inicio_ciclo_actual, dur_prom_ciclo)

        if fase:
            st.subheader("📍 Tu fase actual")
            col_card, col_info = st.columns([1, 2], gap="large")

            with col_card:
                st.markdown(f"""
                <div style="background:{fase['color']};border-radius:16px;padding:28px;text-align:center;">
                    <div style="font-size:52px">{fase['emoji']}</div>
                    <div style="font-size:24px;font-weight:700;margin:10px 0">{fase['nombre']}</div>
                    <div style="color:#374151">Día <b>{fase['dia']}</b> de {dur_prom_ciclo}</div>
                    <div style="margin-top:8px;font-size:13px;color:#6b7280">{fase['restantes']} días restantes en esta fase</div>
                    <div style="margin-top:8px;font-size:12px;color:#9ca3af">Ciclo actual desde: {inicio_ciclo_actual.strftime('%d %b')}</div>
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
                  help="Calculado desde tus ciclos históricos registrados")
        e2.metric("Duración promedio del período",  f"{dur_prom_periodo} días",
                  help="Promedio de días de sangrado registrados")
        e3.metric("Ciclos en historial", len(df))

        st.divider()

        # ── Predicciones (siempre futuras) ────────────────────────────────
        st.subheader("📅 Próximos ciclos")
        st.caption(f"Proyección a futuro basada en tu promedio personal de **{dur_prom_ciclo} días**")

        proximos = calcular_proximos(inicio_ciclo_actual, dur_prom_ciclo)
        cols = st.columns(4)
        for col, fp in zip(cols, proximos):
            dias_falta = (fp - date.today()).days
            label = "¡Hoy!" if dias_falta == 0 else f"En {dias_falta} días"
            col.metric(fp.strftime("%d %b %Y"), label)

        st.divider()

        # ── Historial ─────────────────────────────────────────────────────
        st.subheader("📋 Historial registrado")
        df_show = df[["fecha_inicio","fecha_fin","días período","días ciclo","notas"]].copy()
        df_show["fecha_inicio"] = df_show["fecha_inicio"].astype(str)
        df_show["fecha_fin"]    = df_show["fecha_fin"].apply(
            lambda x: str(x) if pd.notna(x) and x != "" else "En curso"
        )
        st.dataframe(df_show.iloc[::-1].reset_index(drop=True), use_container_width=True, hide_index=True)
        st.divider()
        seccion_eliminar("ciclo", df_show, "registros de ciclo")

    else:
        st.info("📋 Registra al menos 2-3 ciclos históricos para ver tu fase actual y pronósticos personalizados.")

    # ── Registrar ciclo ───────────────────────────────────────────────────
    st.divider()
    with st.expander("➕ Registrar ciclo", expanded=not tiene):
        st.caption("Puedes ingresar ciclos pasados. Con más datos, el pronóstico será más preciso.")
        c1, c2 = st.columns(2)
        with c1:
            nueva_inicio = st.date_input("📅 Fecha de INICIO", value=date.today(),
                                          max_value=date.today(), key="ci_inicio")
        with c2:
            tiene_fin = st.checkbox("¿Ya terminó el período?", value=True)
            if tiene_fin:
                valor_fin = min(nueva_inicio + timedelta(days=4), date.today())
                nueva_fin = st.date_input("📅 Fecha de FIN", value=valor_fin,
                                           min_value=nueva_inicio, max_value=date.today(), key="ci_fin")
                dur_p = (nueva_fin - nueva_inicio).days + 1
                st.info(f"📌 Duración: **{dur_p} días**")
            else:
                nueva_fin = None

        notas_c = st.text_input("Notas", placeholder="Ej: cólicos, flujo abundante, estrés...")

        if st.button("💾 Guardar ciclo", type="primary", use_container_width=True):
            try:
                guardar_fila_usuario("ciclo", [str(nueva_inicio), str(nueva_fin) if nueva_fin else "", notas_c.strip()], uid)
                st.success("✅ Ciclo registrado.")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    # ── Carga masiva de histórico ─────────────────────────────────────────
    with st.expander("📦 Importar ciclos históricos (múltiples a la vez)"):
        st.caption("Ingresa fechas de inicio de períodos anteriores — una por línea en formato `DD/MM/AAAA`.")
        fechas_texto = st.text_area("Fechas de inicio",
            placeholder="01/01/2026\n30/01/2026\n27/02/2026\n27/03/2026", height=120)
        if st.button("📥 Importar", type="secondary"):
            if fechas_texto.strip():
                lineas = [l.strip() for l in fechas_texto.replace(",", "\n").split("\n") if l.strip()]
                ok, err = 0, []
                for linea in lineas:
                    parsed = None
                    for fmt in ["%d/%m/%Y", "%Y-%m-%d", "%m/%d/%Y"]:
                        try:
                            parsed = pd.to_datetime(linea, format=fmt).date()
                            break
                        except Exception:
                            continue
                    if parsed:
                        try:
                            guardar_fila_usuario("ciclo", [str(parsed), "", "Importado"], uid)
                            ok += 1
                        except Exception:
                            err.append(linea)
                    else:
                        err.append(linea)
                if ok:
                    st.success(f"✅ {ok} ciclo(s) importado(s).")
                if err:
                    st.warning(f"⚠️ No se pudieron importar: {', '.join(err)}")
                if ok:
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
