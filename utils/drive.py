import re
import unicodedata
import os
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import json

def autenticar_drive():
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
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

# Simulación: cargar lista de oposiciones (de momento, fija)
def cargar_preguntas_desde_drive(lista=False):
    if lista:
        return ["Auxiliar Administrativo – Ayuntamiento de Sevilla"]
    return []

# Exporta un test generado como JSON
def exportar_test_json(preguntas):
    return json.dumps(preguntas, indent=2)
