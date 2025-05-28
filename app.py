
import streamlit as st
from openai import OpenAI
import uuid
from datetime import datetime
import json
import re
from fpdf import FPDF
import tempfile

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

class PDF(FPDF):
    pass

def generar_preguntas_ia(texto_usuario, n_preguntas):
    prompt = f"""
Eres un generador de preguntas tipo test para opositores. A partir del siguiente texto:

"{texto_usuario}"

Genera {n_preguntas} preguntas tipo test en formato JSON con 4 opciones cada una, y marca la respuesta correcta. Devuelve solo el JSON sin explicaciones, así:

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
    match = re.search(r"\[\s*{.*?}\s*\]", contenido, re.DOTALL)

    if match:
        try:
            preguntas = json.loads(match.group())
        except Exception as e:
            preguntas = [{"pregunta": f"⚠️ Error JSON: {str(e)}", "opciones": [], "respuesta": ""}]
    else:
        preguntas = [{"pregunta": "⚠️ No se encontró un JSON válido.", "opciones": [], "respuesta": ""}]

    return preguntas

def exportar_test_y_soluciones(preguntas):
    font_path = "fonts/Roboto-Regular.ttf"

    pdf_test = PDF()
    pdf_test.add_page()
    pdf_test.add_font("Roboto", "", font_path, uni=True)
    pdf_test.set_font("Roboto", size=12)
    pdf_test.cell(200, 10, txt="TEST - EvalúaYa", ln=True, align="C")
    pdf_test.ln(10)

    for i, p in enumerate(preguntas, 1):
        pdf_test.multi_cell(0, 10, f"{i}. {p['pregunta']}")
        for letra, opcion in zip("ABCD", p["opciones"]):
            pdf_test.cell(0, 10, f"   ({letra}) ( ) {opcion}", ln=True)
        pdf_test.ln(5)

    temp_test = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf_test.output(temp_test.name)

    pdf_sol = PDF()
    pdf_sol.add_page()
    pdf_sol.add_font("Roboto", "", font_path, uni=True)
    pdf_sol.set_font("Roboto", size=12)
    pdf_sol.cell(200, 10, txt="SOLUCIONES - EvalúaYa", ln=True, align="C")
    pdf_sol.ln(10)

    for i, p in enumerate(preguntas, 1):
        pdf_sol.multi_cell(0, 10, f"{i}. {p['pregunta']}")
        respuesta = p.get("respuesta", "").strip() or "[respuesta vacía]"
        pdf_sol.multi_cell(0, 10, f"   Respuesta correcta: {respuesta}")
        pdf_sol.ln(5)

    temp_sol = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf_sol.output(temp_sol.name)

    return temp_test.name, temp_sol.name

st.set_page_config(page_title="EvalúaYa - Generador IA", layout="centered")
st.markdown("## 🧠 EvalúaYa")
st.markdown("### Genera test tipo oposición desde cualquier texto con IA")

texto_input = st.text_area("📄 Pega aquí el texto sobre el que quieres generar preguntas", height=200)
n_preguntas = st.slider("Número de preguntas a generar", 1, 10, 3)

if st.button("🎯 Generar test"):
    if not texto_input.strip():
        st.warning("⚠️ Introduce un texto válido para generar el test.")
    else:
        st.info("Generando test con IA... espera unos segundos.")
        preguntas = generar_preguntas_ia(texto_input, n_preguntas)
        st.success("✅ Test generado:")

        for idx, p in enumerate(preguntas, start=1):
            st.markdown(f"### Pregunta {idx}")
            st.write(p["pregunta"])
            if p["opciones"]:
                st.radio("Opciones:", p["opciones"], key=f"preg_{idx}")
            else:
                st.warning("⚠️ No hay opciones disponibles.")

        # Generar y mostrar botones de descarga
        test_pdf, sol_pdf = exportar_test_y_soluciones(preguntas)

        with open(test_pdf, "rb") as file:
            st.download_button(
                label="📥 Descargar test (PDF)",
                data=file,
                file_name="test_evalua_ya.pdf",
                mime="application/pdf"
            )

        with open(sol_pdf, "rb") as file:
            st.download_button(
                label="📥 Descargar soluciones (PDF)",
                data=file,
                file_name="soluciones_evalua_ya.pdf",
                mime="application/pdf"
            )
