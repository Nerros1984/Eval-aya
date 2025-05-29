import streamlit as st
import os
from datetime import datetime
from utils.drive import subir_archivo_a_drive, CARPETA_TEMARIOS
from utils.sheets import registrar_en_sheet, obtener_oposiciones_guardadas
from oauth2client.service_account import ServiceAccountCredentials
import gspread

st.set_page_config(page_title="EvalúaYa - Generador de Test por Temario", layout="wide")
st.markdown("<h1 style='font-size: 40px;'>🧠 EvalúaYa - Generador de Test por Temario</h1>", unsafe_allow_html=True)

modo = st.radio("", ["📄 Subir nuevo temario", "✨ Usar oposición guardada"], horizontal=True)

if modo == "📄 Subir nuevo temario":
    st.subheader("📁 Subida de Temario")
    st.markdown("**📃 Sube un archivo DOCX o PDF con tu temario:**")

    archivo = st.file_uploader("Subir temario (DOCX o PDF)", type=["pdf", "docx"])
    tipo_contenido = st.selectbox("🔍 ¿Qué contiene este archivo?", ["Temario completo", "Tema individual"])
    nombre_oposicion = st.text_input("<span style='font-size: 14px;'>🌺 Nombre de la oposición (Ej: Administrativo Junta Andalucía)</span>", placeholder="Ej: Administrativo Ayuntamiento Sevilla", label_visibility="visible")
    nombre_temario = st.text_input("<span style='font-size: 14px;'>📂 Nombre del documento de temario (Ej: Temario bloque I)</span>", placeholder="Ej: Temario bloque I", label_visibility="visible")

    if archivo and nombre_oposicion:
        if st.button("✅ Guardar y registrar temario"):
            try:
                with open(archivo.name, "wb") as f:
                    f.write(archivo.getbuffer())
                tmp_path = archivo.name
                url_drive = subir_archivo_a_drive(tmp_path, nombre_oposicion, CARPETA_TEMARIOS)
                os.remove(tmp_path)

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
                st.error(f"❌ Error al guardar el temario: {str(e)}")
    else:
        st.info("📁 Sube un archivo válido y escribe un nombre de oposición para comenzar.")

elif modo == "✨ Usar oposición guardada":
    st.subheader("🎯 Generar Test Oficial")
    try:
        oposiciones = obtener_oposiciones_guardadas()
        if oposiciones:
            seleccion = st.selectbox("📌 Selecciona una oposición:", oposiciones)
            st.success(f"Has seleccionado: {seleccion}")
            # A partir de aquí puedes mostrar botones de generar test
        else:
            st.warning("⚠️ Aún no hay temarios registrados en la plataforma.")
    except Exception as e:
        st.error(f"❌ Error al cargar oposiciones: {str(e)}")
