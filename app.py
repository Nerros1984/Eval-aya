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
from utils.sheets import registrar_en_sheet, obtener_oposiciones_guardadas

st.set_page_config(page_title="EvalúaYa - Generador de Test por Temario", layout="centered")

st.title("🧠 EvalúaYa - Generador de Test por Temario")

# Elección de flujo
flujo = st.radio("", ["📂 Subir nuevo temario", "✨ Usar oposición guardada"])

CARPETA_TEMARIOS_ID = "1x08mfjA7JhnVk9OxvXJD54MLmtdZDCJb"

if flujo == "📂 Subir nuevo temario":
    st.subheader("📄 Subida de Temario")
    st.markdown("**📁 Sube un archivo DOCX o PDF con tu temario:**")

    archivo_subido = st.file_uploader("Subir temario (DOCX o PDF)", type=["pdf", "docx"])
    tipo_contenido = st.selectbox("🔎 ¿Qué contiene este archivo?", ["Temario completo", "Resumen", "Tema individual"])
    nombre_oposicion = st.text_input("📜 Nombre de la oposición (Ej: Administrativo Junta Andalucía)")

    if st.button("✅ Guardar y registrar temario"):
        if archivo_subido and nombre_oposicion.strip():
            with st.spinner("📤 Subiendo archivo y registrando..."):
                tmp_path = f"/tmp/{archivo_subido.name}"
                with open(tmp_path, "wb") as f:
                    f.write(archivo_subido.getbuffer())

                url_drive = subir_archivo_a_drive(tmp_path, nombre_oposicion, CARPETA_TEMARIOS_ID)

                registrar_en_sheet(
                    nombre_oposicion,
                    tipo_contenido,
                    url_drive,
                    "",
                    datetime.now().strftime("%Y-%m-%d %H:%M")
                )

            st.success("✅ Temario registrado correctamente.")
        else:
            st.warning("⚠️ Debes subir un archivo y escribir un nombre de oposición para continuar.")

elif flujo == "✨ Usar oposición guardada":
    st.subheader("🎯 Generar Test Oficial")
    oposiciones = obtener_oposiciones_guardadas()

    if not oposiciones:
        st.info("ℹ️ Aún no hay oposiciones registradas. Sube un temario primero.")
    else:
        seleccion = st.selectbox("Selecciona una oposición:", list(oposiciones.keys()))
        st.markdown(f"📝 Has seleccionado: **{seleccion}**")

        st.button("🧪 Generar Test según examen real")
