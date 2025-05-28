
import streamlit as st
from openai import OpenAI
import uuid
from datetime import datetime
import json
import re
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
import tempfile

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

def exportar_test_y_soluciones(preguntas):
    temp_test = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    temp_sol = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    width, height = A4

    def crear_pdf(ruta, titulo, contenido):
        c = canvas.Canvas(ruta, pagesize=A4)
        y = height - 2 * cm
        c.setFont("Helvetica", 12)
        c.drawCentredString(width / 2, y, titulo)
        y -= 1.5 * cm

        for i, p in enumerate(contenido, 1):
            c.drawString(2 * cm, y, f"{i}. {p['pregunta']}")
            y -= 1 * cm
            for linea in p["extra"]:
                c.drawString(2.5 * cm, y, linea)
                y -= 0.8 * cm
            y -= 0.5 * cm
            if y < 4 * cm:
                c.showPage()
                y = height - 2 * cm
                c.setFont("Helvetica", 12)
        c.save()

    test_content = [{"pregunta": p["pregunta"], "extra": [f"({letra}) ( ) {o}" for letra, o in zip("ABCD", p["opciones"])]} for p in preguntas]
    sol_content = [{"pregunta": p["pregunta"], "extra": [f"✔ Respuesta correcta: {p.get('respuesta', '[respuesta inválida]')}"]} for p in preguntas]

    crear_pdf(temp_test.name, "TEST - EvalúaYa", test_content)
    crear_pdf(temp_sol.name, "SOLUCIONES - EvalúaYa", sol_content)

    return temp_test.name, temp_sol.name

# Streamlit UI
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
