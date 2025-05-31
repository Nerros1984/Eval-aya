import streamlit as st
import json
import os
import unicodedata

from utils.drive import obtener_oposiciones_con_tema_json, descargar_archivo_de_drive
from utils.test import generar_test_examen_completo

st.set_page_config(page_title="EvalúaYa - Generador de Test", page_icon="🔮", layout="centered")
st.title("🧪 EvalúaYa - Generador Inteligente de Test")

# Función para evitar errores con caracteres raros
def limpiar_texto(texto):
    if not isinstance(texto, str):
        return ""
    return unicodedata.normalize("NFKD", texto).encode("utf-8", "ignore").decode("utf-8")

modo = st.selectbox("Selecciona el modo:", ["Usar temario guardado"], index=0)

if modo == "Usar temario guardado":
    st.subheader("📚 Generar test desde temario existente")

    oposiciones = obtener_oposiciones_con_tema_json()
    if not oposiciones:
        st.warning("No hay temarios disponibles en Drive.")
    else:
        seleccion = st.selectbox("Selecciona oposición", oposiciones)

        nombre_archivo = f"temas_{seleccion.strip().lower().replace(' ', '_')}.json"
        path_local = os.path.join("/tmp", nombre_archivo)

        descargado = descargar_archivo_de_drive(nombre_archivo, "1popTRkA-EjI8_4WqKPjkldWVpCYsJJjm", path_local)

        if descargado:
            st.success("Temario descargado correctamente")
            if st.button("🗓️ Generar test simulado con IA"):
                with open(path_local, 'r', encoding='utf-8') as f:
                    temas_dict = json.load(f)

                try:
                    ruta_json, ruta_pdf, preguntas = generar_test_examen_completo(seleccion, temas_dict)
                    st.success("Test generado correctamente.")

                    with open(ruta_pdf, "rb") as f:
                        st.download_button("📎 Descargar test PDF", f, file_name=os.path.basename(ruta_pdf))

                    st.subheader("🔎 Vista previa del test")
                    for idx, preg in enumerate(preguntas, 1):
                        pregunta = limpiar_texto(preg.get('pregunta', ''))
                        st.markdown(f"**{idx}. {pregunta}**")
                        for op in preg.get('opciones', []):
                            st.markdown(f"- {limpiar_texto(op)}")
                except Exception as e:
                    st.error(f"Error generando test: {e}")
        else:
            st.warning("No se pudo encontrar o descargar el archivo JSON del temario.")
