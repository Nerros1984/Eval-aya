import streamlit as st
import os
import tempfile
from datetime import datetime
from utils.sheets import registrar_en_sheet, obtener_oposiciones_guardadas
from utils.drive import subir_archivo_a_drive, CARPETA_TEMARIOS

st.set_page_config(page_title="EvalúaYa - Generador de Test por Temario", page_icon="🧠", layout="wide")
st.markdown("<h1 style='font-size: 42px;'>🧠 EvaluúaYa - Generador de Test por Temario</h1>", unsafe_allow_html=True)

modo = st.radio("", ["📁 Subir nuevo temario", "🌟 Usar oposición guardada"])
st.write("---")

if modo == "📁 Subir nuevo temario":
    st.subheader("📂 Subida de Temario")
    st.markdown("### 📄 Sube un archivo DOCX o PDF con tu temario:")

    archivo = st.file_uploader("Subir temario (DOCX o PDF)", type=["pdf", "docx"])
    tipo_contenido = st.selectbox("\ud83d\udd0d¡¿Qué contiene este archivo?", ["Temario completo", "Temario por temas"])
    nombre_oposicion = st.text_input("<span style='font-size: 14px;'>🌸 Nombre de la oposición (Ej: Administrativo Junta Andalucía)</span>", key="nombre_oposicion", label_visibility="visible")
    nombre_temario = st.text_input("<span style='font-size: 14px;'>🗂️ Nombre del documento de temario (Ej: Temario bloque I)</span>", key="nombre_temario", label_visibility="visible")

    if archivo and nombre_oposicion:
        if st.button("✅ Guardar y registrar temario"):
            try:
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    tmp.write(archivo.read())
                    tmp_path = tmp.name

                url_drive = subir_archivo_a_drive(tmp_path, nombre_oposicion, CARPETA_TEMARIOS)
                os.remove(tmp_path)

                registrar_en_sheet(
                    nombre_oposicion,
                    tipo_contenido,
                    nombre_temario,
                    "",
                    url_drive,
                    datetime.now().strftime("%Y-%m-%d %H:%M")
                )
                st.success("✅ Temario subido y registrado correctamente.")

                st.write("---")
                st.subheader("🎯 Generar Test Oficial")
                modo_test = st.selectbox("Selecciona tipo de test:", ["Examen tipo oficial (todo el temario)", "Test por tema (próximamente disponible)"])
                n_preguntas = st.slider("Número de preguntas:", 5, 25, 10)
                if st.button("📝 Generar test"):
                    st.info("(Simulado) Generando test con {n_preguntas} preguntas para '{modo_test}'...")
                    st.success("Test generado. (Futura opción de descarga y guardado en Drive)")
            except Exception as e:
                st.error(f"❌ Error al subir o registrar el temario: {e}")
    else:
        st.info("🔷 Sube un archivo válido y escribe un nombre de oposición para comenzar.")

elif modo == "🌟 Usar oposición guardada":
    st.subheader("🎯 Generar Test Oficial")
    try:
        oposiciones = obtener_oposiciones_guardadas()
        if oposiciones:
            seleccion = st.selectbox("Selecciona una oposición:", oposiciones)
            modo_test = st.selectbox("Selecciona tipo de test:", ["Examen tipo oficial (todo el temario)", "Test por tema (próximamente disponible)"])
            n_preguntas = st.slider("Número de preguntas:", 5, 25, 10)
            if st.button("📝 Generar test"):
                st.info(f"(Simulado) Generando test de '{seleccion}' con {n_preguntas} preguntas...")
                st.success("Test generado. (Futura opción de descarga y guardado en Drive)")
        else:
            st.warning("⚠️ Aún no hay temarios registrados en la plataforma.")
    except Exception as e:
        st.error(f"❌ Error al cargar oposiciones: {e}")
