
import streamlit as st
from datetime import datetime
import json
from utils.sheets import registrar_en_sheet, obtener_oposiciones_guardadas
from utils.test import generar_test_con_criterio_real, obtener_criterio_test
from utils.drive import subir_archivo_a_drive
import tempfile
import unicodedata

st.set_page_config(page_title="EvalúaYa - Generador de Test por Temario", layout="centered")

# Estado inicial
if "modo" not in st.session_state:
    st.session_state.modo = None
if "archivo" not in st.session_state:
    st.session_state.archivo = None

st.title("🧠 EvalúaYa - Generador de Test por Temario")

# Botones de selección
st.markdown("### ¿Qué deseas hacer?")
col1, col2 = st.columns(2)
with col1:
    if st.button("📂 Subir nuevo temario"):
        st.session_state.modo = "subir"
with col2:
    if st.button("✨ Usar oposición guardada"):
        st.session_state.modo = "usada"

# -----------------------------------
# SUBIR NUEVO TEMARIO
# -----------------------------------
if st.session_state.modo == "subir":
    st.subheader("📂 Subida de Temario")
    archivo = st.file_uploader("📄 Sube un archivo DOCX o PDF con tu temario:", type=["pdf", "docx"])
    if archivo:
        st.session_state.archivo = archivo

    tipo_contenido = st.selectbox("🔎 ¿Qué contiene este archivo?", ["Temario completo", "Resumen", "Tema individual"])
    nombre_oposicion = st.text_input("📜 Nombre de la oposición (Ej: Administrativo Junta Andalucía)")

    if st.session_state.archivo and nombre_oposicion:
        if st.button("✅ Guardar y registrar temario"):
            # Guardar archivo en carpeta 'temarios'
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp.write(st.session_state.archivo.read())
                tmp_path = tmp.name

            url_drive = subir_archivo_a_drive(tmp_path, nombre_oposicion, carpeta_padre_id="1x08mfjA7JhnVk9OxvXJD54MLmtdZDCJb")

            registrar_en_sheet(
                nombre_oposicion,
                tipo_contenido,
                url_drive,
                "",  # json aún no generado
                datetime.now().strftime("%Y-%m-%d %H:%M")
            )
            st.success("✅ Temario guardado con éxito.")

# -----------------------------------
# USAR OPOSICIÓN GUARDADA
# -----------------------------------
elif st.session_state.modo == "usada":
    st.subheader("🎯 Generar Test Oficial")
    oposiciones = obtener_oposiciones_guardadas()
    if not oposiciones:
        st.info("ℹ️ Aún no hay temarios registrados. Sube uno primero.")
    else:
        seleccion = st.selectbox("Selecciona una oposición:", list(oposiciones.keys()))
        if seleccion:
            criterio = obtener_criterio_test(seleccion)
            st.markdown(f"🧾 **Criterio de test para {seleccion}**: {criterio}")
            if st.button("🧪 Generar Test según examen real"):
                preguntas = generar_test_con_criterio_real(seleccion)
                if preguntas:
                    st.success("✅ Test generado con éxito.")
                    for i, p in enumerate(preguntas):
                        st.markdown(f"**{i+1}. {p['pregunta']}**")
                        for opcion in p["opciones"]:
                            st.markdown(f"- {opcion}")
                        st.markdown(f"✅ Respuesta correcta: **{p['respuesta']}**")
                else:
                    st.warning("⚠️ No se encontraron preguntas suficientes.")
