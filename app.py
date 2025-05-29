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
    st.subheader("📥 Subida de Temario")
    archivo_subido = st.file_uploader("📄 Sube un archivo DOCX o PDF con tu temario:", type=["pdf", "docx"])
    tipo_contenido = st.selectbox("🔍 ¿Qué contiene este archivo?", ["Temario completo", "Resumen", "Tema individual"])
    nombre_temario = st.text_input("📝 Nombre del temario (Ej: Administrativo Junta Andalucía)")
    nombre_oposicion = st.text_input("🏛️ Nombre de la oposición", placeholder="Ej: Auxiliar Administrativo – Ayuntamiento de Sevilla")

    if archivo_subido and nombre_temario.strip() and nombre_oposicion.strip():
        if st.button("✅ Guardar y registrar temario"):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
                tmp.write(archivo_subido.read())
                ruta = tmp.name
            try:
                url = subir_archivo_a_drive(ruta, nombre_temario)
                registrar_en_sheet(
                    nombre_temario,
                    tipo_contenido,
                    url,
                    "",  # No generamos aún el test, por lo tanto sin JSON
                    datetime.now().strftime("%Y-%m-%d %H:%M")
                )
                st.success("📁 Temario guardado con éxito en Drive y registrado.")
            except Exception as e:
                st.error(f"❌ Error al guardar el temario: {str(e)}")
    else:
        st.info("🛈 Sube un archivo válido y completa todos los campos para continuar.")

elif modo == "🎯 Usar oposición guardada":
    st.subheader("🎯 Generar Test Oficial")
    try:
        oposiciones = obtener_oposiciones_guardadas()
        if not oposiciones:
            st.info("❕ Aún no hay temarios registrados. Sube uno nuevo desde la sección superior.")
        else:
            seleccion = st.selectbox("Selecciona una oposición:", oposiciones)
            criterio = obtener_criterio_test(seleccion)
            st.markdown(f"<div style='background-color:#1f4e79; padding:10px; border-radius:8px; color:white'>{criterio}</div>", unsafe_allow_html=True)

            if st.button("🧪 Generar Test según examen real"):
                preguntas = generar_test_con_criterio_real(seleccion)
                if preguntas:
                    st.success("✅ Test generado con éxito.")
                    for i, pregunta in enumerate(preguntas):
                        st.markdown(f"### Pregunta {i + 1}")
                        st.write(pregunta["pregunta"])
                        st.radio("Selecciona una opción:", options=pregunta["opciones"], key=f"pregunta_{i}")
                        st.divider()
                else:
                    st.error("❌ No se pudieron generar preguntas.")
    except Exception as e:
        st.error(f"❌ Error cargando oposiciones: {str(e)}")
