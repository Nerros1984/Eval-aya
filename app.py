# app.py

import streamlit as st
from core.test_generator import TestGenerator
from core.test_manager import (
    guardar_test_json,
    generar_y_guardar_pdf,
    registrar_test_en_drive,
    registrar_metadata_en_sheets
)
from utils.sheets import obtener_oposiciones_y_temas  # Nueva función para el desplegable

st.set_page_config(page_title="EvalúaYa", layout="centered")
st.title("📝 EvalúaYa – Generador de Tests de Oposición")

st.markdown("---")
st.header("1. Selecciona oposición y tema")

oposiciones_dict = obtener_oposiciones_y_temas()

oposicion_seleccionada = st.selectbox("Oposición", list(oposiciones_dict.keys()))
tema_seleccionado = st.selectbox("Tema disponible", oposiciones_dict[oposicion_seleccionada])

st.markdown("---")
st.header("2. Subir temario completo")
nombre_oposicion = st.text_input("Nombre de la oposición (manual si no está en la lista)")
temario_texto = st.text_area("Pega aquí el temario completo", height=300)

if st.button("Generar test oficial"):
    if not nombre_oposicion or not temario_texto:
        st.error("Debes completar el nombre de la oposición y pegar el temario.")
    else:
        with st.spinner("Generando test..."):
            try:
                tg = TestGenerator(nombre_oposicion, temario_texto)
                test_dict = tg.generar_test_oficial()

                ruta_json = guardar_test_json(test_dict)
                ruta_pdf = generar_y_guardar_pdf(test_dict)
                enlace_pdf = registrar_test_en_drive(test_dict, ruta_pdf)
                registrar_metadata_en_sheets(test_dict, enlace_pdf)

                st.success("✅ Test generado con "+str(len(test_dict["preguntas"]))+" preguntas.")
                st.markdown(f"[Descargar PDF]({enlace_pdf})")

            except Exception as e:
                st.error(f"Error: {str(e)}")
