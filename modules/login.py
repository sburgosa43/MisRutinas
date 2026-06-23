import streamlit as st
import pandas as pd
from datetime import date

import utils.estado as estado
from utils.sheets import get_worksheet, leer_df_usuario, guardar_fila_usuario
from utils.ui_helpers import seccion_eliminar

PAR_Q = [
    "¿Tu médico alguna vez te dijo que tienes una condición cardíaca y que solo debes hacer ejercicio bajo supervisión médica?",
    "¿Sientes dolor en el pecho cuando realizas actividad física?",
    "En el último mes, ¿has tenido dolor en el pecho sin estar haciendo ejercicio?",
    "¿Pierdes el equilibrio por mareos, o has perdido el conocimiento alguna vez?",
    "¿Tienes algún problema de huesos o articulaciones que podría empeorar con el ejercicio?",
    "¿Tu médico te receta actualmente medicamentos para la presión arterial o el corazón?",
    "¿Conoces alguna otra razón por la que no deberías hacer actividad física?",
]

OBJETIVOS = [
    "Recomposición corporal (perder grasa y ganar músculo al mismo tiempo)",
    "Pérdida de grasa principalmente",
    "Ganancia de músculo e hipertrofia",
    "Mejorar salud general y bienestar",
    "Aumentar fuerza",
]

NIVELES = [
    "Principiante — menos de 6 meses o regresando después de un descanso largo",
    "Intermedio — entre 6 meses y 2 años entrenando",
    "Avanzado — más de 2 años entrenando de forma consistente",
]

EQUIPOS = [
    "Solo peso corporal — sin equipo",
    "Equipo básico — mancuernas y/o bandas elásticas",
    "Equipo intermedio — mancuernas, barra, banco",
    "Acceso a gimnasio completo",
]


def obtener_perfil(user_id: str) -> dict | None:
    try:
        df = leer_df_usuario("evaluacion", user_id)
        return df.iloc[-1].to_dict() if not df.empty else None
    except Exception:
        return None


def generar_programa(dias: int, nivel: str) -> tuple[str, str]:
    n = "avanzado" if "Avanzado" in nivel else ("intermedio" if "Intermedio" in nivel else "principiante")
    if dias <= 3:
        return "Full Body", "3 días/semana es ideal para Full Body — máximo estímulo por sesión."
    elif dias == 4:
        return "Upper / Lower Split", "4 días permite dividir tren superior e inferior, más volumen por grupo."
    else:
        prog = "Push / Pull / Legs (PPL)" if n != "principiante" else "Full Body avanzado"
        return prog, f"Con {dias} días y nivel {n}, puedes manejar más volumen total semanal."


def mostrar():
    estado.cargar_perfil()
    st.title("🧬 Evaluación Inicial")
    st.caption("Completa esta evaluación una vez. La usamos para personalizar todo: programa, rutinas y Coach IA.")
    st.divider()

    # Evaluación previa
    uid    = estado.get('user_id', '')
    perfil = obtener_perfil(uid)
    if perfil:
        with st.expander("📋 Ver tu última evaluación guardada", expanded=False):
            st.dataframe(pd.DataFrame([perfil]), use_container_width=True, hide_index=True)
            st.caption(f"Fecha: {perfil.get('fecha', '—')}")

    tab1, tab2, tab3, tab4 = st.tabs(["🏥 Seguridad PAR-Q", "🎯 Objetivo & Nivel", "📅 Horario & Equipo", "🩹 Lesiones & Estilo de vida"])

    with tab1:
        st.subheader("Cuestionario de Aptitud Física — PAR-Q")
        st.caption("Si respondes SÍ a alguna pregunta, consulta con tu médico antes de iniciar.")
        respuestas_parq = []
        for i, p in enumerate(PAR_Q):
            r = st.radio(f"**{i+1}.** {p}", ["No ✅", "Sí ⚠️"], key=f"parq_{i}", horizontal=True)
            respuestas_parq.append("Sí" in r)
        if any(respuestas_parq):
            st.warning("⚠️ Recomendamos consultar con tu médico antes de iniciar el programa.")
        else:
            st.success("✅ Sin contraindicaciones. ¡Puedes iniciar con seguridad!")

    with tab2:
        obj_idx = OBJETIVOS.index(estado.get("eval_objetivo")) if estado.get("eval_objetivo") in OBJETIVOS else 0
        objetivo = st.selectbox("¿Qué quieres lograr?", OBJETIVOS, index=obj_idx)
        zonas = st.multiselect("¿Qué zonas quieres priorizar?",
                               ["Glúteos","Piernas y muslos","Abdomen y core","Brazos","Espalda","Hombros","Pecho"])
        niv_idx = NIVELES.index(estado.get("eval_nivel")) if estado.get("eval_nivel") in NIVELES else 0
        nivel = st.selectbox("¿Cuánto tiempo llevas entrenando?", NIVELES, index=niv_idx)

    with tab3:
        c1, c2 = st.columns(2)
        with c1:
            dias = st.slider("Días por semana que puedes entrenar", 2, 6, estado.get("eval_dias", 3))
        with c2:
            dur_opts = ["30 min","45 min","60 min","90 min"]
            dur_idx = dur_opts.index(estado.get("eval_duracion")) if estado.get("eval_duracion") in dur_opts else 2
            duracion = st.selectbox("Duración por sesión", dur_opts, index=dur_idx)
        momento = st.selectbox("¿Cuándo prefieres entrenar?",
                               ["Mañana temprano (6-9am)","Mañana (9-12pm)","Mediodía","Tarde (4-7pm)","Noche"])
        eq_idx = EQUIPOS.index(estado.get("eval_equipo")) if estado.get("eval_equipo") in EQUIPOS else 0
        equipo = st.selectbox("¿Con qué equipo cuentas?", EQUIPOS, index=eq_idx)

    with tab4:
        lesiones = st.multiselect("¿Tienes alguna zona sensible o lesionada?",
                                  ["Ninguna","Rodillas","Espalda baja (lumbar)","Espalda alta / hombros",
                                   "Cadera","Tobillos / pies","Cuello / cervical","Muñecas / codos"],
                                  default=["Ninguna"])
        detalle = st.text_area("Detalla cualquier limitación específica:",
                               placeholder="Ej: dolor en rodilla derecha al bajar escaleras...")
        c1, c2 = st.columns(2)
        with c1:
            horas_sueno  = st.slider("Horas de sueño por noche", 4, 10, 7)
            nivel_estres = st.slider("Nivel de estrés (1=bajo, 10=alto)", 1, 10, 5)
        with c2:
            trabajo_sed = st.radio("¿Trabajo sedentario?", ["Sí","No"], horizontal=True)
            agua = st.number_input("Litros de agua/día", 0.5, 5.0, 1.5, 0.5)

    st.divider()

    if st.button("💾 Guardar Evaluación y Generar Perfil", type="primary", use_container_width=True):
        with st.spinner("Guardando..."):
            try:
                parq = "SÍ — consultar médico" if any(respuestas_parq) else "Apto sin restricciones"
                guardar_fila_usuario("evaluacion", [
                    str(date.today()), parq, objetivo, nivel,
                    ", ".join(zonas) if zonas else "General",
                    dias, duracion, momento, equipo,
                    ", ".join(lesiones), detalle.strip(),
                    horas_sueno, nivel_estres, trabajo_sed, agua,
                ], uid)
                estado.set("eval_objetivo", objetivo)
                estado.set("eval_nivel",    nivel)
                estado.set("eval_dias",     dias)
                estado.set("eval_equipo",   equipo)
                estado.set("eval_lesiones", ", ".join(lesiones))
                estado.set("eval_duracion", duracion)
                st.success("✅ Evaluación guardada.")
                st.balloons()

                st.divider()
                st.subheader("🎯 Tu Perfil de Entrenamiento")
                prog, razon = generar_programa(dias, nivel)
                c1, c2, c3 = st.columns(3)
                c1.metric("Programa", prog)
                c2.metric("Frecuencia", f"{dias} días/semana")
                c3.metric("Sesión", duracion)
                st.info(f"**¿Por qué este programa?** {razon}")
                if zonas:
                    st.info(f"**Zonas prioritarias:** {', '.join(zonas)}")
                les_reales = [l for l in lesiones if l != "Ninguna"]
                if les_reales:
                    st.warning(f"⚠️ Zonas a cuidar: {', '.join(les_reales)} — adaptaremos los ejercicios.")
                if horas_sueno < 6:
                    st.warning("😴 Menos de 6h de sueño. Recuerda: el músculo crece mientras descansas.")
                if nivel_estres >= 8:
                    st.warning("😓 Estrés alto. Incluiremos recuperación activa y movilidad en tu programa.")
            except Exception as e:
                st.error(f"Error: {e}")
                st.exception(e)

    # ── Eliminar registros ────────────────────────────────────────────────
    st.divider()
    try:
        df = leer_df_usuario("evaluacion", uid)
        if not df.empty:
            seccion_eliminar("evaluacion", df, "evaluaciones anteriores")
    except Exception:
        pass
