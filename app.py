
from datetime import datetime
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import streamlit as st
import openai
import json
import re
import tempfile

st.set_page_config(page_title="EvalúaYa - Generador de Test por Temario", layout="centered")

st.title("🧠 EvalúaYa - Generador de Test por Temario")
st.markdown("✍️ **Introduce el contenido del temario** (puede ser un párrafo o más):")

texto_input = st.text_area(" ", height=300, label_visibility="collapsed")
num_preguntas = st.slider("Número de preguntas a generar:", min_value=3, max_value=20, value=5)

def extraer_json_valido(respuesta):
    # Elimina ```json y ```
    texto = respuesta.strip().strip("`")
    if texto.startswith("json"):
        texto = texto[len("json"):].strip()

    # Extrae el primer bloque JSON válido
    patron_json = re.search(r'\[\s*{.*?}\s*\]', texto, re.DOTALL)
    if patron_json:
        return patron_json.group(0)
    return texto

def generar_preguntas_ia(texto, num_preguntas):
    prompt = f"""Eres un generador de preguntas tipo test. A partir del siguiente texto:

"""{texto}"""

Genera {num_preguntas} preguntas tipo test en formato JSON con exactamente 4 opciones, y una de ellas debe ser correcta. Devuelve solo el JSON con esta estructura:

[
  {{
    "pregunta": "Texto de la pregunta",
    "opciones": ["Opción A", "Opción B", "Opción C", "Opción D"],
    "respuesta": "Letra de la opción correcta (A, B, C o D)"
  }},
  ...
]
"""
    try:
        client = openai.OpenAI(api_key=st.secrets["openai_api_key"])
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        content = completion.choices[0].message.content
        json_limpio = extraer_json_valido(content)
        preguntas = json.loads(json_limpio)
        return preguntas

    except json.JSONDecodeError as e:
        st.error("❌ Error al interpretar la respuesta como JSON.")
        st.text(json_limpio)
        return None
    except Exception as e:
        st.error(f"⚠️ Error inesperado: {e}")
        return None

if st.button("🧪 Generar test"):
    if texto_input.strip() == "":
        st.warning("Debes introducir contenido para generar el test.")
    else:
        with st.spinner("Generando test con IA... espera unos segundos."):
            preguntas = generar_preguntas_ia(texto_input, num_preguntas)

        if preguntas:
            st.success("✅ Test generado con éxito.")
            for i, pregunta in enumerate(preguntas):
                st.markdown(f"### Pregunta {i + 1}")
                st.write(pregunta["pregunta"])

                respuesta_usuario = st.radio(
                    "Selecciona una opción:",
                    options=pregunta["opciones"],
                    key=f"pregunta_{i}"
                )

                letra_correcta = pregunta["respuesta"]
                opcion_correcta = next(
                    (op for op in pregunta["opciones"] if op.startswith(letra_correcta + ":")), None
                )

                if respuesta_usuario:
                    if respuesta_usuario == opcion_correcta:
                        st.success("✅ ¡Correcto!")
                    else:
                        st.error(f"❌ Incorrecto. La respuesta correcta era: {opcion_correcta}")
                st.divider()
