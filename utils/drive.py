# utils/drive.py

import os
import re
import unicodedata
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st

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

def subir_archivo_a_drive(ruta_archivo, nombre_temario, carpeta_raiz_id):
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

def obtener_oposiciones_con_tema_json():
    drive = autenticar_drive()
    resultados = drive.ListFile({
        'q': f"'{CARPETA_TEMAS_JSON}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
    }).GetList()

    nombres_oposiciones = [carpeta['title'] for carpeta in resultados]
    return nombres_oposiciones

def descargar_archivo_de_drive(nombre_archivo, carpeta_drive_id, path_local_destino):
    drive = autenticar_drive()
    nombre_oposicion = nombre_archivo.replace("temas_", "").replace(".json", "")
    subcarpeta_nombre = normalizar_nombre(nombre_oposicion)

    query_carpeta = f"'{carpeta_drive_id}' in parents and title = '{subcarpeta_nombre}' and mimeType = 'application/vnd.google-apps.folder'"
    subcarpetas = drive.ListFile({'q': query_carpeta, 'maxResults': 1}).GetList()

    if not subcarpetas:
        return False

    subcarpeta_id = subcarpetas[0]['id']
    query = f"'{subcarpeta_id}' in parents and title = '{nombre_archivo}' and trashed = false"
    resultados = drive.ListFile({'q': query, 'maxResults': 1}).GetList()

    if resultados:
        archivo = resultados[0]
        archivo.GetContentFile(path_local_destino)
        return path_local_destino
    else:
        return False
