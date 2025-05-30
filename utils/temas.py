import os
import json
import re
import docx2txt
from utils.drive import subir_archivo_a_drive, CARPETA_TEMAS_JSON

def extraer_temas_de_texto(path_archivo):
    """
    Extrae bloques de texto que comienzan por encabezados tipo #TEMA_1 – Título.
    """
    texto = docx2txt.process(path_archivo)
    patron = re.compile(r'#TEMA_\d+\s+–\s+.*?(?=(?:#TEMA_\d+\s+–|\Z))', re.DOTALL)
    return patron.findall(texto)

def guardar_temas_json(lista_temas, nombre_oposicion):
    """
    Convierte la lista de temas a un dict {titulo: contenido} y lo guarda como JSON en Drive.
    """
    temas_dict = {}
    for contenido in lista_temas:
        titulo = contenido.strip().split('\n')[0]
        temas_dict[titulo] = contenido.strip()

    nombre = nombre_oposicion.strip().lower().replace(" ", "_")
    archivo = f"/tmp/temas_{nombre}.json"
    with open(archivo, 'w', encoding='utf-8') as f:
        json.dump(temas_dict, f, ensure_ascii=False, indent=2)

    return subir_archivo_a_drive(archivo, nombre_oposicion, CARPETA_TEMAS_JSON)

def cargar_temas_desde_json_local(path):
    """
    Carga un archivo JSON local con los temas.
    """
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)
