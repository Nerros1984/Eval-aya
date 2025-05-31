import streamlit as st
import json
import os
import unicodedata
from utils.drive import (
    obtener_oposiciones_con_tema_json,
    descargar_archivo_de_drive
)
from utils.temas import extraer_temas_de_texto, guardar_temas_json
from utils.test import generar_test_examen_completo
from utils.sheets import obtener_tests_de_oposicion

st.set_page_config(page_title="EvalúaYa", layout="wide")
st.title("📘 EvalúaYa - Plataforma Inteligente de Test para Oposiciones")

def limpiar_texto(texto):
    if not isinstance(texto, str):
        return ""
    return unicodedata.normalize("NFKD", texto).encode("utf-8", "ignore").decode("utf-8")

modo = st.sidebar.radio("Selecciona el modo:", ["📤 Subir nuevo temario", "📚 Usar temario guardado"])

if modo == "📤 Subir nuevo temario":
    st.subheader("Subir un nuevo temario")
    archivo = st.file_uploader("Selecciona archivo .docx", type=["docx"])
    nombre_oposicion = st.text_input("Nombre de la oposición")

    if archivo and nombre_oposicion:
        ruta_temporal = os.path.join("/tmp", archivo.name)
        with open(ruta_temporal, "wb") as f:
            f.write(archivo.getbuffer())

        if st.button("Procesar y subir temario"):
            temas_extraidos = extraer_temas_de_texto(ruta_temporal)
            if temas_extraidos:
                enlace = guardar_temas_json(temas_extraidos, nombre_oposicion)
                st.success(f"✅ Temario procesado correctamente y subido a Drive.")
                st.markdown(f"[Abrir archivo en Drive]({enlace})")
            else:
                st.warning("No se detectaron temas con el formato adecuado.")

elif modo == "📚 Usar temario guardado":
    st.subheader("Seleccionar un temario existente")

    oposiciones = obtener_oposiciones_con_tema_json()
    if not oposiciones:
        st.warning("No hay temarios disponibles en Drive.")
    else:
        seleccion = st.selectbox("Selecciona oposición", oposiciones)

        with st.expander("📂 Ver tests ya generados para esta oposición"):
            tests_guardados = obtener_tests_de_oposicion(seleccion)
            if tests_guardados:
                for test in tests_guardados:
                    st.markdown(f"🧾 **{test['nombre_test']}** ({test['fecha']})  
[Descargar PDF]({test['pdf']})")
            else:
                st.markdown("No hay tests guardados aún para esta oposición.")


    oposiciones = obtener_oposiciones_con_tema_json()
    if not oposiciones:
        st.warning("No hay temarios disponibles en Drive.")
    else:
        seleccion = st.selectbox("Selecciona oposición", oposiciones)

        with st.expander("📂 Ver tests ya generados para esta oposición"):
            if seleccion:
                tests_guardados = obtener_tests_de_oposicion(seleccion)
                if tests_guardados:
                    for test in tests_guardados:
                        st.markdown(f"🧾 **{test['nombre_test']}** ({test['fecha']})  
[Descargar PDF]({test['pdf']})")
                else:
                    st.markdown("No hay tests guardados aún para esta oposición.")

        nombre_archivo = f"temas_{seleccion.strip().lower().replace(' ', '_')}.json"
        path_local = os.path.join("/tmp", nombre_archivo)

        if descargar_archivo_de_drive(nombre_archivo, "1popTRkA-EjI8_4WqKPjkldWVpCYsJJjm", path_local):
            st.success("Temario descargado correctamente")

            if st.button("🧠 Generar examen simulado con IA"):
                with open(path_local, "r", encoding="utf-8") as f:
                    temas_dict = json.load(f)

                try:
                    ruta_json, ruta_pdf, preguntas = generar_test_examen_completo(seleccion, temas_dict)
                    st.success("✅ Test generado correctamente")

                    with open(ruta_pdf, "rb") as f_pdf:
                        st.download_button("📎 Descargar test en PDF", f_pdf, file_name=os.path.basename(ruta_pdf))

                    st.subheader("📝 Responde al test")
                    respuestas_usuario = {}
                    for idx, pregunta in enumerate(preguntas, 1):
                        st.markdown(f"**{idx}. {pregunta['pregunta']}**")
                        respuesta = st.radio(
                            f"Selecciona una respuesta para la pregunta {idx}",
                            pregunta["opciones"],
                            key=f"preg_{idx}"
                        )
                        respuestas_usuario[idx] = respuesta

                    if st.button("✅ Validar respuestas"):
                        aciertos = 0
                        total = len(preguntas)
                        for idx, pregunta in enumerate(preguntas, 1):
                            correcta = pregunta.get("respuesta_correcta", "")
                            seleccionada = respuestas_usuario.get(idx, "")
                            if seleccionada == correcta:
                                aciertos += 1
                        st.info(f"Has acertado {aciertos} de {total} preguntas. ({(aciertos/total)*100:.1f}%)")
                except Exception as e:
                    st.error(f"❌ Error generando el test: {e}")
        else:
            st.warning("No se pudo encontrar el archivo del temario.")
