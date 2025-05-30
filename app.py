import streamlit as st
import os
import json
import re
import docx2txt
from datetime import datetime
from utils.drive import subir_archivo_a_drive, CARPETA_TEMARIOS, CARPETA_TEMAS_JSON, autenticar_drive
from utils.sheets import registrar_en_sheet, obtener_oposiciones_guardadas
from utils.test import generar_test_examen_completo, generar_test_desde_tema
from utils.temas import extraer_temas_de_texto, guardar_temas_json, cargar_temas_json

st.set_page_config(page_title="EvaluáYa - Generador de Test por Temario")
st.title("📘 EvaluáYa - Generador de Test de Oposiciones")

modo = st.radio("", ["📁 Subir nuevo temario", "✨ Usar oposición guardada"], horizontal=True)

if modo == "📁 Subir nuevo temario":
    st.header("📂 Subida de Temario")
    st.subheader("📄 Sube un archivo DOCX o PDF con tu temario:")

    archivo_temario = st.file_uploader("Subir temario (DOCX o PDF)", type=["pdf", "docx"])
    tipo_contenido = st.selectbox("📎 ¿Qué contiene este archivo?", ["Temario completo", "Temario por temas"])
    nombre_oposicion = st.text_input("<span style='font-size: 14px;'>🌸 Nombre de la oposición (Ej: Administrativo Junta Andalucía)</span>", label_visibility="visible")
    nombre_documento = st.text_input("<span style='font-size: 14px;'>📄 Nombre del documento de temario (Ej: Temario bloque I)</span>", label_visibility="visible")

    if archivo_temario and nombre_oposicion:
        if st.button("✅ Guardar y registrar temario"):
            with st.spinner("Subiendo y procesando el archivo..."):
                with open("/tmp/temporal", "wb") as f:
                    f.write(archivo_temario.read())
                url_drive = subir_archivo_a_drive("/tmp/temporal", nombre_oposicion, CARPETA_TEMARIOS)
                temas_extraidos = extraer_temas_de_texto("/tmp/temporal")
                guardar_temas_json(temas_extraidos, nombre_oposicion, CARPETA_TEMAS_JSON)
                registrar_en_sheet(nombre_oposicion, tipo_contenido, nombre_documento, None, url_drive, datetime.now().strftime("%Y-%m-%d %H:%M"))
            st.success("✅ Temario subido y registrado correctamente.")
    else:
        st.info("🔷 Sube un archivo válido y escribe un nombre de oposición para comenzar.")

else:
    st.header("📚 Usar oposición ya registrada")
    lista_opos = obtener_oposiciones_guardadas()
    if lista_opos:
        oposicion = st.selectbox("Selecciona una oposición:", lista_opos)
        tipo_test = st.selectbox("Tipo de test", ["Simulacro examen oficial", "Test por temas"])

        if tipo_test == "Test por temas":
            temas_disponibles = cargar_temas_json(oposicion)
            if temas_disponibles:
                lista_temas = list(temas_disponibles.keys())
                tema_seleccionado = st.selectbox("Selecciona el tema", lista_temas)
                num_preguntas = st.slider("Número de preguntas", 5, 50, 10)
                if st.button("📝 Generar test"):
                    test = generar_test_desde_tema(oposicion, tema_seleccionado, num_preguntas)
                    st.write(test)
            else:
                st.warning("⚠️ No se han encontrado temas disponibles para esta oposición.")

        elif tipo_test == "Simulacro examen oficial":
            if st.button("📝 Generar test"):
                test = generar_test_examen_completo(oposicion)
                st.write(test)
    else:
        st.warning("⚠️ Aún no hay temarios registrados en la plataforma.")
