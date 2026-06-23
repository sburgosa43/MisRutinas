import json
import gspread
import streamlit as st
import pandas as pd
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

SPREADSHEET_ID = "15nvtf4jxjq7yU-AZctGXnYst22BpgdFbX8gKQS71imM"

SHEETS_CONFIG = {
    "usuarios": ["id","nombre","pin","fecha_registro","activo"],
    "medidas": [
        "user_id","fecha","genero","fecha_nacimiento","edad_calculada",
        "peso_lbs","altura_cm","hombros_cm","pecho_cm","cintura_cm","cadera_cm",
        "muslo_der_cm","muslo_izq_cm","brazo_der_cm","brazo_izq_cm",
        "imc","rcc","rel_hombros_cintura","notas"
    ],
    "evaluacion": [
        "user_id","fecha","parq_resultado","objetivo","nivel","zonas_enfoque",
        "dias_semana","duracion_sesion","momento_entreno","equipo",
        "lesiones","detalle_lesiones","horas_sueno","nivel_estres",
        "trabajo_sedentario","agua_litros"
    ],
    "ciclo": ["user_id","fecha_inicio","fecha_fin","notas"],
    "rutinas_sesiones": ["user_id","fecha","tipo_rutina","ejercicio","series","reps","peso_lbs","notas"],
    "config":    ["user_id","clave","valor"],
    "ejercicios":["id","nombre","grupo_muscular","descripcion","url_youtube","dificultad","equipo","activo"],
    "evaluaciones_ia":["user_id","fecha","evaluacion_corporal","prioridades","programa_generado"],
    "videos_workouts":["user_id","categoria","titulo","coach","duracion","nivel","equipo","descripcion","video_id","activo","fecha_agregado"],
}


def get_client():
    try:
        info = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
    except KeyError:
        info = dict(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(info, scopes=SCOPES)
    return gspread.authorize(creds)


def get_spreadsheet():
    return get_client().open_by_key(SPREADSHEET_ID)


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


def leer_df(nombre: str) -> pd.DataFrame:
    """Lee toda la pestaña como DataFrame."""
    ws = get_worksheet(nombre)
    datos = ws.get_all_records()
    return pd.DataFrame(datos) if datos else pd.DataFrame()


def leer_df_usuario(nombre: str, user_id: str) -> pd.DataFrame:
    """
    Lee solo las filas del usuario activo.
    Agrega '_fila_sheets' con el número de fila real en Sheets (para poder borrar).
    """
    ws = get_worksheet(nombre)
    datos = ws.get_all_records()
    if not datos:
        return pd.DataFrame()
    df = pd.DataFrame(datos)
    # Guardar número de fila real (fila 1 = header → datos desde fila 2)
    df["_fila_sheets"] = range(2, len(df) + 2)
    if "user_id" in df.columns:
        df = df[df["user_id"] == user_id].reset_index(drop=True)
    return df


def guardar_fila_usuario(nombre: str, datos: list, user_id: str):
    """Guarda una fila anteponiendo user_id."""
    ws = get_worksheet(nombre)
    ws.append_row([user_id] + datos)


def eliminar_fila_sheets(nombre: str, fila_sheets: int):
    """Elimina la fila usando su número real en Google Sheets."""
    ws = get_worksheet(nombre)
    ws.delete_rows(fila_sheets)

def actualizar_fila_sheets(nombre: str, fila_sheets: int, valores: list):
    """Actualiza una fila completa usando su número real en Google Sheets."""
    ws = get_worksheet(nombre)
    ws.update(f'A{fila_sheets}', [[str(v) if v is not None else "" for v in valores]])
