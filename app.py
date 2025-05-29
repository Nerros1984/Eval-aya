import streamlit as st
from datetime import datetime
import tempfile
import os
from utils.drive import subir_archivo_a_drive, CARPETA_TEMARIOS
from utils.sheets import registrar_en_sheet

st.set_page_config(page_title="EvalúaYa - Generador de Test por Temario", layout="centered")

st.title("🧠 EvalúaYa - Generador de Test por Temario")

# Sección: Subir nuevo temario
st.subheader("📂 Subir nuevo temario")
st.markdown("📄 **Sube un archivo DOCX o PDF con tu temario:**")
archivo_subido = st.file_uploader("Subir temario (DOCX o PDF)", type=["pdf", "docx"])

tipo_contenido = st.selectbox("🔎¿Qué contiene este archivo?", ["Temario completo", "Resumen", "Tema individual"])
nombre_oposicion = st.text_input("📜 Nombre de la oposición (Ej: Administrativo Junta Andalucía)")

if archivo_subido and nombre_oposicion.strip():
    if st.button("✅ Guardar y registrar temario"):
        try:
            # Guardar archivo temporal
            tmp_path = os.path.join(tempfile.gettempdir(), archivo_subido.name)
            with open(tmp_path, "wb") as f:
                f.write(archivo_subido.getbuffer())

            # Subir a Drive
            url_drive = subir_archivo_a_drive(tmp_path, nombre_oposicion, CARPETA_TEMARIOS)

            # Registrar en hoja de cálculo
            registrar_en_sheet(
                nombre_oposicion,
                tipo_contenido,
                url_drive,
                "COMPLETO",  # Campo tema
                url_drive,
                datetime.now().strftime("%Y-%m-%d %H:%M")
            )

            st.success("✅ Temario subido y registrado correctamente.")

        except Exception as e:
            st.error(f"❌ Error al guardar el temario: {e}")
else:
    st.info("🔼 Sube un archivo válido y escribe un nombre de oposición para comenzar.")
