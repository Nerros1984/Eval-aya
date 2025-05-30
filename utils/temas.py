import os
import json
import re
import docx2txt

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

def guardar_temas_json(lista_temas, nombre_oposicion, carpeta_destino='./data/temas_json'):
    """
    Guarda cada tema en un archivo JSON individual en la carpeta correspondiente.
    """
    nombre_normalizado = nombre_oposicion.strip().lower().replace(" ", "_")
    carpeta_oposicion = os.path.join(carpeta_destino, nombre_normalizado)

    os.makedirs(carpeta_oposicion, exist_ok=True)

    for i, contenido in enumerate(lista_temas, 1):
        nombre_tema = f"tema_{i:02d}.json"
        ruta_archivo = os.path.join(carpeta_oposicion, nombre_tema)
        with open(ruta_archivo, 'w', encoding='utf-8') as f:
            json.dump({
                "titulo": contenido.strip().split('\n')[0],
                "contenido": contenido.strip()
            }, f, ensure_ascii=False, indent=2)

    return carpeta_oposicion
