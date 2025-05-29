import streamlit as st
import os
import tempfile
from datetime import datetime
from utils.sheets import registrar_en_sheet, obtener_oposiciones_guardadas
from utils.drive import subir_archivo_a_drive, CARPETA_TEMARIOS

st.set_page_config(page_title="EvalúaYa - Generador de Test por Temario", layout="centered")
st.title("\U0001F9E0 EvalúaYa - Generador de Test por Temario")

modo = st.radio("", ["Subir nuevo temario", "Usar oposición guardada"], horizontal=True)

if modo == "Subir nuevo temario":
    st.markdown("### 📄 Subir nuevo temario")
    st.markdown("**📄 Sube un archivo DOCX o PDF con tu temario:**")

    archivo_subido = st.file_uploader("Subir temario (DOCX o PDF)", type=["pdf", "docx"])
    tipo_contenido = st.selectbox("\ud83d\udd0d ¿Qué contiene este archivo?", ["Temario completo", "Tema individual"])
    nombre_oposicion = st.text_input("\ud83c\udf3a Nombre de la oposición (Ej: Administrativo Junta Andalucía)")
    nombre_temario = st.text_input("\ud83d\udcc4 Nombre del documento de temario (Ej: Temario bloque I)")

    if archivo_subido and nombre_oposicion.strip() and nombre_temario.strip():
        if st.button("\u2705 Guardar y registrar temario"):
            try:
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    tmp.write(archivo_subido.read())
                    tmp_path = tmp.name

                url_drive = subir_archivo_a_drive(tmp_path, nombre_oposicion, CARPETA_TEMARIOS)

                registrar_en_sheet(
                    nombre_oposicion,
                    tipo_contenido,
                    nombre_temario,
                    "",  # tema vacío para temario completo
                    url_drive,
                    datetime.now().strftime("%Y-%m-%d %H:%M")
                )

                st.success("\u2705 Temario subido y registrado correctamente.")

            except Exception as e:
                st.error(f"\u274C Error al guardar el temario: {e}")

    else:
        st.info("\u26A0\ufe0f Sube un archivo válido y escribe un nombre de oposición para comenzar.")

elif modo == "Usar oposición guardada":
    st.markdown("### 🎯 Generar Test Oficial")

    oposiciones = obtener_oposiciones_guardadas()

    if not oposiciones:
        st.info("\u26a0️ Aún no hay temarios registrados en la plataforma.")
    else:
        seleccion = st.selectbox("Selecciona una oposición registrada:", oposiciones)
        st.success(f"\u2705 Puedes generar test para: {seleccion}")

        # Aquí debería ir la lógica para mostrar temas disponibles y botones para generar test
        st.markdown("(Aquí iría el selector de temas o generador directo de test)")
