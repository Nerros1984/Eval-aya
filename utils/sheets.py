import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st


def registrar_en_sheet(nombre_temario, tipo_contenido, url_pdf, url_json, fecha):
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["gcp_service_account"],
        ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    )
    client = gspread.authorize(creds)
    sheet = client.open("EvaluaYa_base").worksheet("temarios")
    fila = [nombre_temario, tipo_contenido, url_pdf, url_json, fecha]
    sheet.append_row(fila)


def obtener_oposiciones_guardadas():
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["gcp_service_account"],
        ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    )
    client = gspread.authorize(creds)
    sheet = client.open("EvaluaYa_base").worksheet("temarios")
    datos = sheet.col_values(4)[1:]  # Suponiendo que la columna D tiene las oposiciones
    return sorted(list(set([op for op in datos if op.strip()])))
