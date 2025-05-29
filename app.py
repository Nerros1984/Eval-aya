from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import streamlit as st
import openai
import json
import re
import tempfile
import unicodedata
from utils.drive import subir_archivo_a_drive
from utils.sheets import registrar_en_sheet

st.set_page_config(page_title="EvalúaYa - Generador de Test por Temario", layout="centered")

st.title("🧠 EvalúaYa - Generador de Test por Temario")
st.markdown("📄 **Sube un archivo DOCX o PDF con tu temario:**")

archivo_subido = st.file_uploader("Subir temario (DOCX o PDF)", type=["pdf", "docx"])
tipo_contenido = st.selectbox("¿Qué contiene este archivo?", ["Temario completo", "Resumen", "Tema individual"])
oposicion = st.text_input("📝 Nombre de la oposición (Ej: Administrativo Junta Andalucía)")

num_preguntas = st.slider("Número de preguntas a generar:", min_value=3, max_value=25, value=5)


def normalizar_nombre(nombre):
    nfkd = unicodedata.normalize('NFKD', nombre)
    solo_ascii = nfkd.encode('ASCII', 'ignore').decode('utf-8')
    return solo_ascii.lower().replace(" ", "_")


def extraer_json_valido(respuesta):
    texto = respuesta.strip().strip("`")
    if texto.startswith("json"):
        texto = texto[len("json"):].strip()
    patron_json = re.search(r'\[\s*{.*?}\s*\]', texto, re.DOTALL)
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


if archivo_subido and oposicion.strip():
    contenido_archivo = archivo_subido.read().decode("utf-8", errors="ignore")
    if st.button("🧪 Generar test"):
        with st.spinner("Generando test con IA... espera unos segundos."):
            preguntas = generar_preguntas_ia(contenido_archivo, num_preguntas)

        if preguntas:
            st.success("✅ Test generado con éxito.")
            for i, pregunta in enumerate(preguntas):
                st.markdown(f"### Pregunta {i + 1}")
                st.write(pregunta["pregunta"])
                st.radio(
                    "Selecciona una opción:",
                    options=pregunta["opciones"],
                    key=f"pregunta_{i}"
                )
                st.divider()

            pdf_path = exportar_pdf(preguntas)
            json_data = json.dumps(preguntas, indent=2)
            json_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
            json_temp.write(json_data.encode("utf-8"))
            json_temp.close()

            # Subida de archivos
            temario_normalizado = normalizar_nombre(oposicion)
            url_pdf = subir_archivo_a_drive(pdf_path, temario_normalizado)
            url_json = subir_archivo_a_drive(json_temp.name, temario_normalizado)

            registrar_en_sheet(
                oposicion,
                tipo_contenido,
                url_pdf,
                url_json,
                datetime.now().strftime("%Y-%m-%d %H:%M")
            )

            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="📄 Descargar test en PDF",
                    data=f,
                    file_name="test_generado.pdf",
                    mime="application/pdf"
                )
        else:
            st.error("❌ No se pudo generar el test. Intenta con otro contenido.")
else:
    st.info("🔼 Sube un archivo válido y escribe un nombre de oposición para comenzar.")
