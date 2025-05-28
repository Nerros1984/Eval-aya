
import streamlit as st
from openai import OpenAI
import json
import uuid
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# Configuración inicial
st.set_page_config(page_title="EvalúaYa - Generador de Test por Temario")

st.markdown("## 🧠 EvalúaYa - Generador de Test por Temario")
st.markdown("### ✍️ Introduce el contenido del temario (puede ser un párrafo o más):")

# Función para generar preguntas con IA
def generar_preguntas_ia(texto, num_preguntas=3):
    client = OpenAI()
    prompt = f"""Eres un generador de preguntas tipo test para opositores. A partir del siguiente texto:

{texto}

Genera {num_preguntas} preguntas tipo test en formato JSON. Cada pregunta debe tener 4 opciones (A, B, C, D), con una única opción correcta.

Devuelve el resultado en este formato exacto:
[
  {{
    "pregunta": "¿Pregunta 1?",
    "opciones": ["Opción A", "Opción B", "Opción C", "Opción D"],
    "respuesta": "Opción correcta"
  }},
  ...
]
"""

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    contenido = completion.choices[0].message.content
    try:
        preguntas = json.loads(contenido)
    except:
        preguntas = []
    return preguntas

# Función para exportar test y soluciones en PDF
def exportar_test_y_soluciones(preguntas):
    buffer_test = BytesIO()
    buffer_sol = BytesIO()

    pdf_test = canvas.Canvas(buffer_test, pagesize=A4)
    pdf_sol = canvas.Canvas(buffer_sol, pagesize=A4)

    width, height = A4
    y_test = height - 50
    y_sol = height - 50

    for i, p in enumerate(preguntas, 1):
        pregunta = p["pregunta"]
        opciones = p["opciones"]
        respuesta = p["respuesta"]
        letra_correcta = "ABCD"[opciones.index(respuesta)]

        pdf_test.drawString(40, y_test, f"{i}. {pregunta}")
        y_test -= 20
        for letra, opcion in zip("ABCD", opciones):
            pdf_test.drawString(60, y_test, f"( ) {letra}. {opcion}")
            y_test -= 20
        y_test -= 10

        pdf_sol.drawString(40, y_sol, f"{i}. {pregunta}")
        y_sol -= 20
        pdf_sol.drawString(60, y_sol, f"✅ Respuesta correcta: {letra_correcta}. {respuesta}")
        y_sol -= 30

        if y_test < 100:
            pdf_test.showPage()
            y_test = height - 50
        if y_sol < 100:
            pdf_sol.showPage()
            y_sol = height - 50

    pdf_test.save()
    pdf_sol.save()
    buffer_test.seek(0)
    buffer_sol.seek(0)
    return buffer_test, buffer_sol

# INTERFAZ STREAMLIT
if "preguntas" not in st.session_state:
    st.session_state.preguntas = []

texto_input = st.text_area("✍️ Pega aquí el texto sobre el que quieres generar preguntas", height=200)

num_preguntas = st.slider("Número de preguntas a generar:", min_value=3, max_value=20, value=5)

if st.button("🎯 Generar test"):
    if texto_input.strip():
        st.info("Generando test con IA... espera unos segundos.")
        preguntas = generar_preguntas_ia(texto_input.strip(), num_preguntas)
        if preguntas:
            st.session_state.preguntas = preguntas
            st.success("✅ Test generado con éxito.")
        else:
            st.error("❌ Error al generar preguntas. Intenta nuevamente.")

if st.session_state.preguntas:
    for idx, p in enumerate(st.session_state.preguntas, 1):
        st.markdown(f"### Pregunta {idx}")
        st.markdown(p["pregunta"])
        st.radio("Opciones:", p["opciones"], key=f"pregunta_{idx}")

    test_pdf, sol_pdf = exportar_test_y_soluciones(st.session_state.preguntas)

    st.download_button("📥 Descargar test completo (con soluciones)", test_pdf, file_name="test_preguntas.pdf")
    st.download_button("📄 Descargar solo soluciones", sol_pdf, file_name="soluciones.pdf")

    if st.button("🔄 Resetear test"):
        st.session_state.clear()
        st.rerun()
