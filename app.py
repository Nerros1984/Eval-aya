import streamlit as st
import os
import docx2txt
from utils.test import generar_test_desde_tema, generar_test_examen_completo
from utils.sheets import registrar_en_sheet, obtener_oposiciones_guardadas
from utils.drive import subir_archivo_a_drive
from utils.temas import extraer_temas_de_texto, guardar_temas_json
import tempfile

st.set_page_config(page_title="EvalúaYa", layout="centered")
st.title("📘 EvalúaYa - Generador de Test de Oposiciones")

st.markdown("---")

modo = st.sidebar.radio("Selecciona una opción:", ["Subir nuevo temario", "Usar oposición guardada"])

if modo == "Subir nuevo temario":
    st.header("📤 Subir nuevo temario")

    nombre_oposicion = st.text_input("Nombre de la oposición")
    archivo = st.file_uploader("Sube el archivo del temario (.docx)", type=["docx"])

    if archivo and nombre_oposicion:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            tmp.write(archivo.read())
            ruta_temporal = tmp.name

        st.success("Archivo subido correctamente. Procesando...")

        # Extraer texto y generar temas
        texto = docx2txt.process(ruta_temporal)
        temas = extraer_temas_de_texto(texto)

        if temas:
            url_json = guardar_temas_json(temas, nombre_oposicion)
            st.success("Temas generados y guardados correctamente.")
            st.markdown(f"[Ver archivo JSON de temas]({url_json})")
        else:
            st.warning("No se detectaron temas en el documento.")

        # Subir archivo original a Drive
        url_pdf = subir_archivo_a_drive(ruta_temporal, nombre_oposicion)

        # Registrar en hoja de cálculo
        registrar_en_sheet(nombre_oposicion, "temario_completo", url_pdf, url_json, "")

elif modo == "Usar oposición guardada":
    st.header("📚 Usar oposición ya registrada")

    oposiciones = obtener_oposiciones_guardadas()
    if oposiciones:
        oposicion = st.selectbox("Selecciona una oposición:", oposiciones)
        tipo_test = st.selectbox("Tipo de test", ["Simulacro examen oficial", "Test por temas"])

        if tipo_test == "Test por temas":
            num_preguntas = st.slider("Número de preguntas", 5, 50, 25, step=5)
        else:
            num_preguntas = None

        if st.button("Generar test"):
            if tipo_test == "Simulacro examen oficial":
                test = generar_test_examen_completo(oposicion)
            else:
                test = generar_test_desde_tema(oposicion, num_preguntas)

            if test:
                st.success("Test generado correctamente.")
                st.download_button("Descargar test", test, file_name=f"test_{oposicion}.txt")
            else:
                st.error("No se pudo generar el test. Verifica que haya contenido disponible.")
    else:
        st.warning("Aún no hay oposiciones registradas. Por favor, sube un temario primero.")
