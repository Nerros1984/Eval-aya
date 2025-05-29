from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import streamlit as st
import openai
import json
import re
import tempfile
from docx import Document

st.set_page_config(page_title="EvalúaYa - Generador de Test por Temario", layout="centered")
st.title("🧠 EvalúaYa - Generador de Test por Temario")

# --------------------
# FUNCIONES AUXILIARES
# --------------------

def leer_docx(doc_file):
    doc = Document(doc_file)
    texto = "\n".join([p.text for p in doc.paragraphs if p.text.strip() != ""])
    return texto

def extraer_json_valido(respuesta):
    texto = respuesta.strip().strip("`")
    if texto.startswith("json"):
        texto = texto[len("json"):].strip()
    patron_json = re.search(r'$begin:math:display$\\s*{.*?}\\s*$end:math:display$', texto, re.DOTALL)
    if patron_json:
        return patron_json.group(0)
    return texto

def generar_preguntas_ia(texto, num_preguntas):
    prompt = (
        f"Eres un generador de preguntas tipo test. A partir del siguiente texto:\n\n"
        f"{texto}\n\n"
        f"Genera {num_preguntas} preguntas tipo test en formato JSON con exactamente 4 opciones, "
        "y una de ellas debe ser correcta. Devuelve solo el JSON con esta estructura:\n\n"
        "[\n"
        "  {\n"
        "    \"pregunta\": \"Texto de la pregunta\",\n"
        "    \"opciones\": [\"Opción A\", \"Opción B\", \"Opción C\", \"Opción D\"],\n"
        "    \"respuesta\": \"Letra de la opción correcta (A, B, C o D)\"\n"
        "  },\n"
        "  ...\n"
        "]"
    )
    try:
        client = openai.OpenAI(api_key=st.secrets["openai_api_key"])
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        content = completion.choices[0].message.content
        json_limpio = extraer_json_valido(content)
        preguntas = json.loads(json_limpio)
        return preguntas
    except:
        return None

def exportar_pdf(preguntas):
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    c = canvas.Canvas(temp_file.name, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, height - 60, "Preguntas del test")
    c.setFont("Helvetica", 12)
    y = height - 100
    for i, p in enumerate(preguntas):
        c.drawString(50, y, f"{i+1}. {p['pregunta']}")
        y -= 20
        for op in p["opciones"]:
            c.drawString(70, y, f"- {op}")
            y -= 18
        y -= 10
        if y < 100:
            c.showPage()
            y = height - 60

    c.showPage()
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, height - 60, "Respuestas correctas")
    c.setFont("Helvetica", 12)
    y = height - 100
    for i, p in enumerate(preguntas):
        c.drawString(50, y, f"{i+1}. Respuesta: {p['respuesta']}")
        y -= 20
        if y < 100:
            c.showPage()
            y = height - 60

    c.save()
    return temp_file.name

# --------------------
# INTERFAZ PRINCIPAL
# --------------------

texto_input = ""
archivo = st.file_uploader("📄 O sube un documento Word (.docx)", type=["docx"])
if archivo:
    texto_input = leer_docx(archivo)
    st.success("Documento cargado correctamente.")
    st.write(texto_input[:800] + "...")

texto_manual = st.text_area("✍️ O escribe directamente el contenido del temario:", height=300)
if texto_manual.strip():
    texto_input = texto_manual

num_preguntas = st.slider("Número de preguntas a generar:", min_value=3, max_value=25, value=5)

# Estados persistentes
if "respuestas_usuario" not in st.session_state:
    st.session_state["respuestas_usuario"] = {}

if "preguntas_generadas" not in st.session_state:
    st.session_state["preguntas_generadas"] = []

# Botón de generar test
if st.button("🧪 Generar test"):
    if texto_input.strip() == "":
        st.warning("Debes introducir contenido para generar el test.")
    else:
        with st.spinner("Generando test con IA... espera unos segundos."):
            preguntas = generar_preguntas_ia(texto_input, num_preguntas)

        if preguntas:
            st.session_state["preguntas_generadas"] = preguntas
            st.session_state["respuestas_usuario"] = {}
            st.success("✅ Test generado con éxito.")

# Mostrar preguntas y respuestas
if st.session_state["preguntas_generadas"]:
    preguntas = st.session_state["preguntas_generadas"]
    respuestas_usuario = st.session_state["respuestas_usuario"]

    st.markdown("## 🧠 Test")
    for i, pregunta in enumerate(preguntas):
        st.markdown(f"**{i+1}. {pregunta['pregunta']}**")
        respuesta = st.radio(
            f"Selecciona una opción:",
            options=pregunta["opciones"],
            key=f"pregunta_{i}"
        )
        respuestas_usuario[i] = respuesta
        st.divider()

    # Botón para corregir test
    if st.button("✅ Corregir"):
        st.markdown("## 📊 Resultados del test")
        aciertos = 0
        for i, pregunta in enumerate(preguntas):
            correcta = pregunta["opciones"][["A", "B", "C", "D"].index(pregunta["respuesta"])]
            elegida = respuestas_usuario.get(i, "")
            if elegida == correcta:
                st.markdown(f"✅ **{i+1}. Correcta** — {pregunta['pregunta']}")
                aciertos += 1
            else:
                st.markdown(f"❌ **{i+1}. Incorrecta** — {pregunta['pregunta']}")
                st.markdown(f"- Tu respuesta: {elegida if elegida else 'Sin responder'}")
                st.markdown(f"- 🔵 Correcta: {correcta}")

        st.success(f"Puntuación final: {aciertos}/{len(preguntas)}")

        # Botón para descargar PDF
        pdf_path = exportar_pdf(preguntas)
        with open(pdf_path, "rb") as f:
            st.download_button(
                label="📄 Descargar test en PDF",
                data=f,
                file_name="test_generado.pdf",
                mime="application/pdf"
            )
