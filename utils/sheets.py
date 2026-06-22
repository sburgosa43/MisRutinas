import json
import gspread
import streamlit as st
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

SPREADSHEET_ID = "15nvtf4jxjq7yU-AZctGXnYst22BpgdFbX8gKQS71imM"

SHEETS_CONFIG = {
    "medidas": [
        "fecha", "edad", "peso_lbs", "altura_cm",
        "cintura_cm", "cadera_cm", "muslo_der_cm", "muslo_izq_cm",
        "brazo_der_cm", "brazo_izq_cm", "hombros_cm",
        "imc", "rcc", "rel_hombros_cintura", "notas"
    ],
    "evaluacion": [
        "fecha", "parq_resultado", "objetivo", "nivel", "zonas_enfoque",
        "dias_semana", "duracion_sesion", "momento_entreno", "equipo",
        "lesiones", "detalle_lesiones", "horas_sueno", "nivel_estres",
        "trabajo_sedentario", "agua_litros"
    ],
    "ciclo": ["fecha_inicio", "duracion_dias", "notas"],
    "rutinas_sesiones": [
        "fecha", "tipo_rutina", "ejercicio", "series", "reps", "peso_lbs", "notas"
    ],
    "config": ["clave", "valor"],
    "ejercicios": ["id", "nombre", "grupo_muscular", "descripcion", "url_youtube", "dificultad", "activo"],
}


def get_client():
    try:
        credentials_info = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
    except KeyError:
        credentials_info = dict(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(credentials_info, scopes=SCOPES)
    return gspread.authorize(creds)


def get_spreadsheet():
    client = get_client()
    try:
        return client.open_by_key(SPREADSHEET_ID)
    except Exception as e:
        st.error(f"Error abriendo spreadsheet: {e}")
        raise


def get_worksheet(nombre: str):
    sh = get_spreadsheet()
    try:
        return sh.worksheet(nombre)
    except gspread.WorksheetNotFound:
        headers = SHEETS_CONFIG.get(nombre, [])
        ws = sh.add_worksheet(title=nombre, rows=1000, cols=max(len(headers), 5))
        if headers:
            ws.append_row(headers)
            ws.format("1:1", {"textFormat": {"bold": True}})
        return ws


def leer_como_dataframe(nombre: str):
    import pandas as pd
    ws = get_worksheet(nombre)
    return pd.DataFrame(ws.get_all_records())
