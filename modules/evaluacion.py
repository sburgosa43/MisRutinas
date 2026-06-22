import streamlit as st
import pandas as pd
from datetime import date
from utils.sheets import get_worksheet

PAR_Q = [
    "¿Tu médico alguna vez te dijo que tienes una condición cardíaca y que solo debes hacer ejercicio bajo supervisión médica?",
    "¿Sientes dolor en el pecho cuando realizas actividad física?",
    "En el último mes, ¿has tenido dolor en el pecho sin estar haciendo ejercicio?",
    "¿Pierdes el equilibrio por mareos, o has perdido el conocimiento alguna vez?",
    "¿Tienes algún problema de huesos o articulaciones que podría empeorar con el ejercicio?",
    "¿Tu médico te receta actualmente medicamentos para la presión arterial o el corazón?",
    "¿Conoces alguna otra razón por la que no deberías hacer actividad física?",
]


def obtener_perfil() -> dict | None:
    """Carga el perfil más reciente desde Google Sheets. Usado por otros módulos."""
    try:
        ws  = get_worksheet("evaluacion")
        data = ws.get_all_records()
        if not data:
            return None
        return pd.DataFrame(data).iloc[-1].to_dict()
    except Exception:
        return None


def generar_programa(dias: int, nivel: str, equipo: str, objetivo: str) -> str:
    nivel_s = "principiante" if "Principiante" in nivel else ("intermedio" if "Intermedio" in nivel else "avanzado")
    if dias <= 3:
        return "Full Body — 3 días/semana"
    elif dias <= 4:
        return "Upper / Lower Split — 4 días/semana"
    elif nivel_s == "principiante":
        return "Full Body — 3-4 días/semana"
    else:
        return "Push / Pull / Legs (PPL) — 5-6 días/semana"


def mostrar():
    st.title("🧬 Evaluación Inicial")
    st.caption("Completa esta evaluación una vez. La usamos para personalizar tu programa, tus rutinas y las recomendaciones del Coach IA.")
    st.divider()

    # Cargar evaluación previa si existe
    perfil_previo = obtener_perfil()
    if perfil_previo:
        with st.expander("📋 Ver tu última evaluación", expanded=False):
            st.dataframe(pd.DataFrame([perfil_previo]), use_container_width=True, hide_index=True)
            st.caption(f"Última evaluación: {perfil_previo.get('fecha', '—')}")

    st.subheader("Completa las 4 secciones y guarda al final")
    tab1, tab2, tab3, tab4 = st.tabs(["🏥 Seguridad (PAR-Q)", "🎯 Objetivo & Nivel", "📅 Horario & Equipo", "🩹 Lesiones & Estilo de vida"])

    # ── PAR-Q ────────────────────────────────────────────────────────────
    with tab1:
        st.subheader("Cuestionario de Aptitud Física — PAR-Q")
        st.caption("Si respondes SÍ a cualquier pregunta, consulta con tu médico antes de iniciar. Es por tu seguridad.")
        respuestas_parq = []
        for i, p in enumerate(PAR_Q):
            r = st.radio(f"**{i+1}.** {p}", ["No ✅", "Sí ⚠️"], key=f"parq_{i}", horizontal=True)
            respuestas_parq.append("Sí" in r)
        if any(respuestas_parq):
            st.warning("⚠️ Respondiste SÍ a una o más preguntas. Recomendamos consultar con tu médico antes de iniciar.")
        else:
            st.success("✅ Sin contraindicaciones. ¡Puedes iniciar con seguridad!")

    # ── Objetivo & Nivel ─────────────────────────────────────────────────
    with tab2:
        st.subheader("Tu objetivo principal")
        objetivo = st.selectbox("¿Qué quieres lograr?", [
            "Recomposición corporal (perder grasa y ganar músculo al mismo tiempo)",
            "Pérdida de grasa principalmente",
            "Ganancia de músculo e hipertrofia",
            "Mejorar salud general y bienestar",
            "Aumentar fuerza",
        ])

        zonas = st.multiselect("¿Qué zonas quieres priorizar?", [
            "Glúteos", "Piernas y muslos", "Abdomen y core",
            "Brazos", "Espalda", "Hombros", "Pecho"
        ])

        st.subheader("Tu nivel de experiencia")
        nivel = st.selectbox("¿Cuánto tiempo llevas entrenando?", [
            "Principiante — menos de 6 meses o regresando después de un descanso largo",
            "Intermedio — entre 6 meses y 2 años entrenando",
            "Avanzado — más de 2 años entrenando de forma consistente",
        ])

    # ── Horario & Equipo ─────────────────────────────────────────────────
    with tab3:
        st.subheader("Tu disponibilidad semanal")
        c1, c2 = st.columns(2)
        with c1:
            dias = st.slider("Días por semana que puedes entrenar", 2, 6, 3)
        with c2:
            duracion = st.selectbox("Duración por sesión", ["30 min", "45 min", "60 min", "90 min"])

        momento = st.selectbox("¿Cuándo prefieres entrenar?", [
            "Mañana temprano (6-9am)", "Mañana (9-12pm)",
            "Mediodía", "Tarde (4-7pm)", "Noche (después de 7pm)"
        ])

        st.subheader("Equipo disponible")
        equipo = st.selectbox("¿Con qué cuentas?", [
            "Solo peso corporal — sin equipo",
            "Equipo básico — mancuernas y/o bandas elásticas",
            "Equipo intermedio — mancuernas, barra, banco",
            "Acceso a gimnasio completo",
        ])

    # ── Lesiones & Estilo de vida ─────────────────────────────────────────
    with tab4:
        st.subheader("Historial de lesiones o limitaciones")
        lesiones = st.multiselect("¿Tienes alguna zona sensible o lesionada?", [
            "Ninguna", "Rodillas", "Espalda baja (lumbar)", "Espalda alta / hombros",
            "Cadera", "Tobillos / pies", "Cuello / cervical", "Muñecas / codos"
        ], default=["Ninguna"])
        detalle_lesiones = st.text_area("Detalla si tienes alguna limitación específica:",
                                         placeholder="Ej: dolor en rodilla derecha al bajar escaleras, hernia discal L4-L5...")

        st.subheader("Tu estilo de vida")
        c1, c2 = st.columns(2)
        with c1:
            horas_sueno  = st.slider("Horas de sueño por noche", 4, 10, 7)
            nivel_estres = st.slider("Nivel de estrés actual (1=bajo, 10=muy alto)", 1, 10, 5)
        with c2:
            trabajo_sedentario = st.radio("¿Tu trabajo es sedentario (escritorio)?", ["Sí", "No"], horizontal=True)
            agua = st.number_input("Litros de agua al día", min_value=0.5, max_value=5.0, value=1.5, step=0.5)

    st.divider()

    # ── Guardar ───────────────────────────────────────────────────────────
    if st.button("💾 Guardar Evaluación y Generar Perfil", type="primary", use_container_width=True):
        with st.spinner("Guardando..."):
            try:
                ws = get_worksheet("evaluacion")
                parq_res = "SÍ — consultar médico" if any(respuestas_parq) else "Apto sin restricciones"
                ws.append_row([
                    str(date.today()), parq_res,
                    objetivo, nivel,
                    ", ".join(zonas) if zonas else "General",
                    dias, duracion, momento, equipo,
                    ", ".join(lesiones), detalle_lesiones.strip(),
                    horas_sueno, nivel_estres,
                    trabajo_sedentario, agua,
                ])
                st.success("✅ Evaluación guardada.")
                st.balloons()

                # Perfil generado
                st.divider()
                st.subheader("🎯 Tu Perfil de Entrenamiento")
                programa = generar_programa(dias, nivel, equipo, objetivo)

                c1, c2, c3 = st.columns(3)
                c1.metric("Programa recomendado", programa)
                c2.metric("Frecuencia", f"{dias} días/semana")
                c3.metric("Duración sesión", duracion)

                zonas_str = ", ".join(zonas) if zonas else "Cuerpo completo"
                st.info(f"**Enfoque:** {zonas_str}")

                if lesiones and "Ninguna" not in lesiones:
                    st.warning(f"⚠️ Zonas a cuidar: {', '.join(l for l in lesiones if l != 'Ninguna')} — adaptaremos los ejercicios.")

                if horas_sueno < 6:
                    st.warning("😴 Duermes menos de 6 horas. El sueño es cuando el músculo crece — prioriza descansar más.")
                if nivel_estres >= 8:
                    st.warning("😓 Nivel de estrés alto. Incluiremos trabajo de movilidad y recuperación activa en tu programa.")

            except Exception as e:
                st.error(f"Error al guardar: {e}")
                st.exception(e)
