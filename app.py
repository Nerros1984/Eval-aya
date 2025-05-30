import streamlit as st
import tempfile
import os
import json
from utils.drive import subir_archivo_a_drive, descargar_json_de_drive, CARPETA_TEMARIOS, CARPETA_TEMAS_JSON
from utils.sheets import registrar_temario_en_sheets, obtener_oposiciones_guardadas
from utils.test import generar_test_desde_tema, generar_test_examen_completo
from utils.temas import extraer_temas_de_texto, guardar_temas_json

st.set_page_config(page_title="EvalúaYa - Generador de Test de Oposiciones")
st.title("📘 EvalúaYa - Generador de Test de Oposiciones")

modo = st.radio("", ["📁 Subir nuevo temario", "🔅 Usar oposición guardada"], horizontal=True)

if modo == "📁 Subir nuevo temario":
    st.subheader("📂 Subida de Temario")
    st.markdown("### 📄 Sube un archivo DOCX o PDF con tu temario:")

    archivo_temario = st.file_uploader("Subir temario (DOCX o PDF)", type=["pdf", "docx"])

    tipo_contenido = st.selectbox("🔍 ¿Qué contiene este archivo?", ["Temario completo", "Temario por temas"])

    nombre_oposicion = st.text_input("🌸 Nombre de la oposición (Ej: Administrativo Junta Andalucía)")
    nombre_documento = st.text_input("📝 Nombre del documento de temario (Ej: Temario bloque I)")

    if archivo_temario and nombre_oposicion:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(archivo_temario.read())
            archivo_temporal_path = tmp.name

        if st.button("✅ Guardar y registrar temario"):
            with st.spinner("Subiendo y registrando temario..."):
                try:
                    enlace_drive = subir_archivo_a_drive(archivo_temporal_path, nombre_oposicion, CARPETA_TEMARIOS)
                    registrar_temario_en_sheets(nombre_oposicion, tipo_contenido, nombre_documento, enlace_drive)
                    st.success("✅ Temario subido y registrado correctamente.")

                    # Extraer temas y guardar JSON
                    if tipo_contenido == "Temario completo":
                        lista_temas = extraer_temas_de_texto(archivo_temporal_path)
                        if lista_temas:
                            enlace_temas = guardar_temas_json(lista_temas, nombre_oposicion)
                            st.markdown(f"[🔗 Ver archivo JSON de temas en Drive]({enlace_temas})")
                            st.success("Temas procesados correctamente.")
                        else:
                            st.warning("No se encontraron temas en el archivo.")
                except Exception as e:
                    st.error(f"Ocurrió un error: {str(e)}")
    else:
        st.info("📤 Sube un archivo válido y escribe un nombre de oposición para comenzar.")

else:
    st.subheader("📚 Usar oposición ya registrada")
    oposiciones_disponibles = obtener_oposiciones_guardadas()

    if not oposiciones_disponibles:
        st.warning("⚠️ Aún no hay temarios registrados en la plataforma.")
    else:
        seleccion = st.selectbox("Selecciona una oposición:", oposiciones_disponibles)
        tipo_test = st.selectbox("Tipo de test", ["Simulacro examen oficial", "Test por temas"])

        if tipo_test == "Test por temas":
            path_local_tmp = f"/tmp/temas_{seleccion.strip().lower().replace(' ', '_')}.json"
            temas_dict = {}
            try:
                temas_dict = descargar_json_de_drive(seleccion, path_local_tmp)
            except Exception:
                st.error("❌ El archivo JSON de temas no está disponible localmente.")

            if temas_dict:
                tema_elegido = st.selectbox("Selecciona un tema:", list(temas_dict.keys()))
                num_preguntas = st.slider("Número de preguntas", 5, 50, 10)

                if st.button("🧪 Generar test"):
                    test = generar_test_desde_tema(tema_elegido, temas_dict[tema_elegido], num_preguntas)
                    st.json(test)
        else:
            if st.button("🧪 Generar test"):
                test = generar_test_examen_completo(seleccion)
                st.json(test)
