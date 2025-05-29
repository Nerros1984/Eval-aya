from datetime import datetime
import streamlit as st
import json
import tempfile

from utils.drive import cargar_preguntas_desde_drive, exportar_test_json
from utils.test import generar_test_con_criterio_real, obtener_criterio_test, descargar_pdf_test

st.set_page_config(page_title="EvalúaYa - Generador de Test por Temario", layout="centered")
st.title("🧠 EvalúaYa - Generador de Test por Temario")

# 1. Selector de oposición (temario)
oposiciones_disponibles = cargar_preguntas_desde_drive(lista=True)
oposicion_seleccionada = st.selectbox("Selecciona una oposición:", oposiciones_disponibles)

# 2. Cargar criterio de test para esa oposición
criterio = obtener_criterio_test(oposicion_seleccionada)

if criterio:
    st.info(f"Criterio de test para {oposicion_seleccionada}: {criterio['descripcion']}")
else:
    st.warning("No hay criterio definido aún para esta oposición. Puedes usar distribución libre.")

# 3. Botón para generar test
if st.button("🎯 Generar Test según examen real"):
    with st.spinner("Generando test según criterio oficial..."):
        preguntas = generar_test_con_criterio_real(oposicion_seleccionada)

    if preguntas:
        st.success("✅ Test generado con éxito")

        respuestas_usuario = {}
        for i, pregunta in enumerate(preguntas):
            st.markdown(f"### {i + 1}. {pregunta['pregunta']}")
            seleccion = st.radio(
                label="",
                options=pregunta["opciones"],
                key=f"pregunta_{i}"
            )
            respuestas_usuario[i] = seleccion

        # Evaluar resultado
        if st.button("📊 Evaluar test"):
            aciertos = 0
            for i, pregunta in enumerate(preguntas):
                correcta = pregunta['opciones'][ord(pregunta['respuesta']) - ord('A')]
                if respuestas_usuario[i] == correcta:
                    st.markdown(f"✅ Pregunta {i+1}: Correcta")
                    aciertos += 1
                else:
                    st.markdown(f"❌ Pregunta {i+1}: Incorrecta")
                    st.markdown(f"Respuesta correcta: {correcta}")
            st.info(f"Puntuación final: {aciertos}/{len(preguntas)}")

        # Exportar a JSON
        test_json = exportar_test_json(preguntas)
        st.download_button(
            label="📥 Descargar test en JSON",
            data=test_json,
            file_name="test_generado.json",
            mime="application/json"
        )

        # Exportar a PDF
        pdf_path = descargar_pdf_test(preguntas)
        with open(pdf_path, "rb") as f:
            st.download_button(
                label="📄 Descargar test en PDF",
                data=f,
                file_name="test_generado.pdf",
                mime="application/pdf"
            )
