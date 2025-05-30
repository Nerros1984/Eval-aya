import streamlit as st
import json
import os
from utils.drive import obtener_oposiciones_con_tema_json, descargar_archivo_de_drive
from utils.test import generar_test_examen_completo

st.set_page_config(page_title="EvalúaYa - Generador de Test", page_icon="🔮", layout="centered")

st.title("\U0001f9ea EvalúaYa - Generador Inteligente de Test")

modo = st.selectbox("Selecciona el modo:", ["Usar temario guardado"], index=0)

if modo == "Usar temario guardado":
    st.subheader("\U0001f4da Generar test desde temario existente")

    oposiciones = obtener_oposiciones_con_tema_json()
    if not oposiciones:
        st.warning("No hay temarios disponibles en Drive.")
    else:
        seleccion = st.selectbox("Selecciona oposición", oposiciones)

        nombre_archivo = f"temas_{seleccion.strip().lower().replace(' ', '_')}.json"
        path_local = os.path.join("/tmp", nombre_archivo)

        if descargar_archivo_de_drive(nombre_archivo, "1popTRkA-EjI8_4WqKPjkldWVpCYsJJjm", path_local):
            st.text_input("Ruta al archivo JSON del temario", path_local)

            if st.button("\ud83d\uddd3\ufe0f Generar test"):
                with open(path_local, 'r', encoding='utf-8') as f:
                    temas_dict = json.load(f)
                try:
                    ruta_json, ruta_pdf, preguntas = generar_test_examen_completo(seleccion, temas_dict)
                    st.success("Test generado correctamente.")

                    with open(ruta_pdf, "rb") as f:
                        st.download_button("\ud83d\udd17 Descargar test PDF", f, file_name=os.path.basename(ruta_pdf))

                    st.subheader("\ud83d\udd39 Vista previa del test")
                    for idx, preg in enumerate(preguntas, 1):
                        st.markdown(f"**{idx}. {preg['pregunta']}**")
                        for op in preg['opciones']:
                            st.markdown(f"- {op}")
                except Exception as e:
                    st.error(f"Error generando test: {e}")
        else:
            st.warning("No se pudo encontrar o descargar el archivo JSON del temario.")
