
import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
import streamlit as st

SCOPES = ['https://www.googleapis.com/auth/drive']
CARPETA_TEST_PDF = "1dNkIuLDfV_qGmrCepkFYo5IWlfFwkl7w"
CARPETA_TEST_JSON = "1dNkIuLDfV_qGmrCepkFYo5IWlfFwkl7w"

def autenticar_drive():
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=SCOPES)
    return build("drive", "v3", credentials=credentials)

def subir_archivo_a_drive(ruta_archivo, nombre_oposicion, carpeta_id):
    servicio = autenticar_drive()
    nombre_archivo = os.path.basename(ruta_archivo)

    archivo_metadata = {
        "name": nombre_archivo,
        "parents": [carpeta_id]
    }

    media = MediaFileUpload(ruta_archivo, resumable=True)
    archivo = servicio.files().create(
        body=archivo_metadata,
        media_body=media,
        fields="id"
    ).execute()

    enlace = f"https://drive.google.com/file/d/{archivo.get('id')}/view?usp=sharing"
    return enlace
