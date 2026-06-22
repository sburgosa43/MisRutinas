import gspread
import streamlit as st
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

SPREADSHEET_NAME = "MisRutinas_DB"

SHEETS_CONFIG = {
    "medidas": [
        "fecha", "edad", "peso_kg", "altura_cm",
        "cintura_cm", "cadera_cm",
        "muslo_der_cm", "muslo_izq_cm",
        "brazo_der_cm", "brazo_izq_cm",
        "hombros_cm",
        "imc", "rcc", "rel_hombros_cintura",
        "notas"
    ],
    "config": ["clave", "valor"],
    "ejercicios": [
        "id", "nombre", "grupo_muscular",
        "descripcion", "url_youtube", "dificultad", "activo"
    ],
}


@st.cache_resource
def get_client():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES,
    )
    return gspread.authorize(creds)


def get_spreadsheet():
    client = get_client()
    try:
        return client.open(SPREADSHEET_NAME)
    except gspread.SpreadsheetNotFound:
        return _crear_spreadsheet(client)


def _crear_spreadsheet(client):
    sh = client.create(SPREADSHEET_NAME)
    owner_email = st.secrets.get("owner_email", None)
    if owner_email:
        sh.share(owner_email, perm_type="user", role="owner")
    for i, (nombre, headers) in enumerate(SHEETS_CONFIG.items()):
        if i == 0:
            ws = sh.sheet1
            ws.update_title(nombre)
        else:
            ws = sh.add_worksheet(
                title=nombre,
                rows=1000,
                cols=len(headers) + 5,
            )
        ws.append_row(headers)
        ws.format("1:1", {"textFormat": {"bold": True}})
    return sh


def get_worksheet(nombre: str):
    sh = get_spreadsheet()
    try:
        return sh.worksheet(nombre)
    except gspread.WorksheetNotFound:
        headers = SHEETS_CONFIG.get(nombre, [])
        ws = sh.add_worksheet(
            title=nombre,
            rows=1000,
            cols=max(len(headers), 5),
        )
        if headers:
            ws.append_row(headers)
            ws.format("1:1", {"textFormat": {"bold": True}})
        return ws


def leer_como_dataframe(nombre: str):
    import pandas as pd
    ws = get_worksheet(nombre)
    datos = ws.get_all_records()
    return pd.DataFrame(datos)
