"""
Integración con Google Gemini API (gratuita).
Modelo: gemini-1.5-flash — 15 requests/min, 1M tokens/día gratis.
Documentación: https://aistudio.google.com
"""
import requests
import streamlit as st

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"


def get_api_key() -> str | None:
    try:
        return st.secrets["GEMINI_API_KEY"]
    except Exception:
        return None


def consultar_gemini(prompt: str) -> str:
    """Llama a Gemini y retorna el texto generado."""
    api_key = get_api_key()
    if not api_key:
        raise ValueError("GEMINI_API_KEY no configurada en secrets.")

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 3000,
            "topP": 0.9,
        },
        "safetySettings": [
            {"category": "HARM_CATEGORY_HARASSMENT",       "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH",      "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT","threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT","threshold": "BLOCK_NONE"},
        ]
    }

    resp = requests.post(f"{GEMINI_URL}?key={api_key}", json=payload, timeout=60)

    if resp.status_code != 200:
        raise ConnectionError(f"Error Gemini API ({resp.status_code}): {resp.text[:300]}")

    data = resp.json()
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError) as e:
        raise ValueError(f"Respuesta inesperada de Gemini: {data}") from e


def construir_prompt_programa(perfil: dict, evaluacion_corporal: str, prioridades: list) -> str:
    """Construye el prompt científico para generar el programa personalizado."""
    genero    = perfil.get("genero",        "Mujer")
    objetivo  = perfil.get("eval_objetivo", "Recomposición corporal")
    nivel     = perfil.get("eval_nivel",    "Principiante")
    dias      = perfil.get("eval_dias",     3)
    duracion  = perfil.get("eval_duracion", "60 min")
    equipo    = perfil.get("eval_equipo",   "Equipo básico")
    lesiones  = perfil.get("eval_lesiones", "Ninguna")
    peso      = perfil.get("med_peso",      "—")
    altura    = perfil.get("med_altura",    "—")
    nombre    = perfil.get("nombre_usuario","el usuario")

    prios_str = "\n".join(f"  • {p}" for p in prioridades) if prioridades else "  • No especificadas"
    eval_str  = evaluacion_corporal.strip() if evaluacion_corporal.strip() else "No proporcionada por el profesional."

    return f"""Eres un entrenador personal de élite certificado (NSCA-CPT, CSCS) con especialización en:
- Recomposición corporal femenina (metodología Bret Contreras)
- Biomecánica y corrección postural (Stuart McGill, Squat University)
- Periodización basada en evidencia (Brad Schoenfeld, Mike Israetel)
- Adaptación de entrenamiento al ciclo menstrual (McNulty et al. 2020)

════════════════════════════════════════
PERFIL COMPLETO DE {nombre.upper()}
════════════════════════════════════════
Género:              {genero}
Objetivo principal:  {objetivo}
Nivel de experiencia:{nivel}
Frecuencia semanal:  {dias} días de entrenamiento
Duración por sesión: {duracion}
Equipo disponible:   {equipo}
Peso actual:         {peso} lbs
Altura:              {altura} cm
Lesiones/Limitaciones: {lesiones}

RESULTADOS DE EVALUACIÓN CORPORAL PROFESIONAL:
{eval_str}

PRIORIDADES IDENTIFICADAS EN LA EVALUACIÓN:
{prios_str}

════════════════════════════════════════
GENERA EL SIGUIENTE PROGRAMA:
════════════════════════════════════════

**1. ANÁLISIS DE LA EVALUACIÓN** (4-5 oraciones)
Interpreta los hallazgos, identifica desequilibrios musculares clave y explica cómo impactan el rendimiento y la composición corporal.

**2. TIPO DE PROGRAMA Y JUSTIFICACIÓN**
Indica el split recomendado (Full Body / Upper-Lower / PPL) y por qué es el más adecuado para este perfil específico.

**3. PROGRAMA SEMANAL COMPLETO**
Para cada día de entrenamiento:
- Título del día y grupos musculares trabajados
- Lista de ejercicios con: Series × Repeticiones, Descanso entre series, RPE o % del 1RM recomendado
- 1-2 notas técnicas clave para los ejercicios más importantes

**4. PROTOCOLO DE PROGRESIÓN (4-6 semanas)**
Cómo debe evolucionar el volumen, la carga y la intensidad semana a semana.

**5. RECOMENDACIONES ESPECÍFICAS PARA LAS PRIORIDADES**
Estrategias concretas para abordar cada prioridad identificada en la evaluación corporal.

**6. EJERCICIOS A MODIFICAR O EVITAR**
Basándote en las lesiones y limitaciones reportadas.

Responde en español. Usa lenguaje técnico pero accesible. Sé específico y práctico.
Usa evidencia científica donde sea relevante. Formato con headers en negrita."""
