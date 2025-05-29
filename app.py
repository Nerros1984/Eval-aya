import os
import re
import unicodedata
import streamlit as st
from datetime import datetime
from utils.drive import subir_archivo_a_drive, CARPETA_TEMARIOS
from utils.sheets import registrar_en_sheet, obtener_oposiciones_guardadas
from utils.test import generar_test_con_criterio_real, obtener_criterio_test

# Configuración de la interfaz
st.set_page_config(page_title="EvalúaYa - Generador de Test por Temario")
st.markdown("""
    <style>
    .stButton>button {
        background-color: #3ECF8E;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>🧠 EvalúaYa - Generador de Test por Temario</h1>", unsafe_allow_html=True)

modo = st.radio("", ["📄 Subir nuevo temario", "✨ Usar oposición guardada"], horizontal=True)

# ---------------------- MODO 1: SUBIR NUEVO TEMARIO ------------------------ #
if modo == "📄 Subir nuevo temario":
    st.subheader("📁 Subida de Temario")
    st.markdown("#### 📃 Sube un archivo DOCX o PDF con tu temario:")

    archivo = st.file_uploader("Subir temario (DOCX o PDF)", type=["pdf", "docx"], label_visibility="collapsed")
    tipo_contenido = st.selectbox("¿Qué contiene este archivo?", ["Temario completo", "Bloque de temas"])
    nombre_oposicion = st.text_input("📕 Nombre de la oposición (Ej: Administrativo Junta Andalucía)")
    nombre_temario = st.text_input("📘 Nombre del documento de temario (Ej: Temario bloque I)")

    if archivo and nombre_oposicion and nombre_temario:
        if st.button("✅ Guardar y registrar temario"):
            try:
                # Guardar archivo temporalmente
                tmp_path = os.path.join("/tmp", archivo.name)
                with open(tmp_path, "wb") as f:
                    f.write(archivo.read())

                # Subir a Drive y obtener enlace
                url_drive = subir_archivo_a_drive(tmp_path, nombre_oposicion, CARPETA_TEMARIOS)

                # Registrar en hoja
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
        st.info("🔷 Sube un archivo válido y escribe un nombre de oposición para comenzar.")

# ---------------------- MODO 2: USAR TEMARIO GUARDADO ------------------------ #
elif modo == "✨ Usar oposición guardada":
    st.subheader("🎯 Generar Test Oficial")

    try:
        oposiciones = obtener_oposiciones_guardadas()
        if not oposiciones:
            st.warning("⚠️ Aún no hay temarios registrados en la plataforma.")
        else:
            seleccion = st.selectbox("Selecciona una oposición:", list(oposiciones.keys()))
            criterio = obtener_criterio_test(seleccion)
            st.write(f"Criterio para {seleccion}: {criterio}")
            if st.button("✅ Generar test según examen real"):
                test = generar_test_con_criterio_real(seleccion, criterio)
                st.write(test)
    except Exception as e:
        st.error(f"❌ Error al cargar oposiciones: {e}")
