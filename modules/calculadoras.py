import streamlit as st
import math
import utils.estado as estado

LBS_A_KG = 0.453592

def mostrar():
    estado.cargar_perfil()
    st.title("⚡ Calculadoras Científicas")
    st.caption("NSCA · ACSM · Schoenfeld · Mifflin-St Jeor · US Navy")
    st.divider()

    # Valores del perfil del usuario como defaults
    peso_def  = estado.get("med_peso",   132.0)
    alt_def   = estado.get("med_altura", 165.0)
    edad_def  = estado.get("med_edad",   25)

    tab1, tab2, tab3, tab4 = st.tabs(["💪 1RM & Zonas","🔥 TDEE & Calorías","🥩 Proteína","📐 % Grasa"])

    with tab1:
        st.subheader("Estimador de 1RM")
        c1, c2 = st.columns(2)
        peso_ej = c1.number_input("Peso levantado (lbs)", 5.0, 500.0, 50.0, 2.5)
        reps_ej = c2.number_input("Repeticiones", 1, 20, 8, 1)
        if reps_ej > 1:
            epley  = round(peso_ej * (1 + reps_ej/30), 1)
            brz    = round(peso_ej * (36/(37-reps_ej)), 1)
            ocon   = round(peso_ej * (1 + reps_ej*0.025), 1)
            prom   = round((epley+brz+ocon)/3, 1)
            r1,r2,r3,r4 = st.columns(4)
            r1.metric("Epley", f"{epley} lbs")
            r2.metric("Brzycki", f"{brz} lbs")
            r3.metric("O'Conner", f"{ocon} lbs")
            r4.metric("🎯 Promedio", f"{prom} lbs")
            st.divider()
            st.subheader("Zonas de trabajo (NSCA)")
            zonas = {
                "Fuerza máxima (90-100%)": f"{round(prom*.9,1)}–{prom} lbs · 1-3 reps",
                "Fuerza (80-90%)":         f"{round(prom*.8,1)}–{round(prom*.9,1)} lbs · 3-5 reps",
                "Hipertrofia (65-80%)":    f"{round(prom*.65,1)}–{round(prom*.8,1)} lbs · 6-12 reps",
                "Resistencia (<65%)":      f"< {round(prom*.65,1)} lbs · 12+ reps",
            }
            for z, v in zonas.items():
                st.markdown(f"**{z}:** {v}")
        else:
            st.info("Con 1 repetición, ese peso ya es tu 1RM.")

    with tab2:
        st.subheader("TDEE — Gasto Calórico Total")
        st.caption("Mifflin-St Jeor — el más preciso según ACSM para mujeres.")
        c1,c2,c3 = st.columns(3)
        peso_t  = c1.number_input("Peso (lbs)", 66.0, 330.0, float(peso_def), 1.0, key="t_peso")
        alt_t   = c2.number_input("Altura (cm)", 140.0, 200.0, float(alt_def), 0.5, key="t_alt")
        edad_t  = c3.number_input("Edad", 16, 80, int(edad_def), 1, key="t_edad")
        obj_t   = st.selectbox("Objetivo", ["Pérdida de grasa (-500 kcal)","Recomposición (mantenimiento)","Ganancia muscular (+250 kcal)"])
        bmr = (10 * peso_t * LBS_A_KG) + (6.25 * alt_t) - (5 * int(edad_t)) - 161
        ajuste = -500 if "grasa" in obj_t else (250 if "muscular" in obj_t else 0)
        st.divider()
        st.metric("🔬 Metabolismo basal (BMR)", f"{round(bmr)} kcal/día")
        niveles = {"Sedentaria":1.2,"Ligera (1-2 días)":1.375,"Moderada (3-5 días) ✅":1.55,"Alta (6-7 días)":1.725,"Atleta":1.9}
        for n, mult in niveles.items():
            base = round(bmr*mult)
            total = base + ajuste
            extra = f" → **{total} kcal con ajuste**" if ajuste != 0 else ""
            st.markdown(f"**{n}** → {base} kcal{extra}")

    with tab3:
        st.subheader("Proteína óptima diaria")
        st.caption("Schoenfeld & Morton 2018 — el paper más citado sobre proteína y músculo.")
        c1,c2 = st.columns(2)
        peso_p = c1.number_input("Peso (lbs)", 66.0, 330.0, float(peso_def), 1.0, key="p_peso")
        obj_p  = c2.selectbox("Objetivo", ["Pérdida de grasa","Recomposición","Ganancia muscular"])
        rangos = {"Pérdida de grasa":(2.0,2.4),"Recomposición":(1.8,2.2),"Ganancia muscular":(1.6,2.0)}
        mn, mx = rangos[obj_p]
        kg = peso_p * LBS_A_KG
        st.divider()
        p1,p2 = st.columns(2)
        p1.metric("Mínimo diario", f"{round(kg*mn)}g", f"{mn}g/kg")
        p2.metric("Óptimo diario", f"{round(kg*mx)}g", f"{mx}g/kg")
        st.info(f"💡 Distribuye en 3-5 comidas de {round(kg*mn/4)}–{round(kg*mx/4)}g cada una.")

    with tab4:
        st.subheader("% Grasa Corporal — Método US Navy")
        st.caption("Precisión del 95% vs DEXA. Solo necesitas cinta métrica.")
        c1,c2 = st.columns(2)
        cin_g = c1.number_input("Cintura (cm)", 40.0, 150.0, estado.get("med_cintura",75.0), 0.5, key="g_cin")
        cad_g = c1.number_input("Cadera (cm)", 50.0, 160.0, estado.get("med_cadera",95.0), 0.5, key="g_cad")
        cue_g = c2.number_input("Cuello (cm)", 25.0, 60.0, 33.0, 0.5, key="g_cue")
        alt_g = c2.number_input("Altura (cm)", 140.0, 200.0, float(alt_def), 0.5, key="g_alt")
        try:
            pct = round(163.205*math.log10(cin_g+cad_g-cue_g) - 97.684*math.log10(alt_g) - 78.387, 1)
            if pct > 0:
                cats = [(14,"Atleta élite"),(21,"Fitness ✅"),(25,"Promedio"),(32,"Sobre promedio")]
                cat = next((c for v,c in cats if pct < v), "Alto riesgo metabólico")
                st.divider()
                st.metric("📐 % Grasa estimado", f"{pct}%", cat)
                peso_kg_r = float(peso_def) * LBS_A_KG
                mg = round(peso_kg_r * pct/100, 1)
                mm = round(peso_kg_r - mg, 1)
                g1,g2 = st.columns(2)
                g1.metric("🏋️ Masa magra", f"{round(mm/LBS_A_KG,1)} lbs", f"{mm} kg")
                g2.metric("🧈 Masa grasa", f"{round(mg/LBS_A_KG,1)} lbs", f"{mg} kg")
        except Exception:
            st.warning("Revisa los valores ingresados.")
