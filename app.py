import streamlit as st
import json
import os
from utils.sheets import obtener_oposiciones_guardadas, obtener_temas_json_local
from utils.test import generar_test_desde_tema, generar_test_examen_completo

st.title("Generador de Tests")

# Mostrar oposiciones disponibles
opciones_oposiciones = obtener_oposiciones_guardadas()
nombre_oposicion = st.selectbox("Selecciona la oposición", opciones_oposiciones)

modo_test = st.radio("Tipo de test", ["Por tema", "Simulacro de examen oficial"])

if modo_test == "Por tema":
    temas_dict = obtener_temas_json_local(nombre_oposicion)
    temas_disponibles = list(temas_dict.keys())
    tema_seleccionado = st.selectbox("Selecciona un tema", temas_disponibles)
    num_preguntas = st.slider("Número de preguntas", 5, 20, 10)

    if st.button("Generar test por tema"):
        with st.spinner("Generando test..."):
            ruta_json, preguntas = generar_test_desde_tema(nombre_oposicion, tema_seleccionado, num_preguntas)

        st.success("Test generado correctamente")

        st.write("### Preguntas del test")
        for idx, pregunta in enumerate(preguntas, 1):
            st.write(f"**{idx}. {pregunta['pregunta']}**")
            for opcion in pregunta["opciones"]:
                st.write(f"- {opcion}")

        st.download_button("Descargar PDF", open(ruta_json.replace(".json", ".pdf"), "rb"), file_name=os.path.basename(ruta_json.replace(".json", ".pdf")))

else:
    if st.button("Generar simulacro oficial"):
        with st.spinner("Generando examen oficial..."):
            temas_dict = obtener_temas_json_local(nombre_oposicion)
            ruta_json, ruta_pdf, preguntas = generar_test_examen_completo(nombre_oposicion, temas_dict)

        st.success("Examen oficial generado")

        st.write("### Preguntas del test")
        respuestas_usuario = []
        for idx, pregunta in enumerate(preguntas, 1):
            st.write(f"**{idx}. {pregunta['pregunta']}**")
            respuesta = st.radio(f"Respuesta {idx}", pregunta["opciones"], key=idx)
            respuestas_usuario.append((respuesta, pregunta["respuesta_correcta"]))

        if st.button("Evaluar respuestas"):
            correctas = sum([1 for r, c in respuestas_usuario if r == c])
            st.info(f"Has acertado {correctas} de {len(preguntas)} preguntas. Nota: {round(correctas/len(preguntas)*10,2)}")

        st.download_button("Descargar PDF", open(ruta_pdf, "rb"), file_name=os.path.basename(ruta_pdf))
