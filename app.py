import streamlit as st
import json
import time
import openai
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime
from uuid import uuid4

# Configura tu clave de API
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Inicializa cliente
client = openai.OpenAI()

def generar_preguntas_ia(texto, num_preguntas):
    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Eres un generador de preguntas tipo test para opositores."},
                {"role": "user", "content": f"""
A partir del siguiente texto:

{texto}

Genera {num_preguntas} preguntas tipo test en formato JSON con 4 opciones cada una, una correcta.
Formato:
[
  {{
    "pregunta": "...",
    "opciones": ["A...", "B...", "C...", "D..."],
    "respuesta": "A"
  }}
]
"""}
            ],
            temperature=0.7
        )
        contenido = completion.choices[0].message.content
        return json.loads(contenido)

    except openai.RateLimitError:
        time.sleep(5)
        return generar_preguntas_ia(texto, num_preguntas)

    except Exception as e:
        return [{"pregunta": f"⚠️ Error: {str(e)}", "opciones": [], "respuesta": ""}]

# Interfaz de usuario
st.set_page_config(page_title="EvalúaYa - Test por Temario")
st.title("🧠 EvalúaYa - Generador de Test por Temario")
st.markdown("### \U0001f58a Introduce el contenido del temario (puede ser un párrafo o más):")

texto_input = st.text_area("", height=200)
num_preguntas = st.slider("Número de preguntas a generar:", 3, 20, 5)

if "preguntas" not in st.session_state:
    st.session_state.preguntas = []

if st.button("🎯 Generar test"):
    if texto_input.strip():
        st.info("Generando test con IA... espera unos segundos.")
        st.session_state.preguntas = generar_preguntas_ia(texto_input, num_preguntas)
        st.success("Test generado con éxito.")

if st.session_state.preguntas:
    for i, p in enumerate(st.session_state.preguntas, 1):
        st.markdown(f"**Pregunta {i}**\n{p['pregunta']}")
        st.radio("Opciones:", p['opciones'], index=None, key=f"pregunta_{i}")

    def exportar_test_y_soluciones(preguntas):
        buffer_test = BytesIO()
        buffer_sol = BytesIO()
        c_test = canvas.Canvas(buffer_test, pagesize=A4)
        c_sol = canvas.Canvas(buffer_sol, pagesize=A4)

        c_test.setFont("Helvetica", 12)
        c_sol.setFont("Helvetica", 12)

        y = 800
        for i, p in enumerate(preguntas, 1):
            c_test.drawString(50, y, f"{i}. {p['pregunta']}")
            c_sol.drawString(50, y, f"{i}. {p['pregunta']}")
            y -= 20
            for idx, opcion in enumerate(p['opciones']):
                letra = chr(65 + idx)
                c_test.drawString(70, y, f"({letra}) {opcion}")
                c_sol.drawString(70, y, f"({letra}) {opcion}")
                if letra == p['respuesta']:
                    c_sol.drawString(400, y, "✔")
                y -= 20
            y -= 10
            if y < 100:
                c_test.showPage()
                c_sol.showPage()
                y = 800

        c_test.save()
        c_sol.save()
        buffer_test.seek(0)
        buffer_sol.seek(0)
        return buffer_test, buffer_sol

    test_pdf, sol_pdf = exportar_test_y_soluciones(st.session_state.preguntas)
    st.download_button("📄 Descargar test completo (con soluciones)", data=sol_pdf, file_name=f"test_resuelto_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")

    if st.button("🔁 Resetear test"):
        st.session_state.clear()
        st.rerun()
