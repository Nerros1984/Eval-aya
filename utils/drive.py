import re
import unicodedata
import os
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st

def autenticar_drive():
    scope = ['https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["gcp_service_account"],
        scope
    )
    gauth = GoogleAuth()
    gauth.credentials = credentials
    return GoogleDrive(gauth)

def normalizar_nombre(nombre):
    nombre = unicodedata.normalize('NFKD', nombre).encode('ascii', 'ignore').decode('utf-8')
    nombre = re.sub(r'[^a-zA-Z0-9\s]', '', nombre)
    nombre = nombre.lower().strip().replace(' ', '_')
    return nombre

def obtener_o_crear_carpeta(drive, nombre_temario, carpeta_raiz_id=None):
    nombre_normalizado = normalizar_nombre(nombre_temario)
    query = f"title='{nombre_normalizado}' and mimeType='application/vnd.google-apps.folder'"
    if carpeta_raiz_id:
        query += f" and '{carpeta_raiz_id}' in parents"
    carpetas = drive.ListFile({'q': query}).GetList()
    if carpetas:
        return carpetas[0]['id']
    metadata = {
        'title': nombre_normalizado,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    if carpeta_raiz_id:
        metadata['parents'] = [{'id': carpeta_raiz_id}]
    carpeta = drive.CreateFile(metadata)
    carpeta.Upload()
    return carpeta['id']

def subir_archivo_a_drive(ruta_archivo, nombre_temario):
    drive = autenticar_drive()
    carpeta_id = obtener_o_crear_carpeta(drive, nombre_temario)
    nombre_archivo = os.path.basename(ruta_archivo)
    archivo_drive = drive.CreateFile({
        'title': nombre_archivo,
        'parents': [{'id': carpeta_id}]
    })
    archivo_drive.SetContentFile(ruta_archivo)
    archivo_drive.Upload()
    return archivo_drive['alternateLink']
