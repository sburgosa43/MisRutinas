import streamlit as st
import pandas as pd
from datetime import date

import utils.estado as estado
from utils.sheets import leer_df_usuario, guardar_fila_usuario
from data.coaches import COACHES, coaches_por_objetivo

# ══════════════════════════════════════════════════════════════════════════════
# BASE DE EJERCICIOS
# ══════════════════════════════════════════════════════════════════════════════
EJERCICIOS_BASE = [
    # ── GLÚTEOS ──────────────────────────────────────────────────────────────
    {"id":"g01","nombre":"Hip Thrust con barra","grupo":"Glúteos",
     "descripcion":"El ejercicio #1 para glúteos según la ciencia (Contreras 2015). Espaldas en banco, barra sobre caderas, empuja con talones apretando glúteos en la cima. Pausa 1 seg arriba.",
     "equipo":["barra","banco"],"dificultad":"intermedio",
     "objetivo":["recomposicion","hipertrofia","fuerza"],
     "lesiones_evitar":[],"coach":"Bret Contreras",
     "url":"https://www.youtube.com/results?search_query=bret+contreras+hip+thrust+tutorial"},
    {"id":"g02","nombre":"Hip Thrust con mancuerna","grupo":"Glúteos",
     "descripcion":"Versión accesible del Hip Thrust. Ideal para casa con equipo básico. Mismo patrón de movimiento, mismos resultados.",
     "equipo":["mancuernas","banco"],"dificultad":"principiante",
     "objetivo":["recomposicion","hipertrofia"],"lesiones_evitar":[],
     "coach":"Heather Robertson","url":"https://www.youtube.com/results?search_query=heather+robertson+dumbbell+hip+thrust+tutorial"},
    {"id":"g03","nombre":"Glute Bridge (peso corporal)","grupo":"Glúteos",
     "descripcion":"Sin equipo. Acuéstate boca arriba, pies apoyados, eleva caderas apretando glúteos. Progresa a una sola pierna.",
     "equipo":["ninguno","mat"],"dificultad":"principiante",
     "objetivo":["recomposicion","salud"],"lesiones_evitar":[],
     "coach":"Heather Robertson","url":"https://www.youtube.com/results?search_query=bret+contreras+glute+bridge+tutorial"},
    {"id":"g04","nombre":"Bulgarian Split Squat","grupo":"Glúteos",
     "descripcion":"Pie trasero en banco, pie delantero al frente. Baja rodilla al suelo. Excelente para glúteos y cuádriceps. Añade mancuernas para progresar.",
     "equipo":["ninguno","banco","mancuernas"],"dificultad":"intermedio",
     "objetivo":["recomposicion","hipertrofia","fuerza"],"lesiones_evitar":["Rodillas"],
     "coach":"Jeff Nippard","url":"https://www.youtube.com/results?search_query=jeff+nippard+bulgarian+split+squat+tutorial"},
    {"id":"g05","nombre":"Donkey Kick","grupo":"Glúteos",
     "descripcion":"En cuadrupedia, lleva un talón al techo contrayendo el glúteo. Controla el descenso. Añade tobillera con peso para progresar.",
     "equipo":["ninguno","mat"],"dificultad":"principiante",
     "objetivo":["recomposicion","salud"],"lesiones_evitar":[],
     "coach":"Sydney Cummings","url":"https://www.youtube.com/results?search_query=heather+robertson+donkey+kick+glute+tutorial"},
    {"id":"g06","nombre":"Cable Kickback","grupo":"Glúteos",
     "descripcion":"En polea baja, lleva el pie hacia atrás y arriba contrayendo el glúteo. Mantén el core activo y evita arquear la espalda.",
     "equipo":["maquina_cables"],"dificultad":"principiante",
     "objetivo":["recomposicion","hipertrofia"],"lesiones_evitar":[],
     "coach":"Stephanie Sanzo","url":"https://www.youtube.com/results?search_query=bret+contreras+cable+kickback+glutes+tutorial"},
    {"id":"g07","nombre":"Clamshell con banda","grupo":"Glúteos",
     "descripcion":"Acostada de lado, rodillas dobladas, abre la pierna superior como almeja. Activa glúteo medio. Esencial para salud de cadera.",
     "equipo":["ninguno","mat","banda"],"dificultad":"principiante",
     "objetivo":["recomposicion","salud","rehabilitacion"],"lesiones_evitar":[],
     "coach":"Heather Robertson","url":"https://www.youtube.com/results?search_query=heather+robertson+clamshell+exercise+band+tutorial"},

    # ── CUÁDRICEPS / PIERNAS ─────────────────────────────────────────────────
    {"id":"q01","nombre":"Sentadilla con barra","grupo":"Cuádriceps",
     "descripcion":"Reina de los ejercicios. Barra en trapecios, pies a ancho de hombros, baja hasta paralelo manteniendo el pecho arriba y rodillas sobre pies.",
     "equipo":["barra","rack"],"dificultad":"intermedio",
     "objetivo":["recomposicion","hipertrofia","fuerza"],"lesiones_evitar":["Rodillas","Espalda baja (lumbar)"],
     "coach":"Squat University","url":"https://www.youtube.com/results?search_query=squat+university+barbell+squat+technique+tutorial"},
    {"id":"q02","nombre":"Sentadilla goblet con mancuerna","grupo":"Cuádriceps",
     "descripcion":"Sostén una mancuerna frente al pecho. Excelente para aprender la mecánica de la sentadilla. Mantén el torso erguido.",
     "equipo":["mancuernas"],"dificultad":"principiante",
     "objetivo":["recomposicion","salud"],"lesiones_evitar":["Rodillas"],
     "coach":"Jeff Nippard","url":"https://www.youtube.com/results?search_query=jeff+nippard+goblet+squat+tutorial"},
    {"id":"q03","nombre":"Sentadilla sumo","grupo":"Cuádriceps",
     "descripcion":"Pies más separados que los hombros, pies apuntando afuera. Mayor activación de glúteos e isquiotibiales. Sostén una mancuerna o kettlebell.",
     "equipo":["mancuernas","ninguno"],"dificultad":"principiante",
     "objetivo":["recomposicion","hipertrofia"],"lesiones_evitar":[],
     "coach":"Heather Robertson","url":"https://www.youtube.com/results?search_query=heather+robertson+sumo+squat+tutorial"},
    {"id":"q04","nombre":"Leg Press","grupo":"Cuádriceps",
     "descripcion":"Máquina inclinada. Pies a ancho de caderas en la plataforma. No bloquees completamente las rodillas. Controla el regreso.",
     "equipo":["maquina_leg_press"],"dificultad":"principiante",
     "objetivo":["recomposicion","hipertrofia"],"lesiones_evitar":["Rodillas"],
     "coach":"Jeremy Ethier","url":"https://www.youtube.com/results?search_query=jeremy+ethier+leg+press+technique+tutorial"},
    {"id":"q05","nombre":"Estocada con mancuernas","grupo":"Cuádriceps",
     "descripcion":"Paso largo al frente, baja la rodilla trasera casi al suelo. Alterna piernas. Excelente para equilibrio y fuerza unilateral.",
     "equipo":["ninguno","mancuernas"],"dificultad":"principiante",
     "objetivo":["recomposicion","hipertrofia"],"lesiones_evitar":["Rodillas"],
     "coach":"Heather Robertson","url":"https://www.youtube.com/results?search_query=heather+robertson+dumbbell+lunge+tutorial"},
    {"id":"q06","nombre":"Step Up con mancuernas","grupo":"Cuádriceps",
     "descripcion":"Sube a un banco o step con una pierna a la vez. Empuja con el talón para mayor activación glútea. Controla el descenso.",
     "equipo":["banco","mancuernas","ninguno"],"dificultad":"principiante",
     "objetivo":["recomposicion","salud"],"lesiones_evitar":["Rodillas"],
     "coach":"Heather Robertson","url":"https://www.youtube.com/results?search_query=heather+robertson+step+up+exercise+tutorial"},

    # ── ISQUIOTIBIALES ────────────────────────────────────────────────────────
    {"id":"i01","nombre":"Romanian Deadlift con barra","grupo":"Isquiotibiales",
     "descripcion":"Piernas ligeramente dobladas, baja la barra por las espinillas manteniendo la espalda recta y el core activo. Siente el estiramiento en isquiotibiales.",
     "equipo":["barra"],"dificultad":"intermedio",
     "objetivo":["recomposicion","hipertrofia","fuerza"],"lesiones_evitar":["Espalda baja (lumbar)"],
     "coach":"Jeff Nippard","url":"https://www.youtube.com/results?search_query=jeff+nippard+romanian+deadlift+barbell+tutorial"},
    {"id":"i02","nombre":"Romanian Deadlift con mancuernas","grupo":"Isquiotibiales",
     "descripcion":"Igual que con barra pero más accesible para casa. Mantén las mancuernas cerca del cuerpo durante todo el movimiento.",
     "equipo":["mancuernas"],"dificultad":"principiante",
     "objetivo":["recomposicion","hipertrofia"],"lesiones_evitar":["Espalda baja (lumbar)"],
     "coach":"Jeff Nippard","url":"https://www.youtube.com/results?search_query=jeff+nippard+dumbbell+romanian+deadlift+tutorial"},
    {"id":"i03","nombre":"Leg Curl en máquina","grupo":"Isquiotibiales",
     "descripcion":"Tumbada boca abajo, lleva los talones hacia los glúteos contrayendo los isquiotibiales. Controla el regreso. Excelente aislamiento.",
     "equipo":["maquina_leg_curl"],"dificultad":"principiante",
     "objetivo":["recomposicion","hipertrofia"],"lesiones_evitar":[],
     "coach":"Jeremy Ethier","url":"https://www.youtube.com/results?search_query=jeremy+ethier+lying+leg+curl+machine+tutorial"},
    {"id":"i04","nombre":"Good Morning con mancuernas","grupo":"Isquiotibiales",
     "descripcion":"Mancuernas en hombros, bisagra de cadera hacia adelante manteniendo espalda recta. Activa isquiotibiales y espalda baja.",
     "equipo":["mancuernas"],"dificultad":"intermedio",
     "objetivo":["recomposicion","fuerza"],"lesiones_evitar":["Espalda baja (lumbar)"],
     "coach":"Alan Thrall","url":"https://www.youtube.com/results?search_query=alan+thrall+good+morning+exercise+tutorial"},

    # ── ESPALDA ───────────────────────────────────────────────────────────────
    {"id":"e01","nombre":"Jalón al pecho (Lat Pulldown)","grupo":"Espalda",
     "descripcion":"Agarra la barra un poco más ancho que los hombros, jala hacia el pecho arqueando ligeramente el torso. Contrae los dorsales en la cima.",
     "equipo":["maquina_polea"],"dificultad":"principiante",
     "objetivo":["recomposicion","hipertrofia"],"lesiones_evitar":["Espalda alta / hombros"],
     "coach":"Jeff Nippard","url":"https://www.youtube.com/results?search_query=jeff+nippard+lat+pulldown+technique+tutorial"},
    {"id":"e02","nombre":"Remo con mancuerna (un brazo)","grupo":"Espalda",
     "descripcion":"Rodilla y mano en el banco, tira la mancuerna hacia la cadera manteniendo el codo cerca del cuerpo. Excelente para dorsales y romboides.",
     "equipo":["mancuernas","banco"],"dificultad":"principiante",
     "objetivo":["recomposicion","hipertrofia"],"lesiones_evitar":[],
     "coach":"Jeff Nippard","url":"https://www.youtube.com/results?search_query=jeff+nippard+one+arm+dumbbell+row+tutorial"},
    {"id":"e03","nombre":"Remo con barra","grupo":"Espalda",
     "descripcion":"Inclinado a 45°, tira la barra hacia el abdomen bajo. Uno de los mejores ejercicios para volumen de espalda. Mantén la espalda recta.",
     "equipo":["barra"],"dificultad":"intermedio",
     "objetivo":["recomposicion","hipertrofia","fuerza"],"lesiones_evitar":["Espalda baja (lumbar)"],
     "coach":"Jeff Nippard","url":"https://www.youtube.com/results?search_query=jeff+nippard+barbell+row+technique+tutorial"},
    {"id":"e04","nombre":"Face Pull con banda","grupo":"Espalda",
     "descripcion":"Con banda elástica anclada, tira hacia la cara separando los codos. Fortalece manguito rotador y romboides. Esencial para postura.",
     "equipo":["banda","maquina_cables"],"dificultad":"principiante",
     "objetivo":["recomposicion","salud","rehabilitacion"],"lesiones_evitar":[],
     "coach":"Jeff Nippard","url":"https://www.youtube.com/results?search_query=jeff+nippard+face+pull+band+technique+tutorial"},
    {"id":"e05","nombre":"Superman","grupo":"Espalda",
     "descripcion":"Boca abajo, eleva simultáneamente brazos y piernas del suelo. Fortalece la cadena posterior. Sin equipo, ideal para activación.",
     "equipo":["ninguno","mat"],"dificultad":"principiante",
     "objetivo":["recomposicion","salud"],"lesiones_evitar":["Espalda baja (lumbar)"],
     "coach":"Heather Robertson","url":"https://www.youtube.com/results?search_query=heather+robertson+superman+exercise+back+tutorial"},
    {"id":"e06","nombre":"Dominadas asistidas","grupo":"Espalda",
     "descripcion":"Con banda elástica de apoyo o máquina asistida. El mejor ejercicio para la espalda. Progresa a dominadas sin asistencia.",
     "equipo":["barra_dominadas","banda","maquina_asistida"],"dificultad":"intermedio",
     "objetivo":["recomposicion","hipertrofia","fuerza"],"lesiones_evitar":["Espalda alta / hombros"],
     "coach":"Jeff Nippard","url":"https://www.youtube.com/results?search_query=jeff+nippard+pull+up+progression+tutorial+tutorial"},

    # ── PECHO ─────────────────────────────────────────────────────────────────
    {"id":"p01","nombre":"Press de pecho con mancuernas","grupo":"Pecho",
     "descripcion":"Acostada en banco, mancuernas a la altura del pecho, empuja hacia arriba sin bloquear codos. Controla el descenso.",
     "equipo":["mancuernas","banco"],"dificultad":"principiante",
     "objetivo":["recomposicion","hipertrofia"],"lesiones_evitar":["Espalda alta / hombros"],
     "coach":"Jeremy Ethier","url":"https://www.youtube.com/results?search_query=jeremy+ethier+dumbbell+chest+press+tutorial"},
    {"id":"p02","nombre":"Push-up (flexión de pecho)","grupo":"Pecho",
     "descripcion":"El clásico sin equipo. Manos a ancho de hombros, cuerpo en línea recta. Modifica con rodillas si es necesario. Progresa a versión declinada.",
     "equipo":["ninguno","mat"],"dificultad":"principiante",
     "objetivo":["recomposicion","fuerza","salud"],"lesiones_evitar":["Muñecas / codos"],
     "coach":"Athlean-X","url":"https://www.youtube.com/results?search_query=athlean+x+perfect+push+up+form+tutorial"},
    {"id":"p03","nombre":"Fly con mancuernas","grupo":"Pecho",
     "descripcion":"Acostada en banco, abre los brazos hacia los lados con ligera flexión de codo, junta las mancuernas arriba. Enfatiza el estiramiento del pecho.",
     "equipo":["mancuernas","banco"],"dificultad":"intermedio",
     "objetivo":["recomposicion","hipertrofia"],"lesiones_evitar":["Espalda alta / hombros"],
     "coach":"Jeff Nippard","url":"https://www.youtube.com/results?search_query=jeff+nippard+dumbbell+fly+technique+tutorial"},

    # ── HOMBROS ───────────────────────────────────────────────────────────────
    {"id":"h01","nombre":"Press de hombros con mancuernas","grupo":"Hombros",
     "descripcion":"Sentada o de pie, mancuernas a la altura de los hombros, empuja hacia arriba. No bloquees codos arriba. Activa todo el deltoides.",
     "equipo":["mancuernas"],"dificultad":"principiante",
     "objetivo":["recomposicion","hipertrofia"],"lesiones_evitar":["Espalda alta / hombros","Cuello / cervical"],
     "coach":"Jeff Nippard","url":"https://www.youtube.com/results?search_query=jeff+nippard+dumbbell+shoulder+press+tutorial"},
    {"id":"h02","nombre":"Elevaciones laterales","grupo":"Hombros",
     "descripcion":"Mancuernas a los lados, eleva hasta la altura de los hombros con codos ligeramente doblados. Fundamental para hombros anchos. Pesos ligeros.",
     "equipo":["mancuernas"],"dificultad":"principiante",
     "objetivo":["recomposicion","hipertrofia"],"lesiones_evitar":["Espalda alta / hombros"],
     "coach":"Jeff Nippard","url":"https://www.youtube.com/results?search_query=jeff+nippard+lateral+raise+perfect+form+tutorial"},
    {"id":"h03","nombre":"Elevaciones frontales","grupo":"Hombros",
     "descripcion":"Mancuerna en cada mano, eleva al frente hasta la altura de los hombros alternando o juntas. Activa el deltoides anterior.",
     "equipo":["mancuernas"],"dificultad":"principiante",
     "objetivo":["recomposicion","hipertrofia"],"lesiones_evitar":["Espalda alta / hombros"],
     "coach":"Jeremy Ethier","url":"https://www.youtube.com/results?search_query=jeremy+ethier+front+raise+dumbbell+tutorial"},

    # ── BÍCEPS ────────────────────────────────────────────────────────────────
    {"id":"b01","nombre":"Curl con mancuernas","grupo":"Bíceps",
     "descripcion":"De pie, curl alterno o simultáneo. Codos fijos a los lados, supina la muñeca al subir. Controla el regreso.",
     "equipo":["mancuernas"],"dificultad":"principiante",
     "objetivo":["recomposicion","hipertrofia"],"lesiones_evitar":["Muñecas / codos"],
     "coach":"Jeff Nippard","url":"https://www.youtube.com/results?search_query=jeff+nippard+dumbbell+curl+perfect+form+tutorial"},
    {"id":"b02","nombre":"Curl martillo","grupo":"Bíceps",
     "descripcion":"Igual que el curl normal pero con agarre neutro (pulgares arriba). Activa también el braquial y braquiorradial.",
     "equipo":["mancuernas"],"dificultad":"principiante",
     "objetivo":["recomposicion","hipertrofia"],"lesiones_evitar":["Muñecas / codos"],
     "coach":"Jeremy Ethier","url":"https://www.youtube.com/results?search_query=jeremy+ethier+hammer+curl+tutorial"},
    {"id":"b03","nombre":"Curl con barra","grupo":"Bíceps",
     "descripcion":"Agarre supinado, barra de pie. Mayor carga posible para bíceps. Evita usar el cuerpo para impulsar.",
     "equipo":["barra"],"dificultad":"principiante",
     "objetivo":["recomposicion","hipertrofia","fuerza"],"lesiones_evitar":["Muñecas / codos"],
     "coach":"Jeff Nippard","url":"https://www.youtube.com/results?search_query=jeff+nippard+barbell+curl+technique+tutorial"},

    # ── TRÍCEPS ───────────────────────────────────────────────────────────────
    {"id":"t01","nombre":"Extensión de tríceps sobre cabeza","grupo":"Tríceps",
     "descripcion":"Sentada, mancuerna con ambas manos sobre la cabeza, baja detrás de la nuca y sube. Excelente para el largo del tríceps.",
     "equipo":["mancuernas"],"dificultad":"principiante",
     "objetivo":["recomposicion","hipertrofia"],"lesiones_evitar":["Muñecas / codos","Cuello / cervical"],
     "coach":"Jeff Nippard","url":"https://www.youtube.com/results?search_query=jeff+nippard+overhead+tricep+extension+tutorial"},
    {"id":"t02","nombre":"Fondos en banco (Dips)","grupo":"Tríceps",
     "descripcion":"Manos en el borde del banco, pies al frente. Baja el cuerpo doblando codos a 90°. Añade peso en el regazo para progresar.",
     "equipo":["banco"],"dificultad":"principiante",
     "objetivo":["recomposicion","hipertrofia"],"lesiones_evitar":["Muñecas / codos","Espalda alta / hombros"],
     "coach":"Heather Robertson","url":"https://www.youtube.com/results?search_query=heather+robertson+bench+dips+tricep+tutorial"},
    {"id":"t03","nombre":"Kickback de tríceps","grupo":"Tríceps",
     "descripcion":"Inclinada con una mano en el banco, codo fijo a 90°, extiende el brazo atrás hasta completa extensión. Aislamiento puro.",
     "equipo":["mancuernas","banco"],"dificultad":"principiante",
     "objetivo":["recomposicion","hipertrofia"],"lesiones_evitar":["Muñecas / codos"],
     "coach":"Heather Robertson","url":"https://www.youtube.com/results?search_query=heather+robertson+tricep+kickback+dumbbell+tutorial"},

    # ── CORE ─────────────────────────────────────────────────────────────────
    {"id":"c01","nombre":"Plancha (Plank)","grupo":"Core",
     "descripcion":"Apoya antebrazos y puntillas. Cuerpo en línea recta, core activo. No dejes caer las caderas. Progresa en tiempo.",
     "equipo":["ninguno","mat"],"dificultad":"principiante",
     "objetivo":["recomposicion","salud","fuerza"],"lesiones_evitar":["Espalda baja (lumbar)","Muñecas / codos"],
     "coach":"Squat University","url":"https://www.youtube.com/results?search_query=squat+university+plank+perfect+form+tutorial"},
    {"id":"c02","nombre":"Dead Bug","grupo":"Core",
     "descripcion":"Boca arriba, brazos al techo y rodillas a 90°. Baja el brazo derecho y pierna izquierda simultáneamente sin despegar la espalda. Alterna.",
     "equipo":["ninguno","mat"],"dificultad":"principiante",
     "objetivo":["recomposicion","salud","rehabilitacion"],"lesiones_evitar":["Espalda baja (lumbar)"],
     "coach":"Squat University","url":"https://www.youtube.com/results?search_query=squat+university+dead+bug+exercise+core+tutorial"},
    {"id":"c03","nombre":"Bird Dog","grupo":"Core",
     "descripcion":"En cuadrupedia, extiende simultáneamente el brazo y pierna opuestos. Mantén la cadera nivelada. Esencial para estabilidad lumbar.",
     "equipo":["ninguno","mat"],"dificultad":"principiante",
     "objetivo":["recomposicion","salud","rehabilitacion"],"lesiones_evitar":[],
     "coach":"Squat University","url":"https://www.youtube.com/results?search_query=squat+university+bird+dog+exercise+tutorial"},
    {"id":"c04","nombre":"Mountain Climber","grupo":"Core",
     "descripcion":"En posición de plancha alta, alterna rodillas hacia el pecho rápidamente. Cardio + core en uno.",
     "equipo":["ninguno","mat"],"dificultad":"intermedio",
     "objetivo":["recomposicion","salud"],"lesiones_evitar":["Muñecas / codos","Espalda baja (lumbar)"],
     "coach":"Sydney Cummings","url":"https://www.youtube.com/results?search_query=sydney+cummings+mountain+climber+cardio+tutorial"},
    {"id":"c05","nombre":"Crunch abdominal","grupo":"Core",
     "descripcion":"Boca arriba, rodillas dobladas, sube el tórax hacia las rodillas sin jalar el cuello. Contrae el abdomen en la cima.",
     "equipo":["ninguno","mat"],"dificultad":"principiante",
     "objetivo":["recomposicion","salud"],"lesiones_evitar":["Cuello / cervical"],
     "coach":"Heather Robertson","url":"https://www.youtube.com/results?search_query=heather+robertson+ab+crunch+proper+form+tutorial"},

    # ── CARDIO ────────────────────────────────────────────────────────────────
    {"id":"ca01","nombre":"Bicicleta estática — Steady State","grupo":"Cardio",
     "descripcion":"Pedalea a intensidad moderada (RPE 5-6) durante 20-30 min. Zona 2: puedes hablar con esfuerzo. Ideal para recuperación activa y quema de grasa.",
     "equipo":["bicicleta"],"dificultad":"principiante",
     "objetivo":["recomposicion","salud","perdida_grasa"],"lesiones_evitar":[],
     "coach":"","url":"https://www.youtube.com/results?search_query=+zone+2+cardio+stationary+bike+benefits+tutorial"},
    {"id":"ca02","nombre":"Bicicleta estática — HIIT","grupo":"Cardio",
     "descripcion":"Alterna 30 seg máximo esfuerzo + 90 seg recuperación. 8-10 rondas. Altamente efectivo para composición corporal (Schoenfeld & Dawes).",
     "equipo":["bicicleta"],"dificultad":"intermedio",
     "objetivo":["recomposicion","perdida_grasa"],"lesiones_evitar":["Rodillas"],
     "coach":"","url":"https://www.youtube.com/results?search_query=sydney+cummings+stationary+bike+HIIT+workout+tutorial"},
    {"id":"ca03","nombre":"Jump Squat","grupo":"Cardio",
     "descripcion":"Sentadilla y explota hacia arriba saltando. Aterriza suavemente doblando rodillas. Combina potencia, cardio y piernas.",
     "equipo":["ninguno"],"dificultad":"intermedio",
     "objetivo":["recomposicion","salud"],"lesiones_evitar":["Rodillas","Tobillos / pies"],
     "coach":"Sydney Cummings","url":"https://www.youtube.com/results?search_query=sydney+cummings+jump+squat+explosive+tutorial"},
    {"id":"ca04","nombre":"Burpee","grupo":"Cardio",
     "descripcion":"El ejercicio total body más efectivo para cardio en casa. Modifica omitiendo el salto si es necesario.",
     "equipo":["ninguno","mat"],"dificultad":"intermedio",
     "objetivo":["recomposicion","perdida_grasa"],"lesiones_evitar":["Muñecas / codos","Rodillas"],
     "coach":"Sydney Cummings","url":"https://www.youtube.com/results?search_query=sydney+cummings+burpee+proper+form+tutorial"},
]


# ══════════════════════════════════════════════════════════════════════════════
# MAPEO DE EQUIPO
# ══════════════════════════════════════════════════════════════════════════════
EQUIPO_DISPONIBLE = {
    "Solo peso corporal — sin equipo":
        ["ninguno","mat"],
    "Equipo básico — mancuernas y/o bandas elásticas":
        ["ninguno","mat","mancuernas","banda"],
    "Equipo intermedio — mancuernas, barra, banco":
        ["ninguno","mat","mancuernas","banda","barra","banco","bicicleta"],
    "Acceso a gimnasio completo":
        ["ninguno","mat","mancuernas","banda","barra","banco","bicicleta",
         "rack","maquina_cables","maquina_polea","maquina_leg_press",
         "maquina_leg_curl","maquina_asistida","barra_dominadas"],
}

# Añadir barra_ligera como equivalente a barra para equipo básico
EQUIPO_DISPONIBLE["Equipo básico — mancuernas y/o bandas elásticas"].append("barra")


# ══════════════════════════════════════════════════════════════════════════════
# ESTRUCTURAS DE PROGRAMA
# ══════════════════════════════════════════════════════════════════════════════
ESTRUCTURAS = {
    2: [
        {"nombre":"Día 1 — Cuerpo completo A",
         "grupos":["Glúteos","Cuádriceps","Espalda","Core"],"color":"#dbeafe"},
        {"nombre":"Día 2 — Cuerpo completo B",
         "grupos":["Glúteos","Isquiotibiales","Hombros","Pecho","Core"],"color":"#dcfce7"},
    ],
    3: [
        {"nombre":"Día 1 — Inferior (Glúteos & Piernas)",
         "grupos":["Glúteos","Cuádriceps","Isquiotibiales","Core"],"color":"#fce7f3"},
        {"nombre":"Día 2 — Superior (Empuje & Jale)",
         "grupos":["Espalda","Pecho","Hombros","Bíceps","Tríceps"],"color":"#dbeafe"},
        {"nombre":"Día 3 — Glúteos & Cardio",
         "grupos":["Glúteos","Isquiotibiales","Core","Cardio"],"color":"#dcfce7"},
    ],
    4: [
        {"nombre":"Día 1 — Superior Empuje",
         "grupos":["Pecho","Hombros","Tríceps","Core"],"color":"#dbeafe"},
        {"nombre":"Día 2 — Inferior A (Cuádriceps & Glúteos)",
         "grupos":["Cuádriceps","Glúteos","Core"],"color":"#fce7f3"},
        {"nombre":"Día 3 — Superior Jale",
         "grupos":["Espalda","Bíceps","Hombros","Core"],"color":"#dcfce7"},
        {"nombre":"Día 4 — Inferior B (Glúteos & Isquiotibiales)",
         "grupos":["Glúteos","Isquiotibiales","Cardio"],"color":"#f3e8ff"},
    ],
    5: [
        {"nombre":"Día 1 — Empuje A",
         "grupos":["Pecho","Hombros","Tríceps"],"color":"#dbeafe"},
        {"nombre":"Día 2 — Jale A",
         "grupos":["Espalda","Bíceps","Core"],"color":"#dcfce7"},
        {"nombre":"Día 3 — Piernas & Glúteos A",
         "grupos":["Glúteos","Cuádriceps","Core"],"color":"#fce7f3"},
        {"nombre":"Día 4 — Empuje B + Core",
         "grupos":["Hombros","Pecho","Tríceps","Core"],"color":"#dbeafe"},
        {"nombre":"Día 5 — Piernas & Glúteos B",
         "grupos":["Glúteos","Isquiotibiales","Cardio"],"color":"#f3e8ff"},
    ],
    6: [
        {"nombre":"Día 1 — Empuje A",
         "grupos":["Pecho","Hombros","Tríceps"],"color":"#dbeafe"},
        {"nombre":"Día 2 — Jale A",
         "grupos":["Espalda","Bíceps","Core"],"color":"#dcfce7"},
        {"nombre":"Día 3 — Piernas A",
         "grupos":["Glúteos","Cuádriceps","Core"],"color":"#fce7f3"},
        {"nombre":"Día 4 — Empuje B",
         "grupos":["Hombros","Pecho","Tríceps"],"color":"#dbeafe"},
        {"nombre":"Día 5 — Jale B",
         "grupos":["Espalda","Bíceps","Hombros"],"color":"#dcfce7"},
        {"nombre":"Día 6 — Piernas B + Cardio",
         "grupos":["Glúteos","Isquiotibiales","Cardio"],"color":"#f3e8ff"},
    ],
}


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def get_equipo_lista(equipo_str: str) -> list:
    for k, v in EQUIPO_DISPONIBLE.items():
        if k == equipo_str:
            return v
    return EQUIPO_DISPONIBLE["Solo peso corporal — sin equipo"]


def get_rep_scheme(objetivo: str, dificultad: str = "intermedio") -> str:
    obj = objetivo.lower()
    if "fuerza" in obj:
        return "4-5 × 4-6"
    elif "hipertrofia" in obj or "músculo" in obj:
        return "4 × 8-10"
    elif "grasa" in obj:
        return "3 × 12-15"
    else:  # recomposicion, salud
        return "3-4 × 10-12"


def get_descanso(objetivo: str) -> str:
    obj = objetivo.lower()
    if "fuerza" in obj:           return "2-3 min"
    elif "hipertrofia" in obj:    return "60-90 seg"
    elif "grasa" in obj:          return "30-45 seg"
    else:                          return "60-90 seg"


def filtrar_ejercicios(grupo: str, equipo_lista: list, lesiones_lista: list,
                        max_ej: int = 3) -> list:
    lesiones = [l.strip() for l in lesiones_lista if l and l != "Ninguna"]
    candidatos = [
        e for e in EJERCICIOS_BASE
        if e["grupo"] == grupo
        and any(eq in equipo_lista for eq in e["equipo"])
        and not any(l in e.get("lesiones_evitar", []) for l in lesiones)
    ]
    return candidatos[:max_ej]


def get_fase_actual(uid: str) -> dict | None:
    """Obtiene la fase del ciclo actual del usuario."""
    try:
        from datetime import timedelta
        df = leer_df_usuario("ciclo", uid)
        if df.empty:
            return None
        df["fecha_inicio"] = pd.to_datetime(df["fecha_inicio"], errors="coerce").dt.date
        df = df.dropna(subset=["fecha_inicio"]).sort_values("fecha_inicio")
        if df.empty:
            return None

        ultimo = df.iloc[-1]["fecha_inicio"]
        # Calcular promedio de ciclo
        if len(df) >= 2:
            diffs = [(df.iloc[i]["fecha_inicio"] - df.iloc[i-1]["fecha_inicio"]).days
                     for i in range(1, len(df))]
            dur = round(sum(diffs) / len(diffs))
        else:
            dur = 28

        dias = (date.today() - ultimo).days
        ciclos = dias // dur
        inicio_actual = ultimo + timedelta(days=dur * ciclos)
        dia_ciclo = (date.today() - inicio_actual).days + 1

        if 1 <= dia_ciclo <= 5:
            return {"nombre":"Menstrual","emoji":"🔴","dia":dia_ciclo,
                    "nota":"Baja la intensidad si hay molestias. Cardio suave y movilidad.",
                    "intensidad":0.7}
        elif 6 <= dia_ciclo <= 13:
            return {"nombre":"Folicular","emoji":"🟢","dia":dia_ciclo,
                    "nota":"¡Tu mejor semana! Ideal para cargas máximas y aprender movimientos nuevos.",
                    "intensidad":1.0}
        elif 14 <= dia_ciclo <= 16:
            return {"nombre":"Ovulatoria","emoji":"🟡","dia":dia_ciclo,
                    "nota":"Pico de rendimiento. Intenta tus récords personales hoy.",
                    "intensidad":1.1}
        else:
            return {"nombre":"Lútea","emoji":"🟣","dia":dia_ciclo,
                    "nota":"Entrena moderado. Reduce volumen en la última semana antes del período.",
                    "intensidad":0.85}
    except Exception:
        return None


def badge(texto: str, color: str) -> str:
    return f'<span style="background:{color};color:#1e293b;font-size:11px;padding:2px 8px;border-radius:10px;font-weight:500;">{texto}</span>'


# ══════════════════════════════════════════════════════════════════════════════
# BASE DE WORKOUTS COMPLETOS  (Opción A: video curado | B: búsqueda fallback)
# ══════════════════════════════════════════════════════════════════════════════
# Mapa de video_id por ejercicio para embed directo (coaches top)
_EJ_VIDEOS = {
    "g01": "IncLBJCfgSY",  "g02": "2Vprklk8E-g",  "g03": "2Vprklk8E-g",
    "g04": "2C-uNgKwPLE",  "g05": "SXEDFkMa8xE",  "q01": "ultWZbUMPL8",
    "q02": "MeIiIdhvXT4",  "q05": "D7KaRcUTQeE",  "i01": "jEy_czb3RKA",
    "i02": "jEy_czb3RKA",  "e01": "CAwf7n6Luuc",  "e02": "roCP442wSsA",
    "e03": "G8l_8chR5BE",  "e04": "rep-qVOkqgk",  "p02": "IODxDxX7oi4",
    "h02": "XPPfnSEATJA",  "b01": "ykJmrZ5v0Oo",  "c01": "F-nQ_KJgfCY",
    "c02": "4XLEnwUr1d8",  "c03": "wiFNA3sqjCA",
}

WORKOUTS_DB = {
    "🔥 HIIT": [
        {"titulo":"30 Min Full Body HIIT — Sin equipo","coach":"Heather Robertson",
         "duracion":"30 min","nivel":"Intermedio","equipo":"Sin equipo",
         "descripcion":"HIIT de cuerpo completo con 28 ejercicios. Sin equipo, desde casa.",
         "video_id":"Emu7uB59E2g","busqueda":"heather robertson 30 min full body HIIT no equipment"},
        {"titulo":"15 Min HIIT + Abs","coach":"Heather Robertson",
         "duracion":"15 min","nivel":"Intermedio","equipo":"Sin equipo",
         "descripcion":"Cardio HIIT y abdomen en solo 15 minutos. Perfecta para días cortos.",
         "video_id":"GDY8g5KME9E","busqueda":"heather robertson 15 min HIIT abs workout"},
        {"titulo":"Low Impact HIIT — Sin saltos","coach":"Heather Robertson",
         "duracion":"30 min","nivel":"Principiante","equipo":"Sin equipo",
         "descripcion":"HIIT de bajo impacto. Ideal para principiantes o fase menstrual.",
         "video_id":"aFBRopKNGfw","busqueda":"heather robertson low impact HIIT no jumping"},
        {"titulo":"Fat Burning HIIT — Sin repeticiones","coach":"Heather Robertson",
         "duracion":"30 min","nivel":"Intermedio","equipo":"Sin equipo",
         "descripcion":"HIIT quema grasa sin repetir ejercicios. Gran variedad.",
         "video_id":"AZ-rJgdOYGU","busqueda":"heather robertson fat burning HIIT no repeats"},
    ],
    "🦵 Piernas & Glúteos": [
        {"titulo":"Killer Leg Day — Fuerza","coach":"Heather Robertson",
         "duracion":"35 min","nivel":"Intermedio","equipo":"Mancuernas opcionales",
         "descripcion":"Entrenamiento completo de piernas enfocado en fuerza y forma correcta.",
         "video_id":"eemRXHKsGIc","busqueda":"heather robertson killer leg day strength workout"},
        {"titulo":"HIIT Brutal — Piernas + Glúteos","coach":"Heather Robertson",
         "duracion":"30 min","nivel":"Avanzado","equipo":"Sin equipo",
         "descripcion":"Piernas y glúteos en formato HIIT. Perfecto para fase folicular.",
         "video_id":"sSiq1opmejo","busqueda":"heather robertson brutal legs glutes HIIT"},
        {"titulo":"Legs & Glutes Power","coach":"Heather Robertson",
         "duracion":"30 min","nivel":"Intermedio","equipo":"Sin equipo",
         "descripcion":"Potencia en piernas y glúteos. Ideal fase folicular u ovulatoria.",
         "video_id":"2QAXtSiShbc","busqueda":"heather robertson legs glutes power workout"},
        {"titulo":"Booty + Piernas — Sin equipo","coach":"Heather Robertson",
         "duracion":"30 min","nivel":"Intermedio","equipo":"Sin equipo",
         "descripcion":"Glúteos y piernas desde casa. Sin equipo necesario.",
         "video_id":"pcJsP4gogsI","busqueda":"heather robertson booty leg no equipment"},
    ],
    "💪 Full Body": [
        {"titulo":"Full Body con Mancuernas — 30 min","coach":"Heather Robertson",
         "duracion":"30 min","nivel":"Intermedio","equipo":"Mancuernas",
         "descripcion":"Cuerpo completo combinando fuerza y cardio. Mancuernas requeridas.",
         "video_id":"Q3aYsLpAogA","busqueda":"heather robertson full body workout with weights 30 minutes"},
        {"titulo":"Full Body Fuerza + Cardio","coach":"Heather Robertson",
         "duracion":"30 min","nivel":"Intermedio","equipo":"Sin equipo",
         "descripcion":"Combina fuerza y cardio en un entrenamiento completo y eficiente.",
         "video_id":"m1z7zSWatwo","busqueda":"heather robertson full body HIIT strength cardio"},
        {"titulo":"Full Body HIIT — 20 min","coach":"Heather Robertson",
         "duracion":"20 min","nivel":"Intermedio","equipo":"Sin equipo",
         "descripcion":"Cuerpo completo en solo 20 minutos. Ideal cuando el tiempo es limitado.",
         "video_id":"Gzp8IA2vW_Q","busqueda":"heather robertson 20 minute full body HIIT home"},
    ],
    "🏋️ Core & Abdomen": [
        {"titulo":"Core + Abs — 12 minutos","coach":"Heather Robertson",
         "duracion":"12 min","nivel":"Principiante","equipo":"Mat",
         "descripcion":"Core en llamas en 12 minutos. Sin equipo, solo mat.",
         "video_id":"nkMhnd2kWIQ","busqueda":"heather robertson core ab workout 12 minutes"},
        {"titulo":"11 Min Abs — Sin repeticiones","coach":"Heather Robertson",
         "duracion":"11 min","nivel":"Intermedio","equipo":"Mat",
         "descripcion":"11 minutos sin repetir ejercicios. Variedad total de abdomen.",
         "video_id":"1LMNa9C8gOo","busqueda":"heather robertson 11 minute abs no repeats"},
        {"titulo":"Abs + Booty Workout","coach":"Heather Robertson",
         "duracion":"20 min","nivel":"Intermedio","equipo":"Sin equipo",
         "descripcion":"La combinación ganadora: abdomen y glúteos en una sesión.",
         "video_id":"za43d9iUZ4M","busqueda":"heather robertson abs booty workout"},
    ],
    "🧘 Movilidad & Yoga": [
        {"titulo":"Morning Yoga — Energía y flexibilidad","coach":"Yoga with Adriene",
         "duracion":"20 min","nivel":"Principiante","equipo":"Mat",
         "descripcion":"Yoga matutino para energizar el cuerpo. Ideal para recuperación.",
         "video_id":"v7AYKMP6rOE","busqueda":"yoga with adriene morning yoga 20 minutes"},
        {"titulo":"Yoga para Alivio del Estrés","coach":"Yoga with Adriene",
         "duracion":"25 min","nivel":"Principiante","equipo":"Mat",
         "descripcion":"Yoga restaurativo para reducir el estrés y recuperar el cuerpo.",
         "video_id":"hJbRpHZr_d0","busqueda":"yoga with adriene stress relief yoga"},
    ],
}


def recomendar_workout_dia(grupos: list) -> dict | None:
    """Selecciona el workout completo más relevante para los grupos del día."""
    g = " ".join(grupos).lower()
    if any(x in g for x in ["glúteos","isquiotibiales","cuádriceps","piernas"]):
        cat = "🦵 Piernas & Glúteos"
    elif "cardio" in g:
        cat = "🔥 HIIT"
    elif any(x in g for x in ["core","abdomen"]):
        cat = "🏋️ Core & Abdomen"
    elif any(x in g for x in ["pecho","hombros","espalda","bíceps","tríceps"]):
        cat = "💪 Full Body"
    else:
        cat = "💪 Full Body"
    vids = WORKOUTS_DB.get(cat, [])
    return vids[0] if vids else None


# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════
def mostrar():
    estado.cargar_perfil()
    st.title("🏋️ Rutinas & Programas")

    uid     = estado.get("user_id",       "")
    obj     = estado.get("eval_objetivo", "")
    nivel   = estado.get("eval_nivel",    "")
    dias    = estado.get("eval_dias",     3)
    equipo  = estado.get("eval_equipo",   "")
    lesiones_str = estado.get("eval_lesiones", "")
    genero  = estado.get("genero",        "Mujer")

    lesiones = [l.strip() for l in lesiones_str.split(",") if l.strip() and l.strip() != "Ninguna"]
    equipo_lista = get_equipo_lista(equipo)
    rep_scheme = get_rep_scheme(obj)
    descanso   = get_descanso(obj)
    fase       = get_fase_actual(uid) if genero == "Mujer" else None

    # ── Sin evaluación ────────────────────────────────────────────────────────
    if not obj:
        st.warning("⚠️ Completa la **🧬 Evaluación Inicial** primero para obtener tu programa personalizado.")
        return

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Mi Programa", "🎬 Workouts", "🤖 Programa IA", "💪 Ejercicios", "👩‍💻 Coaches"])

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 1 — MI PROGRAMA
    # ══════════════════════════════════════════════════════════════════════════
    with tab1:
        # Perfil resumen — cards grandes legibles
        obj_label  = obj.split("(")[0].strip()[:30]
        niv_label  = nivel.split("—")[0].strip()[:20] if "—" in nivel else nivel[:20]
        eq_label   = equipo.split("—")[0].strip()[:25]
        st.markdown(f"""
        <div style="display:flex;gap:12px;margin-bottom:8px;flex-wrap:wrap;">
            <div style="flex:1;min-width:160px;background:#141708;border:1px solid rgba(196,228,56,0.3);
                        border-radius:8px;padding:14px 16px;">
                <div style="font-size:11px;color:#7a8a50;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">Objetivo</div>
                <div style="font-size:15px;font-weight:700;color:#c4e438;">{obj_label}</div>
            </div>
            <div style="flex:1;min-width:140px;background:#141708;border:1px solid rgba(196,228,56,0.3);
                        border-radius:8px;padding:14px 16px;">
                <div style="font-size:11px;color:#7a8a50;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">Nivel</div>
                <div style="font-size:15px;font-weight:700;color:#c4e438;">{niv_label}</div>
            </div>
            <div style="flex:1;min-width:120px;background:#141708;border:1px solid rgba(196,228,56,0.3);
                        border-radius:8px;padding:14px 16px;">
                <div style="font-size:11px;color:#7a8a50;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">Frecuencia</div>
                <div style="font-size:15px;font-weight:700;color:#c4e438;">{dias} días/sem</div>
            </div>
            <div style="flex:1;min-width:160px;background:#141708;border:1px solid rgba(196,228,56,0.3);
                        border-radius:8px;padding:14px 16px;">
                <div style="font-size:11px;color:#7a8a50;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">Equipo</div>
                <div style="font-size:15px;font-weight:700;color:#c4e438;">{eq_label}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Nota de fase del ciclo
        if fase:
            fase_estilos = {
                "Menstrual":  {"bg":"#3d0f0f","border":"#8b2020","text":"#ff9090","badge":"#8b2020"},
                "Folicular":  {"bg":"#0f3d1a","border":"#208b40","text":"#90ff90","badge":"#208b40"},
                "Ovulatoria": {"bg":"#3d3800","border":"#8b8000","text":"#ffe060","badge":"#8b8000"},
                "Lútea":      {"bg":"#2d1a4d","border":"#6020a0","text":"#c090ff","badge":"#6020a0"},
            }
            es = fase_estilos.get(fase["nombre"], {"bg":"#1a1a12","border":"#c4e438","text":"#c4e438","badge":"#444"})
            st.markdown(f"""
            <div style="background:{es['bg']};border:1px solid {es['border']};border-left:4px solid {es['border']};
                        border-radius:8px;padding:14px 18px;margin:12px 0;">
                <div style="font-size:16px;font-weight:700;color:{es['text']};margin-bottom:4px;">
                    {fase['emoji']} Fase {fase['nombre']} — Día {fase['dia']}
                </div>
                <div style="font-size:13px;color:{es['text']};opacity:0.85;">{fase['nota']}</div>
            </div>""", unsafe_allow_html=True)

        st.divider()

        # Obtener estructura según días disponibles
        dias_key = min(dias, 6)
        dias_key = max(dias_key, 2)
        estructura = ESTRUCTURAS.get(dias_key, ESTRUCTURAS[3])

        st.subheader(f"📅 Programa semanal — {dias} días")
        st.caption(f"Series × Reps objetivo: **{rep_scheme}** · Descanso entre series: **{descanso}**")

        for i, dia_info in enumerate(estructura):
            with st.expander(f"{dia_info['nombre']}", expanded=(i == 0)):

                # ── Nota de fase del ciclo ────────────────────────────────
                if fase:
                    intensidad = fase["intensidad"]
                    nota_fase = ""
                    if intensidad < 0.8:
                        nota_fase = "💜 Reduce el peso un 20-30% hoy según tu fase del ciclo."
                    elif intensidad > 1.0:
                        nota_fase = "⚡ ¡Hoy puedes dar el máximo! Excelente día para nuevos récords."
                    if nota_fase:
                        st.caption(nota_fase)

                # ── Workout sugerido para el día ──────────────────────────
                workout_dia = recomendar_workout_dia(dia_info["grupos"])
                if workout_dia:
                    st.markdown("#### 🎬 Workout guiado sugerido para hoy")
                    col_wd1, col_wd2 = st.columns([3, 1])
                    with col_wd1:
                        st.caption(
                            f"👩‍💻 **{workout_dia['coach']}** · ⏱ {workout_dia['duracion']} · "
                            f"🏋️ {workout_dia['equipo']}")
                        st.caption(
                            f"_{workout_dia['descripcion']}_")
                        st.caption(
                            "💡 Síguelo completo **o** úsalo de calentamiento antes del plan de abajo.")
                    with col_wd2:
                        st.markdown(
                            f'<div style="background:#0f3d1a;border-radius:6px;padding:8px;'
                            f'text-align:center;font-size:11px;font-weight:600;color:#90ff90;">'
                            f'WORKOUT<br>GUIADO</div>', unsafe_allow_html=True)
                    st.video(f"https://www.youtube.com/watch?v={workout_dia['video_id']}")
                    st.divider()

                # ── Plan de ejercicios del día ────────────────────────────
                st.markdown(f"#### 💪 Plan de ejercicios · {', '.join(dia_info['grupos'])}")
                st.caption(f"📊 {rep_scheme} · ⏱ {descanso} descanso entre series")

                ejercicios_dia = []
                for grupo in dia_info["grupos"]:
                    ejs = filtrar_ejercicios(grupo, equipo_lista, lesiones,
                                              max_ej=2 if len(dia_info["grupos"]) > 3 else 3)
                    ejercicios_dia.extend(ejs)

                if not ejercicios_dia:
                    st.warning("No hay ejercicios disponibles para tu equipo en este día.")
                    continue

                for ej in ejercicios_dia:
                    dif_color = {"principiante":"#0f3d1a","intermedio":"#3d3800",
                                 "avanzado":"#3d0f0f"}.get(ej["dificultad"],"#141708")
                    dif_text  = {"principiante":"#90ff90","intermedio":"#ffe060",
                                 "avanzado":"#ff9090"}.get(ej["dificultad"],"#c4e438")

                    col_ej, col_vt = st.columns([5, 1])
                    with col_ej:
                        st.markdown(
                            f"**{ej['nombre']}** &nbsp;"
                            f"{badge(ej['grupo'], '#1a2040')} &nbsp;"
                            f'<span style="background:{dif_color};color:{dif_text};'
                            f'font-size:10px;padding:2px 7px;border-radius:8px;'
                            f'font-weight:600;">{ej["dificultad"]}</span>',
                            unsafe_allow_html=True)
                        st.caption(ej["descripcion"][:130] + "…" if len(ej["descripcion"]) > 130 else ej["descripcion"])
                    with col_vt:
                        vid_id = _EJ_VIDEOS.get(ej.get("id",""))
                        if vid_id:
                            st.link_button("▶ Tutorial",
                                f"https://www.youtube.com/watch?v={vid_id}",
                                use_container_width=True)
                        elif ej.get("url"):
                            st.link_button("🔍 Ver", ej["url"], use_container_width=True)

                    # Tutorial embebido expandible
                    vid_id = _EJ_VIDEOS.get(ej.get("id",""))
                    if vid_id:
                        with st.expander(f"🎬 Tutorial: {ej['nombre']}", expanded=False):
                            st.video(f"https://www.youtube.com/watch?v={vid_id}")
                    st.markdown("---")

        # Registro de sesión
        st.divider()
        with st.expander("✍️ Registrar sesión de hoy"):
            col_r1, col_r2 = st.columns(2)
            with col_r1:
                dia_sel  = st.selectbox("Día entrenado", [d["nombre"] for d in estructura])
                ej_sel   = st.text_input("Ejercicio principal")
                series_r = st.number_input("Series", 1, 10, 3)
            with col_r2:
                reps_r   = st.text_input("Reps (ej: 10, 10, 8)")
                peso_r   = st.number_input("Peso (lbs)", 0.0, 500.0, 0.0, 2.5)
                notas_r  = st.text_input("Notas")
            if st.button("💾 Guardar sesión", type="primary"):
                try:
                    guardar_fila_usuario("rutinas_sesiones", [
                        str(date.today()), dia_sel, ej_sel,
                        series_r, reps_r, peso_r, notas_r
                    ], uid)
                    st.success("✅ Sesión registrada.")
                except Exception as e:
                    st.error(f"Error: {e}")


    # ══════════════════════════════════════════════════════════════════════════
    # TAB 4 — EJERCICIOS
    # ══════════════════════════════════════════════════════════════════════════
    with tab4:
        st.subheader("💪 Biblioteca de ejercicios")
        st.caption("Videos cortos (<4 min) priorizando coaches top: Bret Contreras · Jeff Nippard · Squat University · Heather Robertson")

        grupos_disponibles = sorted(set(e["grupo"] for e in EJERCICIOS_BASE))
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            grupo_filtro = st.selectbox("Grupo muscular", ["Todos"] + grupos_disponibles)
        with col_f2:
            dif_filtro = st.selectbox("Dificultad", ["Todos","principiante","intermedio","avanzado"])
        with col_f3:
            solo_mi_equipo = st.checkbox("Solo mi equipo", value=True)

        ejercicios_filtrados = EJERCICIOS_BASE.copy()
        if grupo_filtro != "Todos":
            ejercicios_filtrados = [e for e in ejercicios_filtrados if e["grupo"] == grupo_filtro]
        if dif_filtro != "Todos":
            ejercicios_filtrados = [e for e in ejercicios_filtrados if e["dificultad"] == dif_filtro]
        if solo_mi_equipo and equipo_lista:
            ejercicios_filtrados = [e for e in ejercicios_filtrados
                                     if any(eq in equipo_lista for eq in e["equipo"])]

        st.caption(f"{len(ejercicios_filtrados)} ejercicio(s) encontrado(s)")
        st.divider()

        for ej in ejercicios_filtrados:
            with st.expander(f"**{ej['nombre']}** — {ej['grupo']}"):
                col_d, col_v = st.columns([4, 1])
                with col_d:
                    dif_color = {"principiante":"#dcfce7","intermedio":"#fef9c3","avanzado":"#fee2e2"}.get(ej["dificultad"],"#f1f5f9")
                    st.markdown(
                        f"{badge(ej['grupo'],'#e0e7ff')} &nbsp;"
                        f"{badge(ej['dificultad'], dif_color)} &nbsp;"
                        f"{badge(', '.join(ej['equipo'][:2]),'#f1f5f9')}",
                        unsafe_allow_html=True)
                    st.markdown(f"**Técnica:** {ej['descripcion']}")
                    if ej.get("coach"):
                        st.caption(f"👩‍💻 Coach recomendado: {ej['coach']}")
                    if lesiones and any(l in ej.get("lesiones_evitar", []) for l in lesiones):
                        st.warning("⚠️ Este ejercicio puede agravar tus lesiones reportadas.")
                with col_v:
                    vid_id = _EJ_VIDEOS.get(ej["id"])
                    if vid_id:
                        st.video(f"https://www.youtube.com/watch?v={vid_id}")
                    elif ej.get("url"):
                        st.link_button("🔍 Buscar tutorial", ej["url"], use_container_width=True)

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 5 — COACHES
    # ══════════════════════════════════════════════════════════════════════════
    with tab5:
        st.subheader("👩‍💻 Coaches recomendados")
        obj_limpio = obj.lower()
        areas_recomendadas = coaches_por_objetivo(obj_limpio)

        if not areas_recomendadas:
            areas_recomendadas = list(COACHES.keys())

        for area_key in areas_recomendadas:
            area = COACHES.get(area_key)
            if not area:
                continue
            st.markdown(f"### {area['emoji']} {area['nombre_area']}")
            for coach in area["coaches"]:
                with st.container():
                    col_c, col_l = st.columns([5, 1])
                    with col_c:
                        st.markdown(f"**{coach['nombre']}** &nbsp; {badge(coach['idioma'],'#f1f5f9')} &nbsp; {badge(coach['highlight'],'#e0e7ff')}",
                                    unsafe_allow_html=True)
                        st.caption(coach["descripcion"])
                        niv_str = " · ".join(coach["nivel"])
                        st.caption(f"Nivel: {niv_str}")
                    with col_l:
                        st.link_button("Canal ▶", coach["canal"], use_container_width=True)
                    st.markdown("---")
            st.divider()
    # ══════════════════════════════════════════════════════════════════════════
    # TAB 3 — PROGRAMA IA (Google Gemini)
    # ══════════════════════════════════════════════════════════════════════════
    with tab3:
        st.subheader("🤖 Programa Personalizado con IA")
        st.caption("Ingresa los resultados de tu evaluación corporal profesional y la IA generará un programa completamente personalizado.")

        # Verificar API key
        try:
            from utils.gemini import get_api_key, consultar_gemini, construir_prompt_programa
            api_key = get_api_key()
            tiene_api = bool(api_key)
        except Exception:
            tiene_api = False

        if not tiene_api:
            st.warning("⚙️ **API de Gemini no configurada.** Agrega `GEMINI_API_KEY` en los Secrets de Streamlit Cloud.")
            st.code('''# En Streamlit Cloud → Settings → Secrets, agrega:
GEMINI_API_KEY = "tu-api-key-aqui"

# Obtén tu API key gratis en:
# https://aistudio.google.com/app/apikey''')
            st.info("La API de Gemini es **completamente gratuita** hasta 1 millón de tokens/día. No requiere tarjeta de crédito.")
        else:
            st.success("✅ Gemini API configurada y lista.")

        st.divider()

        col_form, col_tips = st.columns([3, 1])
        with col_tips:
            st.markdown("**💡 Tips para mejores resultados:**")
            st.caption("• Incluye los hallazgos del profesional lo más detallado posible")
            st.caption("• Menciona desequilibrios musculares específicos")
            st.caption("• Si tienes resultados de postura, inclúyelos")
            st.caption("• El programa se adapta a tu equipo y horario de tu evaluación")

        with col_form:
            evaluacion_corporal = st.text_area(
                "📋 Resultados de tu evaluación corporal",
                placeholder="""Ejemplo:
- Hombro derecho más alto que el izquierdo (escoliosis leve)
- Glúteo medio débil bilateralmente
- Isquiotibiales tensos, especialmente pierna derecha
- Core débil, tendencia a hiperextensión lumbar
- Cuádriceps dominantes sobre glúteos en sentadilla
- Postura: cabeza adelantada, hombros redondeados""",
                height=180,
                key="eval_corp"
            )

            prioridades = st.multiselect(
                "🎯 Prioridades identificadas en la evaluación",
                ["Activación de glúteo medio", "Fuerza de core", "Estabilidad lumbar",
                 "Corrección postural", "Equilibrio muscular (Der/Izq)", "Movilidad de caderas",
                 "Fuerza de isquiotibiales", "Estabilidad de hombros", "Movilidad torácica",
                 "Fuerza de cuádriceps", "Flexibilidad general", "Control motor",
                 "Resistencia cardiovascular", "Potencia explosiva"],
                key="prioridades_ia"
            )

            notas_adicionales = st.text_input(
                "📝 Notas adicionales o metas específicas (opcional)",
                placeholder="Ej: quiero mejorar mi postura para el trabajo en escritorio",
                key="notas_ia"
            )

        st.divider()

        if st.button("⚡ Generar programa personalizado con IA",
                      type="primary", use_container_width=True,
                      disabled=not tiene_api):
            if not evaluacion_corporal.strip() and not prioridades:
                st.warning("Ingresa al menos los resultados de la evaluación o selecciona prioridades.")
            else:
                eval_completa = evaluacion_corporal
                if notas_adicionales:
                    eval_completa += f"\n\nNotas adicionales: {notas_adicionales}"

                with st.spinner("🧠 Generando tu programa personalizado... (10-20 segundos)"):
                    try:
                        perfil = {
                            "genero":        estado.get("genero", "Mujer"),
                            "eval_objetivo": estado.get("eval_objetivo", ""),
                            "eval_nivel":    estado.get("eval_nivel", ""),
                            "eval_dias":     estado.get("eval_dias", 3),
                            "eval_duracion": estado.get("eval_duracion", "60 min"),
                            "eval_equipo":   estado.get("eval_equipo", ""),
                            "eval_lesiones": estado.get("eval_lesiones", ""),
                            "med_peso":      estado.get("med_peso", ""),
                            "med_altura":    estado.get("med_altura", ""),
                            "nombre_usuario":st.session_state.get("nombre_usuario", ""),
                        }
                        prompt   = construir_prompt_programa(perfil, eval_completa, prioridades)
                        programa = consultar_gemini(prompt)

                        st.success("✅ ¡Programa generado!")
                        st.divider()

                        # Mostrar resultado con formato bonito
                        st.markdown(f"""
<div style="background:#141708;border:1px solid rgba(196,228,56,0.3);
            border-radius:10px;padding:24px;line-height:1.7;">
{programa.replace(chr(10), "<br>")}
</div>""", unsafe_allow_html=True)

                        st.divider()

                        # Guardar en Sheets
                        try:
                            from utils.sheets import guardar_fila_usuario
                            guardar_fila_usuario("evaluaciones_ia", [
                                str(date.today()),
                                evaluacion_corporal[:500],
                                ", ".join(prioridades),
                                programa[:2000]
                            ], uid)
                            st.caption("💾 Programa guardado en tu historial.")
                        except Exception:
                            pass  # No bloquear si falla el guardado

                        # Botón de descarga
                        st.download_button(
                            "⬇️ Descargar programa como texto",
                            data=programa,
                            file_name=f"programa_ia_{date.today()}.txt",
                            mime="text/plain"
                        )

                    except ValueError as e:
                        if "GEMINI_API_KEY" in str(e):
                            st.error("❌ API key no configurada.")
                        else:
                            st.error(f"❌ Error: {e}")
                    except ConnectionError as e:
                        st.error(f"❌ Error de conexión con Gemini: {e}")
                    except Exception as e:
                        st.error(f"❌ Error inesperado: {e}")
                        st.exception(e)
    # ══════════════════════════════════════════════════════════════════════════
    # TAB 2 — WORKOUTS COMPLETOS
    # Base: videos curados en código | Enriquecida: videos agregados desde la app
    # ══════════════════════════════════════════════════════════════════════════
    with tab2:
        st.subheader("🎬 Workouts Completos")
        st.caption("Biblioteca base curada + tus videos favoritos guardados desde la app.")

        # ── Cargar videos desde Google Sheets (biblioteca personal) ───────────
        videos_personales = {}
        try:
            from utils.sheets import leer_df_usuario
            df_vids = leer_df_usuario("videos_workouts", uid)
            if not df_vids.empty:
                activos = df_vids[df_vids.get("activo", "si").astype(str).str.lower() == "si"]
                for _, row in activos.iterrows():
                    cat = str(row.get("categoria", "📌 Mis Videos"))
                    if cat not in videos_personales:
                        videos_personales[cat] = []
                    videos_personales[cat].append({
                        "titulo":     str(row.get("titulo",     "")),
                        "coach":      str(row.get("coach",      "")),
                        "duracion":   str(row.get("duracion",   "")),
                        "nivel":      str(row.get("nivel",      "Intermedio")),
                        "equipo":     str(row.get("equipo",     "")),
                        "descripcion":str(row.get("descripcion","")),
                        "video_id":   str(row.get("video_id",   "")),
                        "busqueda":   str(row.get("titulo",     "")),
                        "desde_sheets": True,
                        "fila_sheets": int(row.get("_fila_sheets", 0)),
                    })
        except Exception:
            pass

        # Combinar: base + personales
        todos_los_workouts = {**WORKOUTS_DB}
        for cat, vids in videos_personales.items():
            if cat in todos_los_workouts:
                todos_los_workouts[cat] = todos_los_workouts[cat] + vids
            else:
                todos_los_workouts[cat] = vids

        # ── Filtros ───────────────────────────────────────────────────────────
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            cat_sel = st.selectbox("Categoría", ["Todas"] + list(todos_los_workouts.keys()),
                                    key="cat_w")
        with col_f2:
            niv_sel = st.selectbox("Nivel", ["Todos","Principiante","Intermedio","Avanzado"],
                                    key="niv_w")

        total_videos = sum(len(v) for v in todos_los_workouts.values())
        personales_count = sum(len(v) for v in videos_personales.values())
        st.caption(f"📚 {total_videos} videos en biblioteca · {personales_count} agregados por ti")
        st.divider()

        # ── Mostrar videos ────────────────────────────────────────────────────
        cats_mostrar = list(todos_los_workouts.keys()) if cat_sel == "Todas" else [cat_sel]

        for cat in cats_mostrar:
            videos = todos_los_workouts.get(cat, [])
            if niv_sel != "Todos":
                videos = [v for v in videos if v.get("nivel") == niv_sel]
            if not videos:
                continue

            st.markdown(f"### {cat}")

            for vid in videos:
                with st.container():
                    col_info, col_badge = st.columns([4, 1])
                    with col_info:
                        tag_personal = " 🌟 *Mi biblioteca*" if vid.get("desde_sheets") else ""
                        st.markdown(f"**{vid['titulo']}**{tag_personal}")
                        st.caption(f"👩‍💻 {vid['coach']}  ·  ⏱ {vid['duracion']}  ·  🏋️ {vid['equipo']}")
                        if vid.get("descripcion"):
                            st.caption(vid["descripcion"])
                    with col_badge:
                        niv_color = {"Principiante":"#0f3d1a","Intermedio":"#3d3800",
                                     "Avanzado":"#3d0f0f"}.get(vid.get("nivel",""),"#141708")
                        st.markdown(
                            f'<div style="background:{niv_color};border-radius:6px;'
                            f'padding:6px 10px;text-align:center;font-size:12px;'
                            f'font-weight:600;">{vid.get("nivel","")}</div>',
                            unsafe_allow_html=True)
                        # Botón eliminar solo para videos personales
                        if vid.get("desde_sheets") and vid.get("fila_sheets"):
                            if st.button("🗑️", key=f"del_vid_{vid['fila_sheets']}",
                                          help="Eliminar de mi biblioteca"):
                                try:
                                    from utils.sheets import eliminar_fila_sheets
                                    eliminar_fila_sheets("videos_workouts", vid["fila_sheets"])
                                    st.success("Eliminado.")
                                    st.rerun()
                                except Exception as ex:
                                    st.error(f"Error: {ex}")

                    # Embed video
                    if vid.get("video_id"):
                        video_url = f"https://www.youtube.com/watch?v={vid['video_id']}"
                        try:
                            st.video(video_url)
                        except Exception:
                            busqueda = vid.get("busqueda","").replace(" ","+")
                            st.link_button("🔍 Buscar en YouTube",
                                f"https://www.youtube.com/results?search_query={busqueda}",
                                use_container_width=True)
                    st.markdown("---")

        # ── Agregar video nuevo ───────────────────────────────────────────────
        st.divider()
        with st.expander("➕ Agregar video a mi biblioteca", expanded=False):
            st.caption("Pega la URL de YouTube o el ID del video. Se guarda en tu cuenta.")

            url_input = st.text_input("URL o ID del video de YouTube",
                placeholder="https://www.youtube.com/watch?v=... o el ID directo (ej: Emu7uB59E2g)")

            # Preview del video
            video_id_preview = None
            if url_input.strip():
                import re
                url = url_input.strip()
                for pattern in [r'v=([a-zA-Z0-9_-]{11})', r'youtu\.be/([a-zA-Z0-9_-]{11})',
                                 r'embed/([a-zA-Z0-9_-]{11})', r'^([a-zA-Z0-9_-]{11})$']:
                    m = re.search(pattern, url)
                    if m:
                        video_id_preview = m.group(1)
                        break

                if video_id_preview:
                    st.success(f"✅ Video ID detectado: `{video_id_preview}`")
                    st.video(f"https://www.youtube.com/watch?v={video_id_preview}")
                else:
                    st.warning("No se pudo extraer el ID. Verifica la URL.")

            col_a1, col_a2 = st.columns(2)
            with col_a1:
                v_titulo   = st.text_input("Título del video", key="v_tit")
                v_coach    = st.text_input("Coach / Canal", key="v_coach",
                                            placeholder="Ej: Heather Robertson")
                v_duracion = st.text_input("Duración", key="v_dur",
                                            placeholder="Ej: 20 min")
            with col_a2:
                cats_existentes = list(todos_los_workouts.keys()) + ["📌 Mis Videos", "🔧 Otra categoría"]
                v_cat = st.selectbox("Categoría", cats_existentes, key="v_cat")
                if v_cat == "🔧 Otra categoría":
                    v_cat = st.text_input("Nueva categoría", key="v_cat_nueva")
                v_nivel   = st.selectbox("Nivel", ["Principiante","Intermedio","Avanzado"], key="v_niv")
                v_equipo  = st.text_input("Equipo necesario", key="v_eq",
                                           placeholder="Ej: Sin equipo / Mancuernas")

            v_desc = st.text_area("Descripción breve", key="v_desc",
                                   placeholder="¿Qué trabaja este video?", height=70)

            if st.button("💾 Guardar en mi biblioteca", type="primary",
                          use_container_width=True):
                if not video_id_preview:
                    st.error("❌ Ingresa una URL válida de YouTube.")
                elif not v_titulo.strip():
                    st.error("❌ Ingresa un título para el video.")
                else:
                    try:
                        from utils.sheets import guardar_fila_usuario
                        guardar_fila_usuario("videos_workouts", [
                            v_cat, v_titulo.strip(), v_coach.strip(),
                            v_duracion.strip(), v_nivel, v_equipo.strip(),
                            v_desc.strip(), video_id_preview, "si",
                            str(date.today())
                        ], uid)
                        st.success(f"✅ '{v_titulo}' guardado en tu biblioteca.")
                        st.rerun()
                    except Exception as ex:
                        st.error(f"Error al guardar: {ex}")

