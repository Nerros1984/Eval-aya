# utils/sheets.py

import gspread
from google.oauth2.service_account import Credentials
from collections import defaultdict

# Configura el acceso a Google Sheets
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
CREDENTIALS_FILE = "credentials.json"
SHEET_NAME = "Registro_Tests_Generados"


def get_worksheet():
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    sheet = client.open(SHEET_NAME)
    return sheet.worksheet("Historial")


def registrar_test_generado(data: dict):
    ws = get_worksheet()
    fila = [
        data.get("fecha"),
        data.get("nombre_oposicion"),
        data.get("test_id"),
        data.get("num_preguntas"),
        data.get("enlace_pdf")
    ]
    ws.append_row(fila, value_input_option="USER_ENTERED")


def obtener_oposiciones_y_temas():
    ws = get_worksheet()
    registros = ws.get_all_records()

    oposiciones_dict = defaultdict(list)
    for row in registros:
        oposicion = row.get("nombre_oposicion")
        tema = row.get("test_id")  # o usa otro campo si tienes "tema" explícito
        if oposicion and tema:
            oposiciones_dict[oposicion].append(tema)

    return dict(oposiciones_dict)
