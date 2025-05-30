import streamlit as st
from test import generar_test_examen
import json

st.title("📘 EvaluáYa - Generador de Test de Oposiciones")
modo = st.radio("", ["📝 Subir nuevo temario", "✨ Usar oposición guardada"])

if modo == "✨ Usar oposición guardada":
    oposiciones = ["Administrativo Ayuntamiento Sevilla"]
    opcion = st.selectbox("Selecciona una oposición:", oposiciones)
    tipo = st.selectbox("Tipo de test", ["Simulacro examen oficial"])

    if st.button("📅 Generar test"):
        with st.spinner("Generando test..."):
            # Simulación local de temas
            temas_dict = {
                "tema_01": [{"pregunta": f"Pregunta {i+1} del tema 01", "opciones": ["A", "B", "C", "D"], "respuesta_correcta": "A"} for i in range(10)],
                "tema_02": [{"pregunta": f"Pregunta {i+1} del tema 02", "opciones": ["A", "B", "C", "D"], "respuesta_correcta": "B"} for i in range(10)],
                "tema_03": [{"pregunta": f"Pregunta {i+1} del tema 03", "opciones": ["A", "B", "C", "D"], "respuesta_correcta": "C"} for i in range(10)],
            }
            ruta_pdf, preguntas = generar_test_examen(opcion, temas_dict)
            st.success("Test generado correctamente.")
            with open(ruta_pdf, "rb") as f:
                st.download_button("📎 Descargar test PDF", f, file_name=ruta_pdf.split("/")[-1])

            st.markdown("---")
            st.subheader("📋 Realiza el test aquí mismo")
            respuestas_usuario = []
            for idx, preg in enumerate(preguntas, 1):
                respuesta = st.radio(f"{idx}. {preg['pregunta']}", preg['opciones'], key=idx)
                respuestas_usuario.append(respuesta)

            if st.button("✅ Evaluar test"):
                aciertos = sum([resp == preg['respuesta_correcta'] for resp, preg in zip(respuestas_usuario, preguntas)])
                st.success(f"Has acertado {aciertos} de {len(preguntas)} preguntas.")
