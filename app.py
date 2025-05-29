from datetime import datetime
import streamlit as st
import json
import tempfile
from utils.drive import cargar_preguntas_desde_drive, exportar_test_json, subir_archivo_a_drive
from utils.sheets import registrar_en_sheet
from utils_test import generar_test_con_criterio_real, obtener_criterio_test, descargar_pdf_test

st.set_page_config(page_title="EvalúaYa - Generador de Test por Temario", layout="centered")
st.title("🧠 EvalúaYa - Generador de Test por Temario")

# === 1. SUBIR TEMARIO ===
st.subheader("📥 Subida de Temario")
archivo_subido = st.file_uploader("Selecciona un archivo DOCX o PDF:", type=["docx", "pdf"])
nombre_temario = st.text_input("📝 Nombre del temario")
oposicion = st.text_input("🏛️ Nombre de la oposición", placeholder="Ej: Auxiliar Administrativo – Ayuntamiento de Sevilla")
tipo = st.selectbox("🔢 Tipo de contenido", ["Temario completo", "Resumen", "Tema individual"])

if st.button("✅ Subir y registrar temario"):
    if archivo_subido and nombre_temario and oposicion:
        with st.spinner("Subiendo archivo a Google Drive..."):
            ruta_temp = f"/tmp/{archivo_subido.name}"
            with open(ruta_temp, "wb") as f:
                f.write(archivo_subido.read())
            url_archivo = subir_archivo_a_drive(ruta_temp, oposicion)

        registrar_en_sheet(
            nombre_temario,
            tipo,
            url_archivo,
            "",
            datetime.now().strftime("%Y-%m-%d %H:%M")
        )
        st.success("📂 Archivo subido y registrado correctamente.")
    else:
        st.warning("Debes completar todos los campos y subir un archivo.")

# === 2. GENERAR TEST ===
st.subheader("🎯 Generar Test Oficial")
oposiciones_disponibles = cargar_preguntas_desde_drive(lista=True)
oposicion_seleccionada = st.selectbox("Selecciona una oposición:", oposiciones_disponibles)

criterio = obtener_criterio_test(oposicion_seleccionada)

if criterio:
    st.info(f"Criterio de test para {oposicion_seleccionada}: {criterio['descripcion']}")
else:
    st.warning("No hay criterio definido aún para esta oposición. Puedes usar distribución libre.")

if st.button("🧪 Generar Test según examen real"):
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

        test_json = exportar_test_json(preguntas)
        st.download_button(
            label="📥 Descargar test en JSON",
            data=test_json,
            file_name="test_generado.json",
            mime="application/json"
        )

        pdf_path = descargar_pdf_test(preguntas)
        with open(pdf_path, "rb") as f:
            st.download_button(
                label="📄 Descargar test en PDF",
                data=f,
                file_name="test_generado.pdf",
                mime="application/pdf"
            )
