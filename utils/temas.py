import os
import json
import re
import docx2txt
from utils.drive import subir_archivo_a_drive, CARPETA_TEMAS_JSON


def extraer_titulos_tema(texto):
    """
    Extrae los títulos de temas de un texto.
    Ejemplo de patrón detectado: Tema 1. Introducción...
    """
    patron = re.compile(r'(Tema\s+\d+\.?\s+.+?)(?=Tema\s+\d+\.|\Z)', re.DOTALL | re.IGNORECASE)
    temas = patron.findall(texto)
    return temas


def extraer_temas_de_texto(path_archivo):
    """
    Dado un archivo DOCX, extrae los temas en formato lista.
    """
    texto = docx2txt.process(path_archivo)
    temas_extraidos = extraer_titulos_tema(texto)
    return temas_extraidos


def guardar_temas_json(lista_temas, nombre_oposicion):
    """
    Convierte la lista de temas a un dict {titulo: contenido} y lo guarda como JSON en Drive.
    Devuelve el enlace del archivo subido.
    """
    temas_dict = {}
    for i, contenido in enumerate(lista_temas, 1):
        titulo = contenido.strip().split('\n')[0]
        temas_dict[titulo] = contenido.strip()

    nombre_normalizado = nombre_oposicion.strip().lower().replace(" ", "_")
    nombre_archivo = f"temas_{nombre_normalizado}.json"

    ruta_temporal = f"/tmp/{nombre_archivo}"
    with open(ruta_temporal, 'w', encoding='utf-8') as f:
        json.dump(temas_dict, f, ensure_ascii=False, indent=2)

    enlace_drive = subir_archivo_a_drive(ruta_temporal, nombre_oposicion, CARPETA_TEMAS_JSON)
    return enlace_drive


def cargar_temas_desde_json_local(path):
    """
    Carga un archivo JSON local con temas y devuelve el diccionario.
    """
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def cargar_temas_desde_drive(path_local_tmp):
    """
    (Pendiente de implementar si deseas bajar desde Drive)
    De momento solo se usa carga local.
    """
    return cargar_temas_desde_json_local(path_local_tmp)
