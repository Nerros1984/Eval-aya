import streamlit as st
import os
import json
import docx2txt
from utils.drive import subir_archivo_a_drive, descargar_archivo_de_drive, CARPETA_TEMAS_JSON
from utils.sheets import guardar_en_sheet, obtener_oposiciones_guardadas
from utils.test import generar_test_desde_tema, generar_test_examen_completo
from utils.temas import extraer_temas_de_texto, guardar_temas_json, cargar_temas_desde_json_local

st.set_page_config(page_title="Generador de Test por Temario", layout="centered")
st.title("📘 EvaluáYa - Generador de Test de Oposiciones")

modo = st.radio("", ["📄 Subir nuevo temario", "🌟 Usar oposición guardada"])

if modo == "📄 Subir nuevo temario":
    st.header("📄 Subida de Temario")
    st.subheader("📄 Sube un archivo DOCX o PDF con tu temario:")
    archivo_temario = st.file_uploader("Subir temario (DOCX o PDF)", type=["pdf", "docx"])

    tipo_contenido = st.selectbox("🔍¿Qué contiene este archivo?", ["Temario completo", "Temario por temas"])
    nombre_oposicion = st.text_input("🌺 Nombre de la oposición (Ej: Administrativo Junta Andalucía)")
    nombre_documento = st.text_input("📝 Nombre del documento de temario (Ej: Temario bloque I)")

    if archivo_temario and nombre_oposicion:
        with open("/tmp/temporal.docx", "wb") as f:
            f.write(archivo_temario.read())

        enlace_drive = subir_archivo_a_drive("/tmp/temporal.docx", nombre_oposicion)
        st.success("✅ Temario subido y registrado correctamente.")

        # Extraer temas y guardar JSON
        lista_temas = extraer_temas_de_texto("/tmp/temporal.docx")
        if lista_temas:
            enlace_json = guardar_temas_json(lista_temas, nombre_oposicion)

        guardar_en_sheet(nombre_oposicion, tipo_contenido, nombre_documento, enlace_drive)

elif modo == "🌟 Usar oposición guardada":
    st.header("📖 Usar oposición ya registrada")

    lista_opos = obtener_oposiciones_guardadas()
    oposicion = st.selectbox("Selecciona una oposición:", lista_opos)
    tipo_test = st.selectbox("Tipo de test", ["Simulacro examen oficial", "Test por temas"])

    if tipo_test == "Test por temas":
        nombre_normalizado = oposicion.strip().lower().replace(" ", "_")
        nombre_json = f"temas_{nombre_normalizado}.json"
        path_local = f"/tmp/{nombre_json}"

        # Descargar si no está localmente
        if not os.path.exists(path_local):
            descargar_archivo_de_drive(nombre_json, CARPETA_TEMAS_JSON, path_local)

        if os.path.exists(path_local):
            temas_dict = cargar_temas_desde_json_local(path_local)
            tema_seleccionado = st.selectbox("Selecciona un tema:", list(temas_dict.keys()))
            num_preguntas = st.slider("Número de preguntas", 5, 50, 10)

            if st.button("Generar test"):
                test = generar_test_desde_tema(temas_dict[tema_seleccionado], num_preguntas)
                st.success("✅ Test generado correctamente.")
                st.write(test)
        else:
            st.error("❌ El archivo JSON de temas no está disponible localmente.")

    elif tipo_test == "Simulacro examen oficial":
        if st.button("Generar test"):
            test = generar_test_examen_completo(oposicion)
            st.success("✅ Test generado correctamente.")
            st.write(test)
