
import os
import json
import re
import unicodedata
from docx import Document

def extraer_temarios_docx(path_docx):
    document = Document(path_docx)
    texto = "\n".join([p.text for p in document.paragraphs])
    return texto

def extraer_temas_de_texto(texto):
    texto = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('utf-8')
    patron_tema = re.compile(r'(TEMA \d+[.:\-\s]+)(.+?)(?=\nTEMA \d+|\Z)', re.DOTALL | re.IGNORECASE)
    coincidencias = patron_tema.findall(texto)
    temas = []
    for i, (titulo, contenido) in enumerate(coincidencias, 1):
        temas.append({
            "numero": i,
            "titulo": titulo.strip(),
            "contenido": contenido.strip()
        })
    return temas

def guardar_temas_json(temas, nombre_oposicion, carpeta_destino="data/temas_json"):
    os.makedirs(carpeta_destino, exist_ok=True)
    ruta = os.path.join(carpeta_destino, f"{nombre_oposicion}.json")
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(temas, f, indent=2, ensure_ascii=False)
    return ruta
