
import streamlit as st
from openai import OpenAI
import json
import re
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
import tempfile

st.set_page_config(page_title="EvalúaYa - Generador de Test", layout="centered")

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
        respuesta = p.get("respuesta", "")
        opciones = p.get("opciones", [])
        letra_correcta = next((l for l, o in zip("ABCD", opciones) if o == respuesta), "?")
        c.drawString(2 * cm, y, f"{i}. {p['pregunta']}")
        y -= 1 * cm
        c.drawString(2.5 * cm, y, f"✔ Respuesta correcta: ({letra_correcta}) {respuesta}")
        y -= 1 * cm
        if y < 4 * cm:
            c.showPage()
            y = height - 2 * cm
            c.setFont("Helvetica", 12)

    c.save()
    return temp_pdf.name

# Interfaz
st.title("🧠 EvalúaYa - Generador de Test por Temario")

if "test_generado" not in st.session_state:
    st.session_state.test_generado = False

if not st.session_state.test_generado:
    texto = st.text_area("✍️ Introduce el contenido del temario (puede ser un párrafo o más):", height=250)
    n_preguntas = st.slider("Número de preguntas a generar:", 3, 20, 5)

    if st.button("🎯 Generar test") and texto.strip():
        with st.spinner("Generando preguntas..."):
            preguntas = generar_preguntas_ia(texto, n_preguntas)
            st.session_state.test_generado = True
            st.session_state.preguntas = preguntas
            st.experimental_rerun()
else:
    st.subheader("📋 Preguntas generadas")
    for i, p in enumerate(st.session_state.preguntas, 1):
        st.markdown(f"**{i}. {p['pregunta']}**")
        for letra, opcion in zip("ABCD", p.get("opciones", [])):
            st.markdown(f"- ({letra}) {opcion}")

    pdf_path = exportar_test_completo(st.session_state.preguntas)
    with open(pdf_path, "rb") as f:
        st.download_button(
            label="📥 Descargar test completo (con soluciones)",
            data=f,
            file_name="test_evaluaYA.pdf",
            mime="application/pdf"
        )

    if st.button("🔁 Resetear test"):
        st.session_state.clear()
        st.experimental_rerun()
