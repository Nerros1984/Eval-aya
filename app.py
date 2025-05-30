import streamlit as st
import json
import os
from utils.test import generar_test_examen_completo

st.set_page_config(page_title="EvalúaYa - Simulador de Examen", layout="wide")
st.title("Generador de Test - Examen Oficial")

# --- Selección de oposición y carga de datos ---
nombre_oposicion = st.text_input("Nombre de la oposición", "Administrativo Ayuntamiento Sevilla")

ruta_temas_json = os.path.join("temarios_procesados", f"temas_{nombre_oposicion}.json")
if not os.path.exists(ruta_temas_json):
    st.warning("No se ha encontrado el archivo de temas. Asegúrate de haber procesado un temario antes.")
    st.stop()

with open(ruta_temas_json, "r", encoding="utf-8") as f:
    temas_dict = json.load(f)

# --- Botón para generar test ---
if st.button("🔹 Generar examen tipo oficial"):
    with st.spinner("Generando examen..."):
        ruta_json, ruta_pdf, preguntas = generar_test_examen_completo(nombre_oposicion, temas_dict)
        st.session_state["preguntas_generadas"] = preguntas
        st.session_state["ruta_pdf_generado"] = ruta_pdf
        st.success("Test generado correctamente.")

# --- Mostrar test generado ---
if "preguntas_generadas" in st.session_state:
    st.subheader("Realiza tu examen")
    respuestas_usuario = []

    for idx, pregunta in enumerate(st.session_state["preguntas_generadas"], 1):
        st.write(f"**{idx}. {pregunta['pregunta']}**")
        respuesta = st.radio(
            f"Selecciona tu respuesta ({idx})", 
            options=pregunta['opciones'],
            key=f"pregunta_{idx}"
        )
        respuestas_usuario.append(respuesta)

    if st.button("✅ Evaluar respuestas"):
        correctas = 0
        for i, pregunta in enumerate(st.session_state["preguntas_generadas"]):
            if respuestas_usuario[i] == pregunta["respuesta_correcta"]:
                correctas += 1
        st.success(f"Has acertado {correctas} de {len(respuestas_usuario)} preguntas.")

# --- Botón de descarga del PDF ---
if "ruta_pdf_generado" in st.session_state:
    ruta_pdf = st.session_state["ruta_pdf_generado"]
    if ruta_pdf and os.path.exists(ruta_pdf):
        with open(ruta_pdf, "rb") as f:
            st.download_button(
                label="📄 Descargar test en PDF",
                data=f,
                file_name=os.path.basename(ruta_pdf),
                mime="application/pdf"
            )
