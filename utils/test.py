import os
import json
import random
from datetime import datetime
import openai
import streamlit as st

from utils.drive import subir_archivo_a_drive, CARPETA_TEST_JSON, CARPETA_TEST_PDF
from utils.pdf import generar_pdf_test
from utils.estructura import estructura_bloques, clasificacion_temas

# Configurar la API key de OpenAI desde secrets
openai.api_key = st.secrets["openai_api_key"]

# --- Generador con OpenAI ---
def generar_preguntas_desde_tema(nombre_tema, contenido_tema, num_preguntas=5):
    prompt = f"""
    Genera {num_preguntas} preguntas tipo test con 4 opciones cada una sobre el siguiente tema:

    Título del tema: {nombre_tema}

    Contenido:
    {contenido_tema}

    El formato debe ser una lista JSON donde cada ítem sea un diccionario con las claves:
    - "pregunta": texto de la pregunta
    - "opciones": lista de 4 opciones
    - "respuesta_correcta": texto exacto de la opción correcta
    """

    try:
        respuesta = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        texto = respuesta.choices[0].message.content
        preguntas = json.loads(texto)
    except Exception as e:
        print("Error procesando respuesta de OpenAI:", e)
        preguntas = []

    return preguntas

# --- Generador de test desde un único tema ---
def generar_test_desde_tema(nombre_oposicion, nombre_tema, contenido_tema, num_preguntas):
    preguntas = generar_preguntas_desde_tema(nombre_tema, contenido_tema, num_preguntas)

    nombre_archivo = f"{nombre_oposicion}_{nombre_tema}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    ruta_local = os.path.join("test_generados", f"{nombre_archivo}.json")
    os.makedirs("test_generados", exist_ok=True)

    with open(ruta_local, "w", encoding="utf-8") as f:
        json.dump(preguntas, f, indent=2, ensure_ascii=False)

    subir_archivo_a_drive(ruta_local, nombre_oposicion, CARPETA_TEST_JSON)

    ruta_pdf = generar_pdf_test(nombre_oposicion, preguntas, nombre_archivo)
    subir_archivo_a_drive(ruta_pdf, nombre_oposicion, CARPETA_TEST_PDF)

    return ruta_local, ruta_pdf, preguntas

# --- Generador de simulacro oficial ---
def generar_test_examen_completo(nombre_oposicion, temas_dict):
    bloques = {k: [] for k in estructura_bloques}

    for tema, contenido in temas_dict.items():
        bloque = clasificacion_temas.get(tema)
        if not bloque:
            continue
        preguntas = generar_preguntas_desde_tema(tema, contenido, estructura_bloques[bloque])
        bloques[bloque].extend(preguntas)

    preguntas_finales = []
    for bloque, cantidad in estructura_bloques.items():
        seleccionadas = random.sample(bloques[bloque], min(len(bloques[bloque]), cantidad))
        preguntas_finales.extend(seleccionadas)

    random.shuffle(preguntas_finales)

    nombre_archivo = f"{nombre_oposicion}_examen_oficial_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    ruta_local_json = os.path.join("test_generados", f"{nombre_archivo}.json")
    os.makedirs("test_generados", exist_ok=True)

    with open(ruta_local_json, "w", encoding="utf-8") as f:
        json.dump(preguntas_finales, f, indent=2, ensure_ascii=False)

    ruta_pdf = generar_pdf_test(nombre_oposicion, preguntas_finales, nombre_archivo)
    subir_archivo_a_drive(ruta_local_json, nombre_oposicion, CARPETA_TEST_JSON)
    subir_archivo_a_drive(ruta_pdf, nombre_oposicion, CARPETA_TEST_PDF)

    return ruta_local_json, ruta_pdf, preguntas_finales
