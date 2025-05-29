import streamlit as st
from datetime import datetime
import os
import tempfile
import json
from utils.drive import subir_archivo_a_drive, CARPETA_TEMARIOS, CARPETA_TEMAS_JSON
from utils.sheets import registrar_en_sheet, obtener_oposiciones_guardadas
from utils.temas import extraer_temas_de_texto, guardar_temas_json
from utils.doc_parser import leer_contenido_docx

st.set_page_config(page_title="EvalúaYa - Generador de Test por Temario", layout="centered")
st.title("🧠 EvalúaYa - Generador de Test por Temario")

modo = st.radio("", ["📁 Subir nuevo temario", "✨ Usar oposición guardada"], horizontal=True)

if modo == "📁 Subir nuevo temario":
    st.subheader("📂 Subida de Temario")

    archivo_subido = st.file_uploader("📄 Sube un archivo DOCX o PDF con tu temario:", type=["pdf", "docx"])
    tipo_contenido = st.selectbox("🔍 ¿Qué contiene este archivo?", ["Temario completo", "Resumen", "Tema individual"])
    nombre_oposicion = st.text_input("🌸 Nombre de la oposición (Ej: Administrativo Junta Andalucía)")
    nombre_temario = st.text_input("📘 Nombre del documento de temario (Ej: Temario bloque I)")

    if archivo_subido and nombre_oposicion.strip() and nombre_temario.strip():
        if st.button("✅ Guardar y registrar temario"):
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(archivo_subido.name)[1]) as tmp:
                tmp.write(archivo_subido.read())
                tmp_path = tmp.name

            try:
                # Subir temario a Drive
                url_drive = subir_archivo_a_drive(tmp_path, nombre_oposicion, CARPETA_TEMARIOS)

                # Leer contenido y generar temas JSON
                contenido = leer_contenido_docx(tmp_path)
                temas = extraer_temas_de_texto(contenido)
                json_path = guardar_temas_json(nombre_oposicion, nombre_temario, temas)

                # Subir JSON a carpeta de temas
                url_json = subir_archivo_a_drive(json_path, nombre_oposicion, CARPETA_TEMAS_JSON)

                # Registrar en Google Sheets
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
        st.info("🔹 Sube un archivo válido y escribe un nombre de oposición para comenzar.")

elif modo == "✨ Usar oposición guardada":
    st.subheader("🎯 Generar Test Oficial")
    oposiciones = obtener_oposiciones_guardadas()

    if oposiciones:
        seleccion = st.selectbox("Selecciona una oposición:", list(oposiciones.keys()))
        info = oposiciones[seleccion]
        st.info(f"Criterio de test: {info['tipo']} \nDocumento: {info['temario']}")

        if st.button("✅ Generar Test según examen real"):
            st.success("Test generado según criterios oficiales (a implementar).")

        st.markdown("---")
        st.subheader("📃 Generar Test por Tema")
        temas = info.get("temas", [])
        if temas:
            tema_sel = st.selectbox("Selecciona un tema:", temas)
            if st.button("🎓 Generar Test de este tema"):
                st.success("Test generado del tema seleccionado (a implementar).")
        else:
            st.warning("🚧 Este temario no tiene temas registrados. Suba un temario completo para generarlos.")
    else:
        st.warning("🚫 Aún no hay temarios registrados en la hoja de cálculo.")
