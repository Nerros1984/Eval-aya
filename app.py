import streamlit as st
from datetime import datetime
import tempfile
import os
from utils.drive import subir_archivo_a_drive, CARPETA_TEMARIOS
from utils.sheets import registrar_en_sheet

st.set_page_config(page_title="EvalúaYa - Generador de Test por Temario", layout="centered")
st.title("\U0001f9e0 EvalúaYa - Generador de Test por Temario")

st.subheader("📄 Subir nuevo temario")
st.markdown("**📃 Sube un archivo DOCX o PDF con tu temario:**")

archivo_subido = st.file_uploader("Subir temario (DOCX o PDF)", type=["pdf", "docx"])
tipo_contenido = st.selectbox("🔍¡Qué contiene este archivo?", ["Temario completo", "Resumen", "Tema individual"])
nombre_oposicion = st.text_input("🌺 Nombre de la oposición (Ej: Administrativo Junta Andalucía)")
nombre_temario = st.text_input("📘 Nombre del documento de temario (Ej: Temario bloque I)")

if archivo_subido and nombre_oposicion.strip() and nombre_temario.strip():
    if st.button("✅ Guardar y registrar temario"):
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(archivo_subido.name)[-1]) as tmp:
                tmp.write(archivo_subido.read())
                tmp_path = tmp.name

            url_drive = subir_archivo_a_drive(tmp_path, nombre_oposicion, CARPETA_TEMARIOS)

            registrar_en_sheet(
                nombre_oposicion,
                tipo_contenido,
                nombre_temario,
                "",
                url_drive,
                datetime.now().strftime("%Y-%m-%d %H:%M")
            )

            st.success("✅ Temario subido y registrado correctamente.")
        except Exception as e:
            st.error(f"❌ Error al guardar el temario: {e}")
else:
    st.info("🔼 Sube un archivo válido y escribe un nombre de oposición y nombre de temario para comenzar.")
