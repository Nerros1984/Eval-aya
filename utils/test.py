import os
import json
import random
from datetime import datetime
import openai
import streamlit as st

from utils.drive import subir_archivo_a_drive, CARPETA_TEST_JSON, CARPETA_TEST_PDF
from utils.pdf import generar_pdf_test
from utils.sheets import registrar_en_sheet

openai.api_key = st.secrets["openai_api_key"]

# CLASIFICACIÓN DE TEMAS EN BLOQUES
clasificacion_temas = {
    "bloque_1": ["TEMA_1", "TEMA_2", "TEMA_3"],
    "bloque_2": ["TEMA_4", "TEMA_5", "TEMA_6"],
    "bloque_3": ["TEMA_7", "TEMA_8", "TEMA_9"],
    "bloque_4": ["TEMA_10", "TEMA_11", "TEMA_12"],
    "bloque_5": ["TEMA_13", "TEMA_14", "TEMA_15"],
    "bloque_6": ["TEMA_16", "TEMA_17", "TEMA_18"],
    "bloque_7": ["TEMA_19", "TEMA_20", "TEMA_21"],
    "bloque_8": ["TEMA_22", "TEMA_23", "TEMA_24"],
    "bloque_9": ["TEMA_25"]
}

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
        respuesta = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        texto = respuesta.choices[0].message.content
        preguntas = json.loads(texto)
    except Exception as e:
        print("❌ Error procesando respuesta de OpenAI:", e)
        preguntas = []

    return preguntas

def generar_test_examen_completo(nombre_oposicion, temas_dict):
    preguntas_total = []
    preguntas_reserva = []

    # Reparto proporcional: 10 preguntas por bloque (9 bloques = 90 preguntas)
    for bloque, datos in estructura_bloques.items():
        temas_bloque = datos["temas"]
        temas_validos = [(tema, temas_dict[tema]) for tema in temas_bloque if tema in temas_dict]

        if not temas_validos:
            continue

        # Distribuir 10 preguntas entre los temas del bloque
        preguntas_por_tema = max(1, 10 // len(temas_validos))
        preguntas_bloque = []

        for tema, contenido in temas_validos:
            preguntas = generar_preguntas_desde_tema(tema, contenido, preguntas_por_tema)
            preguntas_bloque.extend(preguntas)

        # Rellenar si hay menos de 10 por fallos de generación
        while len(preguntas_bloque) < 10 and temas_validos:
            tema, contenido = random.choice(temas_validos)
            extra = generar_preguntas_desde_tema(tema, contenido, 1)
            preguntas_bloque.extend(extra)

        preguntas_total.extend(preguntas_bloque[:10])  # Limitar a 10 preguntas por bloque

    # Preguntas de reserva (2 por bloque = 18 total aprox)
    for bloque, datos in estructura_bloques.items():
        temas_bloque = datos["temas"]
        temas_validos = [(tema, temas_dict[tema]) for tema in temas_bloque if tema in temas_dict]

        if not temas_validos:
            continue

        tema, contenido = random.choice(temas_validos)
        reserva = generar_preguntas_desde_tema(tema, contenido, 2)
        for r in reserva:
            r["reserva"] = True
        preguntas_reserva.extend(reserva)

        if len(preguntas_reserva) >= 10:
            break

    todas = preguntas_total + preguntas_reserva[:10]
    random.shuffle(todas)

    st.warning(f"Se han generado {len(preguntas_total)} preguntas + {len(preguntas_reserva[:10])} de reserva")

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
