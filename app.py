import streamlit as st
import json
import datetime
import os

from utils.test import generar_test_desde_tema, generar_test_examen_completo
from utils.temas import extraer_temas_de_texto, guardar_temas_json, cargar_temas_desde_json_local
from utils.sheets import registrar_en_sheet, obtener_oposiciones_guardadas
from utils.drive import subir_archivo_a_drive

st.set_page_config(page_title="EvalúaYa - Generador de Test", layout="centered")
st.title("🧠 EvalúaYa - Generador Inteligente de Test")

modo = st.sidebar.selectbox("Selecciona el modo:", ["Subir temario", "Usar temario guardado"])

if modo == "Subir temario":
    st.header("📤 Subir nuevo temario")
    nombre_oposicion = st.text_input("Nombre de la oposición")
    nombre_temario = st.text_input("Nombre del documento")
    tipo_contenido = st.selectbox("Tipo de contenido", ["Temario completo", "Temario por temas"])
    archivo = st.file_uploader("Sube tu archivo (DOCX)", type=["docx"])

    if archivo and st.button("Subir temario"):
        with open("/tmp/temp.docx", "wb") as f:
            f.write(archivo.read())

        lista_temas = extraer_temas_de_texto("/tmp/temp.docx")
        st.subheader("Temas detectados:")
        for tema in lista_temas:
            st.markdown(f"- {tema.splitlines()[0]}")

        if st.button("Validar y guardar temario"):
            enlace_json = guardar_temas_json(lista_temas, nombre_oposicion)
            enlace_pdf = subir_archivo_a_drive("/tmp/temp.docx", nombre_oposicion, "temarios_pdf")
            fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            registrar_en_sheet(nombre_oposicion, nombre_temario, tipo_contenido, enlace_pdf, enlace_json, fecha)
            st.success("Temario registrado correctamente ✅")

elif modo == "Usar temario guardado":
    st.header("📚 Generar test desde temario existente")
    oposiciones = obtener_oposiciones_guardadas()
    nombre_oposicion = st.selectbox("Selecciona oposición", oposiciones)

    temas_json_path = st.text_input("Ruta al archivo JSON del temario")
    if temas_json_path:
        temas_dict = cargar_temas_desde_json_local(temas_json_path)
        temas = list(temas_dict.keys())
        tipo_test = st.radio("Tipo de test", ["Por tema", "Examen oficial completo"])

        if tipo_test == "Por tema":
            tema = st.selectbox("Selecciona un tema", temas)
            num_preguntas = st.slider("Número de preguntas", 5, 20, 10)

            if st.button("Generar test del tema"):
                ruta_json, preguntas = generar_test_desde_tema(nombre_oposicion, tema, num_preguntas)
                st.success("✅ Test generado correctamente")
                for i, preg in enumerate(preguntas, 1):
                    st.write(f"**{i}.** {preg['pregunta']}")
                    for op in preg['opciones']:
                        st.write(f"- {op}")

        else:
            if st.button("Generar test oficial completo"):
                ruta_json, ruta_pdf, preguntas_finales = generar_test_examen_completo(nombre_oposicion, temas_dict)
                st.success("✅ Test oficial generado")
                with open(ruta_pdf, "rb") as f:
                    st.download_button("📄 Descargar PDF del test", f, file_name=os.path.basename(ruta_pdf))
                st.subheader("Resumen del test")
                for i, preg in enumerate(preguntas_finales, 1):
                    st.write(f"**{i}.** {preg['pregunta']}")
                    for op in preg['opciones']:
                        st.write(f"- {op}")
