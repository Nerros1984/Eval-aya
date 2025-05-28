
import streamlit as st
import uuid
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import json
import openai

# Configuración inicial
st.set_page_config(page_title="EvalúaYa - Generador de Test", layout="centered")

st.markdown("## 🧠 EvalúaYa - Generador de Test por Temario")
st.markdown("✍️ Introduce el contenido del temario (puede ser un párrafo o más):")

# Inputs
texto_usuario = st.text_area(" ", height=200)
num_preguntas = st.slider("Número de preguntas a generar:", 3, 20, 5)

# Función para generar preguntas
def generar_preguntas(texto, cantidad):
    prompt = f"""
Eres un generador de preguntas tipo test para oposiciones. A partir del siguiente texto:

"""{texto}"""

Genera {cantidad} preguntas tipo test en formato JSON. Cada pregunta debe tener 4 opciones (A, B, C, D) y una sola correcta. Devuelve solo la estructura como esta:

[
  {{
    "pregunta": "...",
    "opciones": ["...", "...", "...", "..."],
    "respuesta": "..."
  }},
  ...
]
"""
    client = openai.OpenAI(api_key=st.secrets["api_key"])
    respuesta = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    contenido = respuesta.choices[0].message.content
    try:
        preguntas = json.loads(contenido)
    except:
        preguntas = []
    return preguntas

# Función para exportar a PDF
def exportar_test_y_soluciones(preguntas):
    test_pdf = BytesIO()
    sol_pdf = BytesIO()
    c_test = canvas.Canvas(test_pdf, pagesize=A4)
    c_sol = canvas.Canvas(sol_pdf, pagesize=A4)
    w, h = A4

    c_test.setFont("Helvetica", 12)
    c_sol.setFont("Helvetica", 12)

    y_test = h - 40
    y_sol = h - 40

    for i, p in enumerate(preguntas, 1):
        c_test.drawString(40, y_test, f"Pregunta {i}: {p['pregunta']}")
        y_test -= 20
        for j, opcion in enumerate(p["opciones"]):
            letra = chr(65 + j)
            c_test.drawString(60, y_test, f"({letra}) {opcion}")
            y_test -= 20
        y_test -= 10

        c_sol.drawString(40, y_sol, f"Pregunta {i}: {p['pregunta']}")
        y_sol -= 20
        correcta = p["respuesta"]
        for j, opcion in enumerate(p["opciones"]):
            letra = chr(65 + j)
            if opcion == correcta:
                c_sol.drawString(60, y_sol, f"✅ ({letra}) {opcion}")
            else:
                c_sol.drawString(60, y_sol, f"({letra}) {opcion}")
            y_sol -= 20
        y_sol -= 10

    c_test.save()
    c_sol.save()
    test_pdf.seek(0)
    sol_pdf.seek(0)
    return test_pdf, sol_pdf

# Generación
if "test_generado" not in st.session_state:
    st.session_state.test_generado = False
    st.session_state.preguntas = []

if not st.session_state.test_generado:
    if st.button("🎯 Generar test"):
        if texto_usuario.strip():
            st.info("Generando test con IA... espera unos segundos.")
            preguntas = generar_preguntas(texto_usuario, num_preguntas)
            if preguntas:
                st.session_state.preguntas = preguntas
                st.session_state.test_generado = True
                st.success("✅ Test generado con éxito.")
        else:
            st.warning("⚠️ Por favor, introduce un texto antes de generar.")
else:
    preguntas = st.session_state.preguntas
    for i, p in enumerate(preguntas, 1):
        st.markdown(f"**Pregunta {i}**")
        st.markdown(p["pregunta"])
        st.radio("Opciones:", p["opciones"], index=None, key=str(uuid.uuid4()))

    test_pdf, sol_pdf = exportar_test_y_soluciones(preguntas)

    st.download_button("📄 Descargar test completo (con soluciones)", test_pdf, file_name="test.pdf")
    st.download_button("📄 Descargar soluciones", sol_pdf, file_name="soluciones.pdf")

    if st.button("🔄 Resetear test"):
        st.session_state.clear()
        st.rerun()
