import os
import json
import re
import tempfile
import streamlit as st
import docx2txt
from datetime import datetime
from utils.drive import subir_archivo_a_drive, descargar_archivo_de_drive, CARPETA_TEMARIOS, CARPETA_TEMAS_JSON, CARPETA_TEST_JSON, CARPETA_TEST_PDF
from utils.sheets import registrar_en_sheet, obtener_oposiciones_guardadas
from utils.temas import extraer_temas_de_texto, guardar_temas_json, cargar_temas_desde_json_local
from utils.test import generar_test_desde_tema, generar_test_examen_completo

st.set_page_config(page_title="EvalúaYa - Generador de Test", page_icon="📘")
st.title("EvalúaYa - Generador de Test de Oposiciones")

modo = st.radio("", ["Subir nuevo temario", "Usar oposición guardada"], horizontal=True)

if modo == "Subir nuevo temario":
    st.subheader("Subida de Temario")
    st.markdown("Sube un archivo DOCX o PDF con tu temario:")
    archivo_temario = st.file_uploader("Subir temario (DOCX o PDF)", type=["pdf", "docx"])

    tipo_contenido = st.selectbox("\u00bfQué contiene este archivo?", ["Temario completo", "Tema individual", "Resumen del temario"])
    nombre_oposicion = st.text_input("Nombre de la oposición (Ej: Administrativo Junta Andalucía)")
    nombre_temario = st.text_input("Nombre del documento de temario (Ej: Temario bloque I)")

    if archivo_temario and nombre_oposicion and nombre_temario:
        if st.button("Detectar temas y mostrar vista previa"):
            extension = archivo_temario.name.split(".")[-1].lower()
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{extension}") as tmp:
                tmp.write(archivo_temario.read())
                tmp_path = tmp.name

            temas_extraidos = extraer_temas_de_texto(tmp_path)
            if temas_extraidos:
                st.session_state.temas_extraidos = temas_extraidos
                st.session_state.tmp_path = tmp_path
                st.session_state.archivo_temario = archivo_temario
                st.session_state.tipo_contenido = tipo_contenido
                st.session_state.nombre_oposicion = nombre_oposicion
                st.session_state.nombre_temario = nombre_temario
                st.success("Temas detectados correctamente. Revisa la vista previa abajo y confirma.")
                for i, t in enumerate(temas_extraidos, 1):
                    st.markdown(f"**Tema {i}:** {t.splitlines()[0]}")
            else:
                st.error("No se han podido detectar temas. Asegúrese de usar el formato recomendado.")

        if 'temas_extraidos' in st.session_state:
            if st.button("Confirmar y registrar temario"):
                with st.spinner("Registrando temario..."):
                    enlace_drive = subir_archivo_a_drive(st.session_state.tmp_path, st.session_state.nombre_oposicion, CARPETA_TEMARIOS)
                    enlace_json = guardar_temas_json(st.session_state.temas_extraidos, st.session_state.nombre_oposicion)

                    registrar_en_sheet(
                        st.session_state.nombre_oposicion,
                        st.session_state.nombre_temario,
                        st.session_state.tipo_contenido,
                        enlace_drive,
                        enlace_json,
                        datetime.now().strftime("%Y-%m-%d %H:%M")
                    )
                    st.success("Temario subido, registrado y procesado correctamente.")

elif modo == "Usar oposición guardada":
    st.subheader("Usar oposición ya registrada")
    oposiciones = obtener_oposiciones_guardadas()

    if not oposiciones:
        st.warning("Aún no hay oposiciones registradas. Sube un temario desde la otra sección.")
    else:
        opcion = st.selectbox("Selecciona una oposición:", oposiciones)
        tipo_test = st.selectbox("Tipo de test", ["Test por temas", "Simulacro examen oficial"])

        nombre_archivo = f"temas_{opcion.strip().lower().replace(' ', '_')}.json"
        path_local = f"/tmp/{nombre_archivo}"
        json_ok = descargar_archivo_de_drive(nombre_archivo, CARPETA_TEMAS_JSON, path_local)

        if not json_ok:
            st.error("El archivo JSON de temas no está disponible localmente.")
        else:
            temas_dict = cargar_temas_desde_json_local(path_local)

            if tipo_test == "Test por temas":
                tema_elegido = st.selectbox("Selecciona un tema", list(temas_dict.keys()))
                num_preguntas = st.slider("Número de preguntas", 5, 50, 10)

                if st.button("Generar test"):
                    ruta_json, preguntas = generar_test_desde_tema(opcion, tema_elegido, num_preguntas)
                    st.success("Test generado correctamente.")
                    st.download_button("Descargar test (JSON)", data=open(ruta_json).read(), file_name=os.path.basename(ruta_json))

            elif tipo_test == "Simulacro examen oficial":
                if st.button("Generar test"):
                    ruta_json, preguntas = generar_test_examen_completo(opcion, 25)
                    st.success("Simulacro generado correctamente.")
                    st.download_button("Descargar test (JSON)", data=open(ruta_json).read(), file_name=os.path.basename(ruta_json))
