
import streamlit as st
from openai import OpenAI
import json
import re
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
import tempfile
from datetime import datetime

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

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

def exportar_test_completo(preguntas):
    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    c = canvas.Canvas(temp_pdf.name, pagesize=A4)
    width, height = A4
    y = height - 2 * cm
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width / 2, y, "TEST - EvalúaYa")
    y -= 1.5 * cm
    c.setFont("Helvetica", 12)

    for i, p in enumerate(preguntas, 1):
        c.drawString(2 * cm, y, f"{i}. {p['pregunta']}")
        y -= 1 * cm
        for letra, opcion in zip("ABCD", p.get("opciones", [])):
            c.drawString(2.5 * cm, y, f"({letra}) ( ) {opcion}")
            y -= 0.8 * cm
        y -= 0.5 * cm
        if y < 4 * cm:
            c.showPage()
            y = height - 2 * cm
            c.setFont("Helvetica", 12)

    c.showPage()
    y = height - 2 * cm
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width / 2, y, "SOLUCIONES")
    y -= 1.5 * cm
    c.setFont("Helvetica", 12)

    for i, p in enumerate(preguntas, 1):
        c.drawString(2 * cm, y, f"{i}. {p['pregunta']}")
        y -= 1 * cm
        c.drawString(2.5 * cm, y, f"✔ Respuesta correcta: {p.get('respuesta', '')}")
        y -= 1 * cm
        if y < 4 * cm:
            c.showPage()
            y = height - 2 * cm
            c.setFont("Helvetica", 12)

    c.save()
    return temp_pdf.name

# INTERFAZ STREAMLIT
st.set_page_config(page_title="EvalúaYa - Generador IA", layout="centered")
st.title("🧠 EvalúaYa")
st.subheader("Genera test tipo oposición desde cualquier texto con IA")

if "preguntas" not in st.session_state:
    st.session_state.preguntas = None

texto_input = st.text_area("📄 Pega aquí el texto sobre el que quieres generar preguntas", height=200)
n_preguntas = st.slider("Número de preguntas a generar", 1, 10, 3)

col1, col2 = st.columns([1, 1])
with col1:
    if st.button("🎯 Generar test"):
        if not texto_input.strip():
            st.warning("⚠️ Introduce un texto válido.")
        else:
            st.info("🛠 Generando test con IA...")
            st.session_state.preguntas = generar_preguntas_ia(texto_input, n_preguntas)

with col2:
    if st.session_state.preguntas:
        if st.button("🔁 Resetear test"):
            st.session_state.preguntas = None

if st.session_state.preguntas:
    st.success("✅ Test generado:")
    for idx, p in enumerate(st.session_state.preguntas, start=1):
        st.markdown(f"### Pregunta {idx}")
        st.write(p["pregunta"])
        if p["opciones"]:
            st.radio("Opciones:", p["opciones"], key=f"preg_{idx}")
        else:
            st.warning("⚠️ No hay opciones disponibles.")

    test_pdf = exportar_test_completo(st.session_state.preguntas)
    with open(test_pdf, "rb") as file:
        st.download_button(
            label="📥 Descargar test completo (con soluciones)",
            data=file,
            file_name="evalua_test_completo.pdf",
            mime="application/pdf"
        )
