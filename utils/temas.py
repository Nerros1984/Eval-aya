import os
import json
import re
import docx2txt
from utils.drive import subir_archivo_a_drive, CARPETA_TEMAS_JSON

def extraer_temas_de_texto(path_archivo):
    texto = docx2txt.process(path_archivo)
    
    # Patrón más robusto para detectar encabezados del tipo #TEMA_1 – Título
    patron = re.compile(
        r'#TEMA[_\s]?(\d{1,2})\s*[–\-]\s*(.+?)(?=(#TEMA[_\s]?\d{1,2}\s*[–\-]|$))',
        re.DOTALL | re.IGNORECASE
    )
    
    coincidencias = patron.findall(texto)
    
    # Reconstruye el contenido por tema con formato consistente
    temas = [
        f"#TEMA_{num} – {titulo.strip()}\n{contenido.strip()}"
        for num, titulo, contenido in coincidencias
    ]
    return temas

def guardar_temas_json(lista_temas, nombre_oposicion):
    temas_dict = {
        contenido.strip().split('\n')[0]: contenido.strip()
        for contenido in lista_temas
    }
    nombre = nombre_oposicion.strip().lower().replace(" ", "_")
    archivo = f"/tmp/temas_{nombre}.json"
    with open(archivo, 'w', encoding='utf-8') as f:
        json.dump(temas_dict, f, ensure_ascii=False, indent=2)
    return subir_archivo_a_drive(archivo, nombre_oposicion, CARPETA_TEMAS_JSON)

def cargar_temas_desde_json_local(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)
