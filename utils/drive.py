import re
import unicodedata
import os
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st

# IDs de las carpetas raíz en Google Drive
CARPETA_TEMARIOS = "1x08mfjA7JhnVk9OxvXJD54MLmtdZDCJb"
CARPETA_TEMAS_JSON = "1popTRkA-EjI8_4WqKPjkldWVpCYsJJjm"
CARPETA_TEST_JSON = "1dNkIuLDfV_qGmrCepkFYo5IWlfFwkl7w"
CARPETA_TEST_PDF = "1dNkIuLDfV_qGmrCepkFYo5IWlfFwkl7w"

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
    nombre = re.sub(r'[^a-zA-Z0-9\\s]', '', nombre)
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

def subir_archivo_a_drive(ruta_local_json, nombre_oposicion, CARPETA_TEST_JSON):
    drive = autenticar_drive()
    carpeta_id = obtener_o_crear_carpeta(drive, nombre_temario, carpeta_raiz_id)
    nombre_archivo = os.path.basename(ruta_archivo)
    archivo_drive = drive.CreateFile({
        'title': nombre_archivo,
        'parents': [{'id': carpeta_id}]
    })
    archivo_drive.SetContentFile(ruta_archivo)
    archivo_drive.Upload()
    return archivo_drive['alternateLink']

def descargar_archivo_de_drive(nombre_archivo, carpeta_drive_id, path_local_destino):
    """
    Busca el archivo dentro de una subcarpeta (por oposición) en la carpeta principal de Drive
    y lo descarga al path local indicado.
    """
    drive = autenticar_drive()
    
    # Obtener nombre normalizado de subcarpeta
    subcarpeta_nombre = normalizar_nombre(nombre_archivo.replace("temas_", "").replace(".json", ""))
    
    # Buscar subcarpeta dentro de carpeta_drive_id
    query_carpeta = f"'{carpeta_drive_id}' in parents and title = '{subcarpeta_nombre}' and mimeType = 'application/vnd.google-apps.folder'"
    subcarpetas = drive.ListFile({'q': query_carpeta, 'maxResults': 1}).GetList()

    if not subcarpetas:
        return False

    subcarpeta_id = subcarpetas[0]['id']

    # Buscar archivo dentro de esa subcarpeta
    query = f"'{subcarpeta_id}' in parents and title = '{nombre_archivo}' and trashed = false"
    resultados = drive.ListFile({'q': query, 'maxResults': 1}).GetList()

    if resultados:
        archivo = resultados[0]
        archivo.GetContentFile(path_local_destino)
        return path_local_destino
    else:
        return False
