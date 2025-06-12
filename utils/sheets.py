# utils/sheets.py

import gspread
from google.oauth2.service_account import Credentials

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
