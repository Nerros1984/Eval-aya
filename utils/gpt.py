# utils/gpt.py

import openai
import streamlit as st

openai.api_key = st.secrets["openai_api_key"]

def generar_preguntas_gpt(tema_texto: str, num_preguntas: int):
    prompt = f"""
Eres un generador automático de preguntas tipo test. A partir del siguiente texto del temario:

\"\"\"{tema_texto}\"\"\"

Genera exactamente {num_preguntas} preguntas de tipo test. Cada pregunta debe tener:
- enunciado breve
- 4 opciones (A, B, C, D)
- indicar cuál es la respuesta correcta

Devuélvelo en formato JSON como una lista así:
[
  {{
    "pregunta": "...",
    "opciones": ["A", "B", "C", "D"],
    "respuesta_correcta": "A"
  }},
  ...
]
"""

    respuesta = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Eres un generador de preguntas de oposiciones."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=1800
    )

    import json
    try:
        contenido = respuesta.choices[0].message.content
        return json.loads(contenido)
    except Exception as e:
        return [{"pregunta": f"Error al generar preguntas: {e}", "opciones": [], "respuesta_correcta": ""}]
