import streamlit as st
from openai import OpenAI
import uuid
from datetime import datetime
import json
import re

# Cliente OpenAI con clave desde secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def generar_preguntas_ia(texto_usuario):
    prompt = f"""
Eres un generador de preguntas tipo test para opositores. A partir del siguiente texto:

"{texto_usuario}"

Genera 3 preguntas tipo test en formato JSON con 4 opciones cada una, y marca la respuesta correcta. Devuelve solo el JSON sin explicaciones, así:

[
  {{
    "pregunta": "¿Cuál es la función del poder legislativo?",
    "opciones": ["Ejecutar leyes", "Interpretar leyes", "Crear leyes", "Proponer leyes"],
    "respuesta": "Crear leyes"
  }},
  ...
]
    """

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    contenido = completion.choices[0].message.content

    # Intentar extraer JSON de la respuesta
    match = re.search(r"\[\s*{.*?}\s*\]", contenido, re.DOTALL)
    if match:
        try:
            preguntas = json.loads(match.group())
        except Exception as e:
            preguntas = [{
                "pregunta": f"⚠️ Error al procesar el JSON: {str(e)}",
                "opciones": [],
                "respuesta": ""
            }]
    else:
        preguntas = [{
            "pregunta": "⚠️ No se encontró un bloque JSON válido en la respuesta de la IA.",
            "opciones": [],
            "respuesta": ""
        }]
    
    return preguntas

# INTERFAZ STREAMLIT
st.set_page_config(page_title="EvalúaYa - Generador IA", layout="centered")
st.markdown("## 🧠 EvalúaYa")
st.markdown("### Genera test tipo oposición desde cualquier texto con IA")

texto_input = st.text_area("📄 Pega aquí el texto sobre el que quieres generar preguntas", height=200)

if st.button("🎯 Generar test"):
    if not texto_input.strip():
        st.warning("⚠️ Introduce un texto válido para generar el test.")
    else:
        st.info("Generando test con IA... espera unos segundos.")
        preguntas = generar_preguntas_ia(texto_input)
        st.success("✅ Test generado:")

        for idx, p in enumerate(preguntas, start=1):
            st.markdown(f"### Pregunta {idx}")
            st.write(p["pregunta"])
            if p["opciones"]:
                st.radio("Opciones:", p["opciones"], key=f"preg_{idx}")
            else:
                st.warning("⚠️ No hay opciones disponibles.")

        st.caption(f"🆔 Test ID: {uuid.uuid4()} — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
