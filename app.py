import os
import json
import re
import unicodedata
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import streamlit as st
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# Constantes para carpetas
CARPETA_TEMAS_JSON = "1popTRkA-EjI8_4WqKPjkldWVpCYsJJjm"

# Funciones auxiliares

def autenticar_drive():
    scope = ['https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["gcp_service_account"], scope)
    gauth = GoogleAuth()
    gauth.credentials = credentials
    return GoogleDrive(gauth)

def normalizar_nombre(nombre):
    nombre = unicodedata.normalize('NFKD', nombre).encode('ascii', 'ignore').decode('utf-8')
    nombre = re.sub(r'[^a-zA-Z0-9\s]', '', nombre)
    return nombre.lower().strip().replace(' ', '_')

def extraer_temas_de_texto(texto):
    temas = {}
    tema_actual = ""
    lineas = texto.split("\n")
    for linea in lineas:
        if re.match(r'^\d+\.\s', linea):  # línea tipo '1. Tema introductorio'
            tema_actual = linea.strip()
            temas[tema_actual] = ""
        elif tema_actual:
            temas[tema_actual] += linea.strip() + " "
    return temas

def guardar_temas_json(temas, nombre_oposicion):
    drive = autenticar_drive()
    nombre_archivo = f"temas_{normalizar_nombre(nombre_oposicion)}_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    ruta_local = f"/tmp/{nombre_archivo}"

    with open(ruta_local, "w", encoding="utf-8") as f:
        json.dump(temas, f, indent=2, ensure_ascii=False)

    archivo_drive = drive.CreateFile({
        'title': nombre_archivo,
        'parents': [{'id': CARPETA_TEMAS_JSON}]
    })
    archivo_drive.SetContentFile(ruta_local)
    archivo_drive.Upload()
    return archivo_drive['alternateLink']

# Ejecución manual para probar
if __name__ == "__main__":
    texto_ejemplo = """
1. Tema introductorio
Este es el contenido del primer tema. Sigue una explicación larga...

2. Segundo tema
Aquí comienza el segundo tema con más contenido educativo.
    """
    temas = extraer_temas_de_texto(texto_ejemplo)
    enlace_json = guardar_temas_json(temas, "Administrativo Ayuntamiento Sevilla")
    print(f"Guardado en: {enlace_json}")
