import streamlit as st
import os
import json
import datetime
from utils.drive import subir_archivo_a_drive, CARPETA_TEMARIOS, CARPETA_TEMAS_JSON
from utils.sheets import registrar_en_sheet, obtener_oposiciones_guardadas
from utils.temas import extraer_temas_de_texto, guardar_temas_json, cargar_temas_desde_json_local
from utils.test import generar_test_desde_tema, generar_test_examen_completo

st.set_page_config(page_title="EvalúaYa - Generador de Test de Oposiciones")
st.title("📘 EvalúaYa - Generador de Test de Oposiciones")

modo = st.radio("", ["📂 Subir nuevo temario", "✨ Usar oposición guardada"], horizontal=True)

if modo == "📂 Subir nuevo temario":
    st.header("📁 Subida de Temario")
    st.subheader("📄 Sube un archivo DOCX o PDF con tu temario:")
    archivo = st.file_uploader("Subir temario (DOCX o PDF)", type=["pdf", "docx"])
    tipo_contenido = st.selectbox("¿Qué contiene este archivo?", ["Temario completo", "Temario por temas"])
    nombre_oposicion = st.text_input("🌸 Nombre de la oposición (Ej: Administrativo Junta Andalucía)")
    nombre_temario = st.text_input("📄 Nombre del documento de temario (Ej: Temario bloque I)")

    if archivo and nombre_oposicion:
        if st.button("✅ Guardar y registrar temario"):
            with open(f"/tmp/{archivo.name}", "wb") as f:
                f.write(archivo.getvalue())
            tmp_path = f"/tmp/{archivo.name}"

            enlace = subir_archivo_a_drive(tmp_path, nombre_oposicion, CARPETA_TEMARIOS)

            temas_extraidos = extraer_temas_de_texto(tmp_path)
            enlace_temas = guardar_temas_json(temas_extraidos, nombre_oposicion)

            registrar_en_sheet([
                nombre_oposicion,
                tipo_contenido,
                nombre_temario,
                "",
                enlace,
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            ])

            st.success("✅ Temario subido y registrado correctamente.")

elif modo == "✨ Usar oposición guardada":
    st.header("📚 Usar oposición ya registrada")
    oposiciones = obtener_oposiciones_guardadas()

    if not oposiciones:
        st.warning("⚠️ Aún no hay temarios registrados en la plataforma.")
    else:
        oposicion = st.selectbox("Selecciona una oposición:", oposiciones)
        tipo_test = st.selectbox("Tipo de test", ["Test por temas", "Simulacro examen oficial"])

        if tipo_test == "Test por temas":
            nombre_normalizado = oposicion.strip().lower().replace(" ", "_")
            ruta_temporal = f"/tmp/temas_{nombre_normalizado}.json"

            if os.path.exists(ruta_temporal):
                temas_dict = cargar_temas_desde_json_local(ruta_temporal)
                tema_seleccionado = st.selectbox("Selecciona el tema:", list(temas_dict.keys()))
                num_preguntas = st.slider("Número de preguntas", 5, 50, 10)
                if st.button("📝 Generar test"):
                    test = generar_test_desde_tema(temas_dict[tema_seleccionado], num_preguntas)
                    st.write(test)
            else:
                st.error("❌ El archivo JSON de temas no está disponible localmente.")

        elif tipo_test == "Simulacro examen oficial":
            if st.button("📝 Generar test"):
                test = generar_test_examen_completo(oposicion)
                st.write(test)
