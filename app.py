import streamlit as st
from utils.drive import subir_archivo_a_drive
from utils.sheets import registrar_en_sheet, obtener_oposiciones_guardadas
from utils.test import generar_test_con_criterio_real, obtener_criterio_test
from datetime import datetime
import tempfile
import json
import openai
import re
import unicodedata

st.set_page_config(page_title="EvalúaYa - Generador de Test por Temario", layout="centered")
st.title("\U0001f9e0 EvalúaYa - Generador de Test por Temario")

# -- Helpers --
def normalizar_nombre(nombre):
    nfkd = unicodedata.normalize('NFKD', nombre)
    solo_ascii = nfkd.encode('ASCII', 'ignore').decode('utf-8')
    return solo_ascii.lower().replace(" ", "_")

# -- Selección inicial --
st.markdown("## Elige una opción:")
opcion = st.radio("", ["📂 Subir nuevo temario", "🎯 Usar oposición guardada"], label_visibility="collapsed")

# -----------------------------
# OPCIÓN 1: SUBIR TEMARIO NUEVO
# -----------------------------
if opcion == "📂 Subir nuevo temario":
    st.markdown("### \U0001f4c4 Subida de Temario")
    archivo = st.file_uploader("Sube un archivo DOCX o PDF con tu temario:", type=["docx", "pdf"])
    tipo_contenido = st.selectbox("\U0001f50d ¿Qué contiene este archivo?", ["Temario completo", "Resumen", "Tema individual"])
    nombre_temario = st.text_input("\U0001f4d1 Nombre del temario (Ej: Administrativo Junta Andalucía)")
    nombre_oposicion = st.text_input("\U0001f3db️ Nombre de la oposición", placeholder="Ej: Auxiliar Administrativo – Ayuntamiento de Sevilla")

    if archivo and nombre_temario and nombre_oposicion:
        if st.button("✅ Guardar y registrar temario"):
            with tempfile.NamedTemporaryFile(delete=False, suffix=archivo.name.split(".")[-1]) as tmp:
                tmp.write(archivo.read())
                ruta = tmp.name
            url = subir_archivo_a_drive(ruta, normalizar_nombre(nombre_temario))
            registrar_en_sheet(nombre_temario, tipo_contenido, url, "", datetime.now().strftime("%Y-%m-%d %H:%M"), nombre_oposicion)
            st.success("Temario guardado y registrado correctamente.")

# -----------------------------
# OPCIÓN 2: USAR TEMARIO EXISTENTE
# -----------------------------
elige_oposicion = None
if opcion == "🎯 Usar oposición guardada":
    st.markdown("### \U0001f3af Generar Test Oficial")
    oposiciones = obtener_oposiciones_guardadas()
    elige_oposicion = st.selectbox("Selecciona una oposición:", oposiciones)

    if elige_oposicion:
        criterio = obtener_criterio_test(elige_oposicion)
        st.info(f"Criterio de test para {elige_oposicion}: {criterio['descripcion']}")

        if st.button("\U0001f58a️ Generar Test según examen real"):
            test = generar_test_con_criterio_real(elige_oposicion)
            st.success("Test generado con éxito.")
            for i, p in enumerate(test):
                st.markdown(f"**{i+1}. {p['pregunta']}**")
                for op in p['opciones']:
                    st.markdown(f"- {op}")

            # Exportar
            st.download_button("📄 Descargar JSON", data=json.dumps(test, indent=2), file_name="test.json", mime="application/json")
