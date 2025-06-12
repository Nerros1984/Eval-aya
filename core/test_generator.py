import os
import json
import random
from datetime import datetime
import streamlit as st
from openai import OpenAI

from utils.drive import subir_archivo_a_drive, CARPETA_TEST_JSON, CARPETA_TEST_PDF
from utils.pdf import generar_pdf_test
from utils.estructura import clasificacion_temas
from utils.sheets import registrar_en_sheet

# Inicialización del cliente OpenAI moderno
client = OpenAI(api_key=st.secrets["openai_api_key"])

def generar_preguntas_desde_tema(nombre_tema, contenido_tema, num_preguntas=5):
    prompt = f"""
    Eres un generador de exámenes oficiales para oposiciones. Tu tarea es generar exactamente {num_preguntas} preguntas tipo test a partir del siguiente tema.

    Título del tema: {nombre_tema}

    Contenido del tema:
    {contenido_tema}

    Las preguntas deben cumplir este formato:
    - Cada pregunta tiene 4 opciones (A, B, C, D).
    - Una única respuesta es correcta.
    - El resultado debe estar en JSON válido con esta estructura exacta:

    [
      {{
        "pregunta": "Texto de la pregunta",
        "opciones": ["Opción A", "Opción B", "Opción C", "Opción D"],
        "respuesta_correcta": "Opción C"
      }},
      ...
    ]

    Devuelve ÚNICAMENTE el JSON, sin explicaciones ni introducciones.
    """

    try:
        respuesta = client.chat.completions.create(
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

def generar_test_examen_completo(nombre_oposicion, temas_dict):
    preguntas_total = []
    preguntas_reserva = []

    temas_validos = [(tema, contenido) for tema, contenido in temas_dict.items() if tema in clasificacion_temas]
    random.shuffle(temas_validos)

    for tema, contenido in temas_validos:
        preguntas = generar_preguntas_desde_tema(tema, contenido, 4)
        preguntas_total.extend(preguntas)
        if len(preguntas_total) >= 90:
            break

    for tema, contenido in temas_validos:
        preguntas = generar_preguntas_desde_tema(tema, contenido, 2)
        preguntas_reserva.extend(preguntas)
        if len(preguntas_reserva) >= 10:
            break

    preguntas_total = preguntas_total[:90]
    preguntas_reserva = preguntas_reserva[:10]

    for p in preguntas_reserva:
        p["reserva"] = True

    todas = preguntas_total + preguntas_reserva
    random.shuffle(todas)

    st.warning(f"Se han generado {len(preguntas_total)} preguntas + {len(preguntas_reserva)} de reserva")

    nombre_archivo = f"{nombre_oposicion}_examen_oficial_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    os.makedirs("test_generados", exist_ok=True)

    ruta_json = os.path.join("test_generados", f"{nombre_archivo}.json")
    with open(ruta_json, "w", encoding="utf-8") as f:
        json.dump(todas, f, indent=2, ensure_ascii=False)

    enlace_json = subir_archivo_a_drive(ruta_json, nombre_oposicion, CARPETA_TEST_JSON)
    ruta_pdf = generar_pdf_test(nombre_oposicion, todas, nombre_archivo)
    enlace_pdf = subir_archivo_a_drive(ruta_pdf, nombre_oposicion, CARPETA_TEST_PDF)

    fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
    registrar_en_sheet(nombre_oposicion, nombre_archivo, "test", enlace_pdf, enlace_json, fecha)

    return ruta_json, ruta_pdf, todas
