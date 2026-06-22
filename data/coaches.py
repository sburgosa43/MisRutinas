"""
Base de datos de coaches y canales de YouTube organizados por objetivo y tipo de ejercicio.
"""

COACHES = {
    "glúteos_cadera": {
        "nombre_area": "Glúteos & Cadera",
        "emoji": "🍑",
        "coaches": [
            {"nombre": "Bret Contreras (Glute Lab)", "canal": "https://www.youtube.com/@BretContreras1",
             "descripcion": "El mayor experto mundial en glúteos. Inventor del Hip Thrust. Base científica total.",
             "nivel": ["intermedio", "avanzado"], "idioma": "Inglés", "highlight": "🔬 Evidencia científica"},
            {"nombre": "Stephanie Sanzo", "canal": "https://www.youtube.com/@StephanieSanzo",
             "descripcion": "Programas de fuerza e hipertrofia con énfasis en piernas y glúteos.",
             "nivel": ["principiante", "intermedio", "avanzado"], "idioma": "Inglés", "highlight": "💪 Muy completo"},
            {"nombre": "Juan Suárez Fitness", "canal": "https://www.youtube.com/@JuanSuarezFitness",
             "descripcion": "Glúteos y entrenamiento femenino en español, basado en evidencia.",
             "nivel": ["principiante", "intermedio"], "idioma": "Español 🇪🇸", "highlight": "🇪🇸 En español"},
        ],
    },
    "hipertrofia_ciencia": {
        "nombre_area": "Hipertrofia & Ciencia",
        "emoji": "🧠",
        "coaches": [
            {"nombre": "Jeff Nippard", "canal": "https://www.youtube.com/@JeffNippard",
             "descripcion": "El mejor canal científico de hipertrofia. Cita estudios en cada video. Imprescindible.",
             "nivel": ["intermedio", "avanzado"], "idioma": "Inglés", "highlight": "🔬 #1 en ciencia"},
            {"nombre": "Jeremy Ethier (Built With Science)", "canal": "https://www.youtube.com/@JeremyEthier",
             "descripcion": "Programas basados en ciencia con excelente producción. Muy pedagógico.",
             "nivel": ["principiante", "intermedio", "avanzado"], "idioma": "Inglés", "highlight": "📊 Muy pedagógico"},
            {"nombre": "Renaissance Periodization", "canal": "https://www.youtube.com/@RenaissancePeriodization",
             "descripcion": "Referencia mundial en periodización y volumen óptimo por músculo (Dr. Mike Israetel).",
             "nivel": ["avanzado"], "idioma": "Inglés", "highlight": "🏆 Referencia mundial"},
        ],
    },
    "rutinas_casa": {
        "nombre_area": "Rutinas en Casa",
        "emoji": "🏠",
        "coaches": [
            {"nombre": "Heather Robertson", "canal": "https://www.youtube.com/@HeatherRobertson",
             "descripcion": "La mejor para rutinas en casa. Miles de videos gratis de HIIT, fuerza y cardio.",
             "nivel": ["principiante", "intermedio"], "idioma": "Inglés", "highlight": "🏆 La mejor en casa"},
            {"nombre": "Sydney Cummings Houdyshell", "canal": "https://www.youtube.com/@SydneyCummings",
             "descripcion": "Variedad enorme: HIIT, fuerza, cardio. Muy motivadora. Videos diarios.",
             "nivel": ["principiante", "intermedio", "avanzado"], "idioma": "Inglés", "highlight": "🔥 Super motivadora"},
            {"nombre": "Pamela Reif", "canal": "https://www.youtube.com/@PamelaRf1",
             "descripcion": "Rutinas cortas e intensas en casa. Muy popular para abdomen y full body.",
             "nivel": ["principiante", "intermedio"], "idioma": "Sin habla (música)", "highlight": "⚡ Rutinas cortas"},
        ],
    },
    "movilidad_yoga": {
        "nombre_area": "Movilidad, Yoga & Recuperación",
        "emoji": "🧘",
        "coaches": [
            {"nombre": "Yoga with Adriene", "canal": "https://www.youtube.com/@yogawithadriene",
             "descripcion": "La coach de yoga más reconocida. Perfecta para recuperación y días de baja energía.",
             "nivel": ["principiante", "intermedio"], "idioma": "Inglés", "highlight": "🌟 #1 yoga YouTube"},
            {"nombre": "MommaStrong", "canal": "https://www.youtube.com/@MommaStrong",
             "descripcion": "Especialista en suelo pélvico, core profundo y salud femenina.",
             "nivel": ["principiante", "intermedio"], "idioma": "Inglés", "highlight": "💆 Salud femenina"},
        ],
    },
    "recomposicion_femenina": {
        "nombre_area": "Recomposición Corporal Femenina",
        "emoji": "✨",
        "coaches": [
            {"nombre": "Lauren Gleisberg", "canal": "https://www.youtube.com/@LaurenGleisberg",
             "descripcion": "Especialista en transformación femenina. Programas de recomposición con pesas.",
             "nivel": ["principiante", "intermedio"], "idioma": "Inglés", "highlight": "👩 Especialista femenina"},
            {"nombre": "Stephanie Buttermore", "canal": "https://www.youtube.com/@StephanieButtermore",
             "descripcion": "PhD en ciencias. Mezcla ciencia y entrenamiento femenino de forma excepcional.",
             "nivel": ["intermedio", "avanzado"], "idioma": "Inglés", "highlight": "🔬 PhD + atleta"},
        ],
    },
    "fuerza_tecnica": {
        "nombre_area": "Técnica & Biomecánica",
        "emoji": "🏋️",
        "coaches": [
            {"nombre": "Squat University", "canal": "https://www.youtube.com/@SquatUniversity",
             "descripcion": "El mejor recurso de biomecánica. Imprescindible para buena técnica en sentadilla, peso muerto y press.",
             "nivel": ["principiante", "intermedio", "avanzado"], "idioma": "Inglés", "highlight": "🎓 Biomecánica #1"},
            {"nombre": "Alan Thrall", "canal": "https://www.youtube.com/@AlanThrall",
             "descripcion": "Técnica de levantamientos básicos explicada de forma muy clara y directa.",
             "nivel": ["principiante", "intermedio"], "idioma": "Inglés", "highlight": "📐 Técnica clara"},
        ],
    },
}


def coaches_por_objetivo(objetivo: str) -> list:
    obj = objetivo.lower()
    if "recomposición" in obj or "recomposicion" in obj:
        return ["glúteos_cadera", "rutinas_casa", "recomposicion_femenina", "movilidad_yoga"]
    elif "grasa" in obj or "pérdida" in obj:
        return ["rutinas_casa", "glúteos_cadera", "movilidad_yoga"]
    elif "músculo" in obj or "hipertrofia" in obj:
        return ["hipertrofia_ciencia", "glúteos_cadera", "fuerza_tecnica"]
    elif "fuerza" in obj:
        return ["fuerza_tecnica", "hipertrofia_ciencia", "glúteos_cadera"]
    else:
        return ["rutinas_casa", "movilidad_yoga", "glúteos_cadera"]
