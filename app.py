from datetime import datetime
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import streamlit as st
import openai
import json
import tempfile

# Configuración de página
st.set_page_config(page_title="EvalúaYa - Generador de Test por Temario", layout="centered")

st.title("🧠 EvalúaYa - Generador de Test por Temario")
st.markdown("✍️ **Introduce el contenido del temario** (puede ser un párrafo o más):")

# Inputs de usuario
texto_input = st.text_area(" ", height=200, label_visibility="collapsed")
num_preguntas = st.slider("Número de preguntas a generar:", min_value=3, max_value=20, value=5)

# Funcíon para generar preguntas con IA
def generar_preguntas_ia(texto, num_preguntas):
    prompt = f"""Eres un generador de preguntas tipo test. A partir del siguiente texto:

\"\"\"{texto}\"\"\"

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
        preguntas = json.loads(content)
        return preguntas
    except Exception:
        st.error("⚠️ No ha sido posible generar el test. Inténtalo más tarde.")
        return None

# Funcíon para exportar test y soluciones
def exportar_test_y_soluciones(preguntas):
    test_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    sol_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

    # Test PDF
    c = canvas.Canvas(test_temp.name, pagesize=A4)
    width, height = A4
    c.setFont("Helvetica", 12)
    y = height - 50
    for i, p in enumerate(preguntas):
        c.drawString(50, y, f"{i+1}. {p['pregunta']}")
        y -= 20
        for letra, opcion in zip(["A", "B", "C", "D"], p["opciones"]):
            c.drawString(70, y, f"( ) {letra}. {opcion}")
            y -= 20
        y -= 10
        if y < 100:
            c.showPage()
            y = height - 50
    c.save()

    # Soluciones PDF
    c = canvas.Canvas(sol_temp.name, pagesize=A4)
    y = height - 50
    c.setFont("Helvetica", 12)
    for i, p in enumerate(preguntas):
        c.drawString(50, y, f"{i+1}. {p['pregunta']}")
        y -= 20
        c.drawString(70, y, f"✅ Respuesta correcta: {p['respuesta']}")
        y -= 30
        if y < 100:
            c.showPage()
            y = height - 50
    c.save()

    return test_temp.name, sol_temp.name

# Estado de la app
if "test_generado" not in st.session_state:
    st.session_state.test_generado = False
    st.session_state.preguntas = None

# Generar test
if st.button("🎯 Generar test"):
    if not texto_input.strip():
        st.warning("⚠️ Introduce el contenido del temario para generar el test.")
    else:
        st.info("Generando test con IA... espera unos segundos.")
        preguntas = generar_preguntas_ia(texto_input.strip(), num_preguntas)
        if preguntas:
            st.session_state.preguntas = preguntas
            st.session_state.test_generado = True
            st.success("✅ Test generado con éxito.")

# Mostrar test y descargas si está generado
if st.session_state.test_generado and st.session_state.preguntas:
    st.markdown("---")
    for i, p in enumerate(st.session_state.preguntas):
        st.markdown(f"### Pregunta {i+1}")
        st.markdown(f"**{p['pregunta']}**")
        for opcion in p["opciones"]:
            st.radio("Opciones:", p["opciones"], index=-1, key=f"{i}_{opcion}", label_visibility="collapsed", disabled=True)

    # Exportar PDF
    test_file, sol_file = exportar_test_y_soluciones(st.session_state.preguntas)
    with open(test_file, "rb") as f1, open(sol_file, "rb") as f2:
        st.download_button("📄 Descargar test (solo preguntas)", f1, file_name="test.pdf")
        st.download_button("📄 Descargar soluciones", f2, file_name="soluciones.pdf")

    # Botón de reset
    if st.button("🔁 Resetear test"):
        st.session_state.test_generado = False
        st.session_state.preguntas = None
        st.rerun()
