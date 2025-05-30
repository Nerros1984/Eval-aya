import os
import json
import re
import tempfile
import streamlit as st
import docx2txt
from datetime import datetime
from utils.drive import subir_archivo_a_drive, descargar_archivo_de_drive, CARPETA_TEMARIOS, CARPETA_TEMAS_JSON
from utils.sheets import registrar_en_sheet, obtener_oposiciones_guardadas
from utils.temas import extraer_temas_de_texto, guardar_temas_json, cargar_temas_desde_json_local
from utils.test import generar_test_desde_tema, generar_test_examen_completo
from pydrive.files import ApiRequestError

st.set_page_config(page_title="EvalúaYa - Generador de Test", page_icon="📘")
st.title("📘 EvalúaYa - Generador de Test de Oposiciones")

modo = st.radio("", ["📂 Subir nuevo temario", "✨ Usar oposición guardada"], horizontal=True)

if modo == "📂 Subir nuevo temario":
    st.subheader("📂 Subida de Temario")
    st.markdown("📄 Sube un archivo DOCX o PDF con tu temario:")
    archivo_temario = st.file_uploader("Subir temario (DOCX o PDF)", type=["pdf", "docx"])

    tipo_contenido = st.selectbox("🤓 ¿Qué contiene este archivo?", ["Temario completo", "Temario por temas"])
    nombre_oposicion = st.text_input("🌺 Nombre de la oposición (Ej: Administrativo Junta Andalucía)")
    nombre_temario = st.text_input("📜 Nombre del documento de temario (Ej: Temario bloque I)")

    if st.button("📤 Confirmar y registrar temario"):
        if archivo_temario and nombre_oposicion and nombre_temario:
            with st.spinner("Registrando temario..."):
                try:
                    extension = archivo_temario.name.split(".")[-1].lower()
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{extension}") as tmp:
                        tmp.write(archivo_temario.read())
                        tmp_path = tmp.name

                    enlace_drive = subir_archivo_a_drive(tmp_path, nombre_oposicion, CARPETA_TEMARIOS)
                    temas_extraidos = extraer_temas_de_texto(tmp_path)
                    enlace_json = guardar_temas_json(temas_extraidos, nombre_oposicion)

                    registrar_en_sheet(
                        nombre_oposicion,
                        nombre_temario,
                        tipo_contenido,
                        enlace_drive,
                        enlace_json,
                        datetime.now().strftime("%Y-%m-%d %H:%M")
                    )

                    st.success("✅ Temario subido, registrado y procesado correctamente.")
                except ApiRequestError:
                    st.warning("⚠️ Ya existe un temario con ese contenido. Puedes verlo en la sección '✨ Usar oposición guardada'.")
        else:
            st.error("❌ Por favor, completa todos los campos y sube un archivo válido.")

elif modo == "✨ Usar oposición guardada":
    st.subheader("📚 Usar oposición ya registrada")

    oposiciones = obtener_oposiciones_guardadas()

    if not oposiciones:
        st.info("ℹ️ Aún no hay temarios registrados. Sube uno desde la opción anterior.")
    else:
        opcion = st.selectbox("Selecciona una oposición:", oposiciones)
        tipo_test = st.selectbox("Tipo de test", ["Test por temas", "Simulacro examen oficial"])

        nombre_archivo = f"temas_{opcion.strip().lower().replace(' ', '_')}.json"
        path_local = f"/tmp/{nombre_archivo}"
        json_ok = descargar_archivo_de_drive(nombre_archivo, CARPETA_TEMAS_JSON, path_local)

        if not json_ok:
            st.error("❌ El archivo JSON de temas no está disponible localmente.")
        else:
            temas_dict = cargar_temas_desde_json_local(path_local)

            if tipo_test == "Test por temas":
                tema_elegido = st.selectbox("Selecciona un tema", list(temas_dict.keys()))
                num_preguntas = st.slider("Número de preguntas", 5, 50, 10)

                if st.button("📝 Generar test"):
                    test = generar_test_desde_tema(temas_dict[tema_elegido], num_preguntas)
                    st.write(test)

            elif tipo_test == "Simulacro examen oficial":
                if st.button("📝 Generar test"):
                    test = generar_test_examen_completo(opcion)
                    st.write(test)
