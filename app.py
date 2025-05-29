import streamlit as st
from datetime import datetime
import tempfile
import os

from utils.sheets import registrar_en_sheet, obtener_oposiciones_guardadas
from utils.drive import subir_archivo_a_drive, CARPETA_TEMARIOS

st.set_page_config(page_title="EvalúaYa - Generador de Test por Temario", layout="centered")
st.title("🧠 EvalúaYa - Generador de Test por Temario")

st.markdown("### 📃 Sube un archivo DOCX o PDF con tu temario:")
archivo_subido = st.file_uploader("Subir temario (DOCX o PDF)", type=["pdf", "docx"])

tipo_contenido = st.selectbox("\ud83d\udd0d ¿Qué contiene este archivo?", ["Temario completo", "Resumen", "Tema individual"])
nombre_oposicion = st.text_input("\ud83c\udfdb Nombre de la oposición (Ej: Administrativo Junta Andalucía)")

if archivo_subido and nombre_oposicion.strip():
    if st.button("✅ Guardar y registrar temario"):
        try:
            # Guardar archivo temporalmente
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(archivo_subido.name)[-1]) as tmp_file:
                tmp_file.write(archivo_subido.read())
                tmp_path = tmp_file.name

            # Subir a Drive y registrar
            url_drive = subir_archivo_a_drive(tmp_path, nombre_oposicion, CARPETA_TEMARIOS)

            registrar_en_sheet(
                nombre_oposicion,
                tipo_contenido,
                archivo_subido.name,
                "",  # tema (vacío por ahora)
                url_drive,
                datetime.now().strftime("%Y-%m-%d %H:%M")
            )

            st.success("✅ Temario guardado correctamente.")
        except Exception as e:
            st.error(f"❌ Error al guardar el temario: {e}")
else:
    st.info("\u2b06\ufe0f Sube un archivo válido y escribe un nombre de oposición para comenzar.")
