import gspread
from google.oauth2.service_account import Credentials
import streamlit as st

def registrar_en_sheet(nombre_temario, tipo, url_pdf, url_json, fecha):
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict)
    client = gspread.authorize(creds)

    # 📌 Ahora accede al archivo correcto
    spreadsheet = client.open("EvaluaYa_base")
    worksheet = spreadsheet.worksheet("Temarios")

    nueva_fila = [nombre_temario, tipo, url_pdf, url_json, fecha]
    worksheet.append_row(nueva_fila)
