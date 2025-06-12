import json
from openai import OpenAI
import streamlit as st

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
