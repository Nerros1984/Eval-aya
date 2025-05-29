from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import streamlit as st
import openai
import json
import re
import tempfile
import unicodedata
from utils.drive import subir_archivo_a_drive
from utils.sheets import registrar_en_sheet, obtener_oposiciones_guardadas
from utils.test import generar_test_con_criterio_real, obtener_criterio_test

st.set_page_config(page_title="EvalúaYa - Generador de Test por Temario", layout="centered")

st.title("🧠 EvalúaYa - Generador de Test por Temario")

modo = st.radio("", ["📤 Subir nuevo temario", "🎯 Usar oposición guardada"])

if modo == "📤 Subir nuevo temario":
    st.header("📤 Subida de Temario")
    archivo_subido = st.file_uploader("📄 Sube un archivo DOCX o PDF con tu temario:", type=["pdf", "docx"])
    tipo_contenido = st.selectbox("🔍 ¿Qué contiene este archivo?", ["Temario completo", "Resumen", "Tema individual"])
    nombre_temario = st.text_input("📌 Nombre del temario (Ej: Administrativo Ayuntamiento Sevilla)")
    nombre_oposicion = st.text_input("🏛️ Nombre de la oposición", placeholder="Ej: Auxiliar Administrativo – Ayuntamiento de Sevilla")
    
    if archivo_subido and nombre_temario.strip() and nombre_oposicion.strip():
        if st.button("✅ Guardar y registrar temario"):
            with st.spinner("Subiendo y registrando temario..."):
                extension = archivo_subido.name.split(".")[-1].lower()
                suffix = f".{extension}"
                temp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
                temp.write(archivo_subido.read())
                temp.close()

                # Subir a carpeta correspondiente
                url = subir_archivo_a_drive(temp.name, "temarios")
                registrar_en_sheet(
                    nombre_oposicion,
                    nombre_temario,
                    tipo_contenido,
                    url,
                    "",
                    datetime.now().strftime("%Y-%m-%d %H:%M")
                )
                st.success("✅ Temario guardado correctamente.")
    else:
        st.info("🔼 Sube un archivo válido y completa todos los campos.")

else:
    st.header("🎯 Generar Test Oficial")
    oposiciones = obtener_oposiciones_guardadas()
    if not oposiciones:
        st.warning("⚠️ Aún no hay oposiciones registradas. Sube un temario primero.")
    else:
        seleccion = st.selectbox("Selecciona una oposición:", list(oposiciones.keys()))
        st.info(f"📘 Criterio de test para {seleccion}: {obtener_criterio_test(seleccion)}")

        if st.button("🧪 Generar Test según examen real"):
            with st.spinner("Generando test..."):
                preguntas = generar_test_con_criterio_real(seleccion)

            if preguntas:
                st.success("✅ Test generado con éxito.")
                for i, pregunta in enumerate(preguntas):
                    st.markdown(f"### Pregunta {i + 1}")
                    st.write(pregunta["pregunta"])
                    st.radio(
                        "Selecciona una opción:",
                        options=pregunta["opciones"],
                        key=f"pregunta_{i}"
                    )
                    st.divider()

                # PDF export
                def exportar_pdf(preguntas):
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                    c = canvas.Canvas(temp_file.name, pagesize=A4)
                    width, height = A4

                    c.setFont("Helvetica-Bold", 14)
                    c.drawString(100, height - 60, "Preguntas del test")
                    c.setFont("Helvetica", 12)
                    y = height - 100
                    for i, p in enumerate(preguntas):
                        c.drawString(50, y, f"{i+1}. {p['pregunta']}")
                        y -= 20
                        for op in p["opciones"]:
                            c.drawString(70, y, f"- {op}")
                            y -= 18
                        y -= 10
                        if y < 100:
                            c.showPage()
                            y = height - 60

                    c.showPage()
                    c.setFont("Helvetica-Bold", 14)
                    c.drawString(100, height - 60, "Respuestas correctas")
                    c.setFont("Helvetica", 12)
                    y = height - 100
                    for i, p in enumerate(preguntas):
                        c.drawString(50, y, f"{i+1}. Respuesta: {p['respuesta']}")
                        y -= 20
                        if y < 100:
                            c.showPage()
                            y = height - 60

                    c.save()
                    return temp_file.name

                pdf_path = exportar_pdf(preguntas)
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        label="📄 Descargar test en PDF",
                        data=f,
                        file_name="test_generado.pdf",
                        mime="application/pdf"
                    )
            else:
                st.error("❌ No se pudo generar el test. Inténtalo más tarde.")
