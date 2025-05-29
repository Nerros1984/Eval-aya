from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import streamlit as st
import openai
import json
import re
import tempfile
import unicodedata
import os

from utils.drive import subir_archivo_a_drive, CARPETA_TEMARIOS
from utils.sheets import registrar_en_sheet

st.set_page_config(page_title="EvalúaYa - Generador de Test por Temario", layout="centered")

st.title("🧠 EvalúaYa - Generador de Test por Temario")
st.markdown("📄 **Sube un archivo DOCX o PDF con tu temario:**")

archivo_subido = st.file_uploader("Subir temario (DOCX o PDF)", type=["pdf", "docx"])
tipo_contenido = st.selectbox("🔎¿Qué contiene este archivo?", ["Temario completo", "Resumen", "Tema individual"])
nombre_oposicion = st.text_input("📜 Nombre de la oposición (Ej: Administrativo Junta Andalucía)")

if archivo_subido and nombre_oposicion.strip():
    if st.button("✅ Guardar y registrar temario"):
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(archivo_subido.name)[1]) as tmp:
                tmp.write(archivo_subido.read())
                tmp_path = tmp.name

            url_drive = subir_archivo_a_drive(tmp_path, nombre_oposicion, CARPETA_TEMARIOS)

            registrar_en_sheet(
                nombre_oposicion,
                tipo_contenido,
                url_drive,
                "",
                datetime.now().strftime("%Y-%m-%d %H:%M")
            )

            st.success("✅ Temario guardado correctamente.")

        except Exception as e:
            st.error(f"❌ Error al guardar el temario: {str(e)}")
else:
    st.info("🔼 Sube un archivo válido y escribe un nombre de oposición para comenzar.")
