import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st


def registrar_en_sheet(nombre_oposicion, nombre_temario, tipo_contenido, enlace_pdf, enlace_json, fecha):
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["gcp_service_account"],
        ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    )
    client = gspread.authorize(creds)
    sheet = client.open("EvaluaYa_base").worksheet("temarios")

    fila = [nombre_oposicion, nombre_temario, tipo_contenido, enlace_pdf, enlace_json, fecha]
    sheet.append_row(fila)

def obtener_oposiciones_guardadas():
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["gcp_service_account"],
        ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    )
    client = gspread.authorize(creds)
    sheet = client.open("EvaluaYa_base").worksheet("temarios")
    datos = sheet.col_values(1)[1:]  # Columna A: "oposicion", omite cabecera

    # Limpiar y normalizar las oposiciones
    oposiciones = set()
    for op in datos:
        op_normalizada = op.strip()
        if op_normalizada:
            oposiciones.add(op_normalizada)

    return sorted(list(oposiciones))
