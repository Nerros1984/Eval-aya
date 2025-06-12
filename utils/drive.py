import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import streamlit as st

# Credenciales desde streamlit secrets
credentials_dict = st.secrets["gcp_service_account"]
credentials = service_account.Credentials.from_service_account_info(credentials_dict)

drive_service = build("drive", "v3", credentials=credentials)

# Carpetas por defecto (puedes ajustar estos IDs si quieres usar constantes fijas)
CARPETA_TEST_JSON = "test_json"
CARPETA_TEST_PDF = "test_pdf"

# Función auxiliar para buscar o crear carpetas

def obtener_o_crear_carpeta(nombre_carpeta, carpeta_padre_id=None):
    query = f"name='{nombre_carpeta}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    if carpeta_padre_id:
        query += f" and '{carpeta_padre_id}' in parents"

    respuesta = drive_service.files().list(q=query, spaces='drive').execute()
    archivos = respuesta.get('files', [])

    if archivos:
        return archivos[0]['id']

    metadata = {
        'name': nombre_carpeta,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    if carpeta_padre_id:
        metadata['parents'] = [carpeta_padre_id]

    archivo = drive_service.files().create(body=metadata, fields='id').execute()
    return archivo['id']


def subir_archivo_a_drive(ruta_archivo, subcarpeta, carpeta_padre_id=None):
    nombre_archivo = os.path.basename(ruta_archivo)
    carpeta_id = obtener_o_crear_carpeta(subcarpeta, carpeta_padre_id)

    archivo_metadata = {
        'name': nombre_archivo,
        'parents': [carpeta_id]
    }

    media = MediaFileUpload(ruta_archivo, resumable=True)

    archivo = drive_service.files().create(
        body=archivo_metadata,
        media_body=media,
        fields='id, webViewLink'
    ).execute()

    return archivo.get('webViewLink')
