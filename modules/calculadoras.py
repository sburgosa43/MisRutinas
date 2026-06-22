import streamlit as st
import math

# ──────────────────────────────────────────────────────────────────────────────
# CONSTANTES
# ──────────────────────────────────────────────────────────────────────────────
LBS_A_KG = 0.453592
PULGADAS_A_CM = 2.54


# ──────────────────────────────────────────────────────────────────────────────
# FUNCIONES CIENTÍFICAS
# ──────────────────────────────────────────────────────────────────────────────

def calcular_1rm(peso_lbs: float, reps: int) -> dict:
    """Fórmulas de Epley, Brzycki y O'Conner para estimar 1RM."""
    p = peso_lbs
    r = reps
    return {
        "Epley":    round(p * (1 + r / 30), 1),
        "Brzycki":  round(p * (36 / (37 - r)), 1),
        "O'Conner": round(p * (1 + r * 0.025), 1),
        "Promedio": round((p*(1+r/30) + p*(36/(37-r)) + p*(1+r*0.025)) / 3, 1),
    }


def porcentajes_1rm(un_rm: float) -> dict:
    """Zonas de trabajo basadas en % del 1RM (NSCA)."""
    return {
        "Fuerza máxima (90-100%)":   f"{round(un_rm * 0.90, 1)} – {round(un_rm, 1)} lbs  |  1-3 reps",
        "Fuerza (80-90%)":           f"{round(un_rm * 0.80, 1)} – {round(un_rm * 0.90, 1)} lbs  |  3-5 reps",
        "Hipertrofia (65-80%)":      f"{round(un_rm * 0.65, 1)} – {round(un_rm * 0.80, 1)} lbs  |  6-12 reps",
        "Resistencia muscular (<65%)": f"< {round(un_rm * 0.65, 1)} lbs  |  12+ reps",
    }


def calcular_tdee(peso_lbs: float, altura_cm: float, edad: int, objetivo: str) -> dict:
    """
    BMR con Mifflin-St Jeor (ACSM) para mujer.
    Multiplicadores de actividad estándar.
    """
    peso_kg = peso_lbs * LBS_A_KG
    bmr = (10 * peso_kg) + (6.25 * altura_cm) - (5 * edad) - 161
    niveles = {
        "Sedentaria (sin ejercicio)":           round(bmr * 1.2),
        "Ligera (1-2 días/semana)":             round(bmr * 1.375),
        "Moderada (3-5 días/semana) ✅":         round(bmr * 1.55),
        "Alta (6-7 días/semana)":               round(bmr * 1.725),
        "Muy alta (atleta / trabajo físico)":   round(bmr * 1.9),
    }
    # Ajuste por objetivo
    ajustes = {
        "Pérdida de grasa (-500 kcal)":     -500,
        "Recomposición (mantenimiento)":      0,
        "Ganancia muscular (+200-300 kcal)": +250,
    }
    ajuste = ajustes.get(objetivo, 0)
    return {"bmr": round(bmr), "niveles": niveles, "ajuste": ajuste, "objetivo": objetivo}


def calcular_proteina(peso_lbs: float, objetivo: str) -> dict:
    """
    Recomendaciones de proteína basadas en Schoenfeld & Morton (2018).
    Rango: 1.6-2.2 g/kg para hipertrofia.
    """
    peso_kg = peso_lbs * LBS_A_KG
    rangos = {
        "Pérdida de grasa":    (2.0, 2.4),
        "Recomposición":       (1.8, 2.2),
        "Ganancia muscular":   (1.6, 2.0),
    }
    min_g, max_g = rangos.get(objetivo, (1.6, 2.2))
    return {
        "min_g_dia": round(peso_kg * min_g),
        "max_g_dia": round(peso_kg * max_g),
        "min_g_kg":  min_g,
        "max_g_kg":  max_g,
    }


def calcular_grasa_navy(cintura_cm: float, cadera_cm: float, cuello_cm: float, altura_cm: float) -> float:
    """
    Fórmula del US Navy para % grasa corporal (mujeres).
    Referencia: Hodgdon & Beckett (1984).
    """
    try:
        log_val = math.log10(cintura_cm + cadera_cm - cuello_cm) - math.log10(altura_cm)
        return round(163.205 * log_val - 97.684 * math.log10(altura_cm) - 78.387, 1)
    except Exception:
        return None


def clasificar_grasa_mujer(pct: float) -> tuple[str, str]:
    if pct < 14:   return "Atleta élite", "#6366f1"
    elif pct < 21: return "Atleta / Fitness ✅", "#10b981"
    elif pct < 25: return "Promedio", "#f59e0b"
    elif pct < 32: return "Por encima del promedio", "#f97316"
    else:          return "Alto riesgo metabólico", "#ef4444"


# ──────────────────────────────────────────────────────────────────────────────
# MÓDULO PRINCIPAL
# ──────────────────────────────────────────────────────────────────────────────

def mostrar():
    st.title("⚡ Calculadoras Científicas")
    st.caption("Basadas en evidencia: NSCA, ACSM, Schoenfeld, Brzycki, Mifflin-St Jeor.")
    st.divider()

    tab1, tab2, tab3, tab4 = st.tabs([
        "💪 1RM & Zonas",
        "🔥 TDEE & Calorías",
        "🥩 Proteína",
        "📐 % Grasa Corporal",
    ])

    # ── TAB 1: 1RM ────────────────────────────────────────────────────────
    with tab1:
        st.subheader("Estimador de 1RM")
        st.caption("¿Cuánto puedes levantar una sola vez? Calcula sin arriesgar lesiones.")

        c1, c2 = st.columns(2)
        with c1:
            peso_ej  = st.number_input("Peso levantado (lbs)", min_value=5.0, max_value=500.0, value=50.0, step=2.5)
        with c2:
            reps_ej  = st.number_input("Repeticiones realizadas", min_value=1, max_value=20, value=8, step=1)

        if reps_ej == 1:
            st.info("Con 1 repetición, el peso ingresado **ya es tu 1RM**.")
        else:
            resultados = calcular_1rm(peso_ej, reps_ej)
            st.divider()

            r1, r2, r3, r4 = st.columns(4)
            r1.metric("Epley",    f"{resultados['Epley']} lbs")
            r2.metric("Brzycki",  f"{resultados['Brzycki']} lbs")
            r3.metric("O'Conner", f"{resultados["O'Conner"]} lbs")
            r4.metric("🎯 Promedio", f"{resultados['Promedio']} lbs")

            st.divider()
            st.subheader("Zonas de trabajo recomendadas")
            st.caption("Basado en tu 1RM estimado (promedio)")
            zonas = porcentajes_1rm(resultados["Promedio"])
            for zona, valor in zonas.items():
                st.markdown(f"**{zona}:** {valor}")

    # ── TAB 2: TDEE ───────────────────────────────────────────────────────
    with tab2:
        st.subheader("Gasto Calórico Total (TDEE)")
        st.caption("Mifflin-St Jeor — el más preciso según ACSM para mujeres.")

        c1, c2, c3 = st.columns(3)
        with c1:
            peso_t  = st.number_input("Peso (lbs)", min_value=66.0, max_value=330.0, value=132.0, step=1.0, key="tdee_peso")
        with c2:
            altura_t = st.number_input("Altura (cm)", min_value=140.0, max_value=200.0, value=165.0, step=0.5, key="tdee_altura")
        with c3:
            edad_t  = st.number_input("Edad", min_value=16, max_value=80, value=28, step=1, key="tdee_edad")

        objetivo_t = st.selectbox("Objetivo", [
            "Pérdida de grasa (-500 kcal)",
            "Recomposición (mantenimiento)",
            "Ganancia muscular (+200-300 kcal)",
        ])

        resultado_t = calcular_tdee(peso_t, altura_t, edad_t, objetivo_t)
        st.divider()
        st.metric("🔬 Metabolismo basal (BMR)", f"{resultado_t['bmr']} kcal/día",
                  help="Calorías que quemas sin hacer nada — solo existiendo.")

        st.subheader("Selecciona tu nivel de actividad:")
        for nivel, cals in resultado_t["niveles"].items():
            ajuste = resultado_t["ajuste"]
            total  = cals + ajuste
            label  = f"**{nivel}** → {cals} kcal base"
            if ajuste != 0:
                label += f" → **{total} kcal con ajuste por objetivo**"
            st.markdown(label)

    # ── TAB 3: PROTEÍNA ───────────────────────────────────────────────────
    with tab3:
        st.subheader("Recomendación de Proteína")
        st.caption("Basado en Schoenfeld & Morton 2018 — el paper más citado sobre proteína y músculo.")

        c1, c2 = st.columns(2)
        with c1:
            peso_p = st.number_input("Peso (lbs)", min_value=66.0, max_value=330.0, value=132.0, step=1.0, key="prot_peso")
        with c2:
            obj_p  = st.selectbox("Objetivo", ["Pérdida de grasa", "Recomposición", "Ganancia muscular"])

        res_p = calcular_proteina(peso_p, obj_p)
        st.divider()

        p1, p2 = st.columns(2)
        p1.metric("Mínimo diario", f"{res_p['min_g_dia']} g",
                  f"{res_p['min_g_kg']} g por kg de peso")
        p2.metric("Óptimo diario", f"{res_p['max_g_dia']} g",
                  f"{res_p['max_g_kg']} g por kg de peso")

        st.info(f"💡 Apunta a **{res_p['min_g_dia']}–{res_p['max_g_dia']}g de proteína por día** "
                f"distribuidos en 3-5 comidas de {round(res_p['min_g_dia']/4)}–{round(res_p['max_g_dia']/4)}g cada una.")

    # ── TAB 4: % GRASA ────────────────────────────────────────────────────
    with tab4:
        st.subheader("% Grasa Corporal — Método US Navy")
        st.caption("Precisión del 95% comparado con DEXA. Solo necesitas una cinta métrica.")

        c1, c2 = st.columns(2)
        with c1:
            cintura_g  = st.number_input("Cintura (cm)", min_value=40.0, max_value=150.0, value=75.0, step=0.5, key="g_cintura")
            cadera_g   = st.number_input("Cadera (cm)",  min_value=50.0, max_value=160.0, value=95.0, step=0.5, key="g_cadera")
        with c2:
            cuello_g   = st.number_input("Cuello (cm)",  min_value=25.0, max_value=60.0,  value=33.0, step=0.5, key="g_cuello")
            altura_g   = st.number_input("Altura (cm)",  min_value=140.0, max_value=200.0, value=165.0, step=0.5, key="g_altura")

        pct_grasa = calcular_grasa_navy(cintura_g, cadera_g, cuello_g, altura_g)

        if pct_grasa and pct_grasa > 0:
            cat_grasa, _ = clasificar_grasa_mujer(pct_grasa)
            st.divider()
            st.metric("📐 % Grasa Corporal Estimado", f"{pct_grasa}%", cat_grasa)

            # Masa grasa vs masa magra
            peso_ref = st.number_input("Tu peso actual (lbs) para desglose:", min_value=66.0, value=132.0, step=1.0)
            peso_kg_ref = peso_ref * LBS_A_KG
            masa_grasa  = round(peso_kg_ref * pct_grasa / 100, 1)
            masa_magra  = round(peso_kg_ref - masa_grasa, 1)
            g1, g2 = st.columns(2)
            g1.metric("🏋️ Masa magra", f"{round(masa_magra / LBS_A_KG, 1)} lbs", f"{masa_magra} kg")
            g2.metric("🧈 Masa grasa", f"{round(masa_grasa / LBS_A_KG, 1)} lbs", f"{masa_grasa} kg")
        else:
            st.warning("Revisa los valores ingresados.")
