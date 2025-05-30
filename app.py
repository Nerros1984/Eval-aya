import streamlit as st
import os
import json
import re
import datetime
import docx2txt

from utils.drive import subir_archivo_a_drive, descargar_archivo_de_drive, CARPETA_TEMARIOS, CARPETA_TEMAS_JSON
from utils.sheets import registrar_en_sheet, obtener_oposiciones_guardadas
from utils.test import generar_test_desde_tema, generar_test_examen_completo
from utils.temas import extraer_temas_de_texto, guardar_temas_json, cargar_temas_desde_json_local

st.set_page_config(page_title="Generador de Test EvalúaYa", page_icon="📘")
st.title("📘 EvaluáYa - Generador de Test de Oposiciones")

modo = st.radio("", ["📂 Subir nuevo temario", "✨ Usar oposición guardada"])

if modo == "📂 Subir nuevo temario":
    st.subheader("📂 Subida de Temario")
    archivo_temario = st.file_uploader("📄 Sube un archivo DOCX o PDF con tu temario:", type=["pdf", "docx"])

    tipo_contenido = st.selectbox("🧐 ¿Qué contiene este archivo?", ["Temario completo", "Temario por temas"])
    nombre_oposicion = st.text_input("🌺 Nombre de la oposición (Ej: Administrativo Junta Andalucía)")
    nombre_temario = st.text_input("📝 Nombre del documento de temario (Ej: Temario bloque I)")

    if archivo_temario and nombre_oposicion:
        with open("/tmp/temporal.docx", "wb") as f:
            f.write(archivo_temario.read())

        enlace_drive = subir_archivo_a_drive("/tmp/temporal.docx", nombre_oposicion, CARPETA_TEMARIOS)

        try:
            temas_extraidos = extraer_temas_de_texto("/tmp/temporal.docx")
            enlace_json = guardar_temas_json(temas_extraidos, nombre_oposicion)
        except Exception as e:
            st.error(f"❌ Error al extraer o guardar temas: {e}")
            enlace_json = ""

        fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        registrar_en_sheet(nombre_oposicion, nombre_temario, tipo_contenido, enlace_drive, enlace_json, fecha_actual)
        st.success("✅ Temario subido, registrado y procesado correctamente.")

else:
    st.subheader("📚 Usar oposición ya registrada")
    oposiciones = obtener_oposiciones_guardadas()
    if oposiciones:
        oposicion = st.selectbox("Selecciona una oposición:", oposiciones)
        tipo_test = st.selectbox("Tipo de test", ["Test por temas", "Simulacro examen oficial"])

        nombre_normalizado = oposicion.strip().lower().replace(" ", "_")
        nombre_json = f"temas_{nombre_normalizado}.json"
        ruta_local = f"/tmp/{nombre_json}"

        if not os.path.exists(ruta_local):
            descargado = descargar_archivo_de_drive(nombre_json, CARPETA_TEMAS_JSON, ruta_local)
            if descargado is None:
                st.error("❌ El archivo JSON de temas no está disponible localmente.")

        if os.path.exists(ruta_local):
            temas_dict = cargar_temas_desde_json_local(ruta_local)

            if tipo_test == "Test por temas":
                tema = st.selectbox("Selecciona un tema", list(temas_dict.keys()))
                num_pregs = st.slider("Número de preguntas", 5, 50, 10)
                if st.button("📝 Generar test"):
                    test = generar_test_desde_tema(temas_dict[tema], num_pregs)
                    st.write(test)
            else:
                if st.button("📝 Generar test"):
                    test = generar_test_examen_completo(oposicion)
                    st.write(test)
    else:
        st.warning("⚠️ Aún no hay oposiciones registradas.")
