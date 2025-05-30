import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st

def _get_client():
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["gcp_service_account"],
        ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    )
    return gspread.authorize(creds)

def registrar_en_sheet(nombre_oposicion, nombre_temario, tipo_contenido, enlace_pdf, enlace_json, fecha):
    client = _get_client()
    sheet = client.open("EvaluaYa_base").worksheet("temarios")
    fila = [nombre_oposicion, nombre_temario, tipo_contenido, enlace_pdf, enlace_json, fecha]
    sheet.append_row(fila)

def obtener_oposiciones_guardadas():
    client = _get_client()
    sheet = client.open("EvaluaYa_base").worksheet("temarios")
    datos = sheet.col_values(1)[1:]  # Columna A, sin cabecera
    oposiciones = sorted(set(op.strip() for op in datos if op.strip()))
    return oposiciones

def obtener_temarios_de_oposicion(nombre_oposicion):
    client = _get_client()
    sheet = client.open("EvaluaYa_base").worksheet("temarios")
    registros = sheet.get_all_values()[1:]  # sin cabecera

    return [
        {
            "nombre_temario": fila[1],
            "tipo": fila[2],
            "pdf": fila[3],
            "json": fila[4],
            "fecha": fila[5]
        }
        for fila in registros
        if len(fila) >= 6 and fila[0] == nombre_oposicion and fila[2] == "temario"
    ]

def obtener_tests_de_oposicion(nombre_oposicion):
    client = _get_client()
    sheet = client.open("EvaluaYa_base").worksheet("temarios")
    registros = sheet.get_all_values()[1:]  # sin cabecera

    return [
        {
            "nombre_test": fila[1],
            "tipo": fila[2],
            "pdf": fila[3],
            "json": fila[4],
            "fecha": fila[5]
        }
        for fila in registros
        if len(fila) >= 6 and fila[0] == nombre_oposicion and fila[2] == "test"
    ]
