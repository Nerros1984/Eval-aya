import streamlit as st
import os
import json
from datetime import datetime
from utils.sheets import guardar_registro_temario, obtener_oposiciones_guardadas
from utils.drive import subir_archivo_a_drive, descargar_archivo_de_drive, CARPETA_TEMARIOS, CARPETA_TEMAS_JSON
from utils.test import generar_test_examen_completo, generar_test_desde_tema
from utils.temas import extraer_temas_de_texto, guardar_temas_json, cargar_temas_desde_json_local

st.set_page_config(page_title="EvaluáYa - Generador de Test por Temario", page_icon="📘")
st.title("📘 EvaluáYa - Generador de Test de Oposiciones")

modo = st.radio("", ["📁 Subir nuevo temario", "✨ Usar oposición guardada"], horizontal=True)

if modo == "📁 Subir nuevo temario":
    st.subheader("📂 Subida de Temario")
    st.markdown("**📄 Sube un archivo DOCX o PDF con tu temario:**")
    archivo_subido = st.file_uploader("Subir temario (DOCX o PDF)", type=["pdf", "docx"])

    tipo_contenido = st.selectbox("📌 ¿Qué contiene este archivo?", ["Temario completo", "Temario por temas"])
    nombre_oposicion = st.text_input("🌸 Nombre de la oposición (Ej: Administrativo Junta Andalucía)")
    nombre_doc = st.text_input("📝 Nombre del documento de temario (Ej: Temario bloque I)")

    if archivo_subido and nombre_oposicion:
        if st.button("✅ Guardar y registrar temario"):
            with st.spinner("Procesando y guardando..."):
                # Guardar archivo en Drive
                tmp_path = f"/tmp/{archivo_subido.name}"
                with open(tmp_path, "wb") as f:
                    f.write(archivo_subido.read())

                enlace_drive = subir_archivo_a_drive(tmp_path, nombre_oposicion, CARPETA_TEMARIOS)

                # Extraer temas y guardar JSON
                temas_extraidos = extraer_temas_de_texto(tmp_path)
                guardar_temas_json(temas_extraidos, nombre_oposicion)

                # Guardar en hoja de cálculo
                guardar_registro_temario(
                    oposicion=nombre_oposicion,
                    tipo=tipo_contenido,
                    temario=nombre_doc,
                    tema="",
                    enlace_drive=enlace_drive,
                    fecha=datetime.now().strftime("%Y-%m-%d %H:%M")
                )

                st.success("✅ Temario subido y registrado correctamente.")

elif modo == "✨ Usar oposición guardada":
    st.subheader("📚 Usar oposición ya registrada")
    oposiciones = obtener_oposiciones_guardadas()

    if oposiciones:
        seleccion = st.selectbox("Selecciona una oposición:", oposiciones)
        tipo_test = st.selectbox("Tipo de test", ["Simulacro examen oficial", "Test por temas"])

        nombre_normalizado = seleccion.strip().lower().replace(" ", "_")
        nombre_archivo = f"temas_{nombre_normalizado}.json"
        path_local = f"/tmp/{nombre_archivo}"

        if tipo_test == "Simulacro examen oficial":
            if st.button("📝 Generar test"):
                with st.spinner("Generando test completo..."):
                    test = generar_test_examen_completo(seleccion)
                    st.success("✅ Test generado")

        elif tipo_test == "Test por temas":
            if not os.path.exists(path_local):
                resultado = descargar_archivo_de_drive(nombre_archivo, CARPETA_TEMAS_JSON, path_local)
            else:
                resultado = path_local

            if resultado:
                temas = cargar_temas_desde_json_local(path_local)
                tema_seleccionado = st.selectbox("Selecciona un tema:", list(temas.keys()))
                num_preguntas = st.slider("Número de preguntas", min_value=5, max_value=50, value=10, step=5)

                if st.button("📝 Generar test"):
                    with st.spinner("Generando test por tema..."):
                        test = generar_test_desde_tema(temas[tema_seleccionado], num_preguntas)
                        st.success("✅ Test generado")
            else:
                st.error("❌ El archivo JSON de temas no está disponible localmente.")
    else:
        st.info("ℹ️ Aún no hay temarios registrados en la plataforma.")
