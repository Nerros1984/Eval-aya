import streamlit as st
import json
import openai
from datetime import datetime
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# Configuración de página
st.set_page_config(page_title="EvalúaYa - Generador de Test", layout="centered")

# Función para generar preguntas con IA
def generar_preguntas_ia(texto, num_preguntas):
    client = openai.OpenAI(api_key=st.secrets["openai_api_key"])
    prompt = f"""
Eres un generador de preguntas tipo test para opositores. A partir del siguiente texto:

f"""{texto}"""

Genera {num_preguntas} preguntas tipo test en formato JSON con 4 opciones (A, B, C, D) y señala cuál es la respuesta correcta. Devuelve algo como esto:

[
  {{
    "pregunta": "...",
    "opciones": ["...", "...", "...", "..."],
    "respuesta": "A"
  }},
  ...
]
"""
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    contenido = completion.choices[0].message.content
    try:
        preguntas = json.loads(contenido)
    except:
        preguntas = []
    return preguntas

# Generar PDFs
def exportar_test_y_soluciones(preguntas):
    buffer_test = BytesIO()
    buffer_sol = BytesIO()
    test_pdf = canvas.Canvas(buffer_test, pagesize=A4)
    sol_pdf = canvas.Canvas(buffer_sol, pagesize=A4)
    width, height = A4

    test_pdf.setFont("Helvetica", 12)
    sol_pdf.setFont("Helvetica", 12)

    y_test = height - 50
    y_sol = height - 50

    for idx, p in enumerate(preguntas, start=1):
        pregunta = p["pregunta"]
        opciones = p["opciones"]
        respuesta = p["respuesta"]

        test_pdf.drawString(50, y_test, f"Pregunta {idx}: {pregunta}")
        for i, opcion in enumerate(opciones):
            letra = chr(65 + i)
            y_test -= 15
            test_pdf.drawString(70, y_test, f"( ) {letra}) {opcion}")
        y_test -= 30

        sol_pdf.drawString(50, y_sol, f"Pregunta {idx}: Respuesta correcta: {respuesta}) {opciones[ord(respuesta) - 65]}")
        y_sol -= 30

    test_pdf.save()
    sol_pdf.save()

    buffer_test.seek(0)
    buffer_sol.seek(0)

    return buffer_test, buffer_sol

# UI principal
st.title("🧠 EvalúaYa - Generador de Test por Temario")
st.markdown("✍️ Introduce el contenido del temario (puede ser un párrafo o más):")

texto_input = st.text_area(" ", height=200)

num_preguntas = st.slider("Número de preguntas a generar:", min_value=3, max_value=20, value=3)

if "test_generado" not in st.session_state:
    st.session_state.test_generado = False

if st.button("🎯 Generar test"):
    if not texto_input.strip():
        st.warning("⚠️ Por favor, introduce un texto para generar el test.")
    else:
        try:
            with st.spinner("Generando test con IA... espera unos segundos."):
                preguntas = generar_preguntas_ia(texto_input.strip(), num_preguntas)
            st.success("✅ Test generado con éxito.")
            st.session_state.test_generado = True
            st.session_state.preguntas = preguntas
        except openai.RateLimitError:
            st.error("⚠️ No ha sido posible generar el test. Has alcanzado el límite de uso de la IA. Inténtalo de nuevo más tarde.")
            st.stop()
        except Exception as e:
            st.error(f"❌ Se ha producido un error al generar el test: {str(e)}")
            st.stop()

if st.session_state.get("test_generado", False):
    preguntas = st.session_state.preguntas

    for idx, p in enumerate(preguntas, start=1):
        st.markdown(f"### Pregunta {idx}")
        st.markdown(p["pregunta"])
        st.radio("Opciones:", p["opciones"], index=None, key=f"pregunta_{idx}")

    test_pdf, sol_pdf = exportar_test_y_soluciones(preguntas)
    col1, col2 = st.columns(2)

    with col1:
        st.download_button("📄 Descargar test", data=test_pdf, file_name="test.pdf", mime="application/pdf")
    with col2:
        st.download_button("📄 Descargar test completo (con soluciones)", data=sol_pdf, file_name="test_soluciones.pdf", mime="application/pdf")

    if st.button("🔄 Resetear test"):
        st.session_state.clear()
        st.experimental_rerun()
