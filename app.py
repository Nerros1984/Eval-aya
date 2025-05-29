import streamlit as st
from datetime import datetime
import json
import os
from utils.drive import subir_archivo_a_drive, CARPETA_TEMARIOS
from utils.sheets import registrar_en_sheet, obtener_oposiciones_guardadas

st.set_page_config(page_title="🧠 EvalúaYa - Generador de Test por Temario", layout="centered")
st.title("\U0001f9e0 EvalúaYa - Generador de Test por Temario")

modo = st.radio("", ["📁 Subir nuevo temario", "✨ Usar oposición guardada"], horizontal=True)

# ------------------------
# SUBIR NUEVO TEMARIO
# ------------------------
if modo == "📁 Subir nuevo temario":
    st.subheader("\ud83d\udcc4 Sube un archivo DOCX o PDF con tu temario:")

    archivo = st.file_uploader("Subir temario (DOCX o PDF)", type=["pdf", "docx"])
    tipo_contenido = st.selectbox("🔍 ¿Qué contiene este archivo?", ["Temario completo", "Resumen", "Tema individual"])
    nombre_oposicion = st.text_input("🌺 Nombre de la oposición (Ej: Administrativo Junta Andalucía)")
    nombre_temario = st.text_input("\ud83d\udcc2 Nombre del documento de temario (Ej: Temario bloque I)")

    if archivo and nombre_oposicion.strip() and nombre_temario.strip():
        if st.button("✅ Guardar y registrar temario"):
            try:
                with open(f"temp_{archivo.name}", "wb") as f:
                    f.write(archivo.read())
                tmp_path = f.name

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
        st.info("\ud83d\udcc4 Sube un archivo válido y escribe un nombre de oposición para comenzar.")

# ------------------------
# USAR TEMARIO GUARDADO
# ------------------------
elif modo == "✨ Usar oposición guardada":
    st.subheader("\ud83c\udfaf Generar Test Oficial")

    temarios = obtener_oposiciones_guardadas()
    if not temarios:
        st.warning("\u26a0\ufe0f Aún no hay temarios registrados en la plataforma.")
    else:
        opciones = list({t[0] for t in temarios})
        seleccion = st.selectbox("Selecciona una oposición:", opciones)

        if seleccion:
            st.success(f"Temario disponible para: {seleccion}")
            # AQUI debería salir opción para generar test (por tema o completo)
