# app.py (versión base estructurada para flujo limpio)

import streamlit as st
from datetime import datetime
from utils.sheets import registrar_en_sheet, obtener_oposiciones_guardadas
from utils.drive import subir_archivo_a_drive
from utils.test import generar_test_con_criterio_real, obtener_criterio_test

st.set_page_config(page_title="EvalúaYa - Generador de Test por Temario", layout="centered")
st.title("\U0001f9e0 EvalúaYa - Generador de Test por Temario")

# Menú principal: elegir acción
modo = st.radio("", ["\U0001f4c2 Subir nuevo temario", "✨ Usar oposición guardada"], index=0)

if modo == "\U0001f4c2 Subir nuevo temario":
    st.subheader("\ud83d\udcc1 Subida de Temario")

    archivo_subido = st.file_uploader("Sube un archivo DOCX o PDF con tu temario:", type=["pdf", "docx"])
    tipo_contenido = st.selectbox("\ud83d\udd0d ¿Qué contiene este archivo?", ["Temario completo", "Resumen", "Tema individual"])
    nombre_oposicion = st.text_input("\ud83c\udfe2 Nombre de la oposición (Ej: Administrativo Junta Andalucía)")

    if archivo_subido and nombre_oposicion.strip():
        if st.button("\ud83d\udcc5 Guardar y registrar temario"):
            # Guardado en carpeta de Drive
            with open("temp_subida", "wb") as f:
                f.write(archivo_subido.read())
            enlace = subir_archivo_a_drive("temp_subida", nombre_oposicion)

            # Registro en hoja
            registrar_en_sheet(
                nombre_oposicion,
                tipo_contenido,
                "",  # temario json vacío
                enlace,
                datetime.now().strftime("%Y-%m-%d %H:%M")
            )
            st.success("Temario subido y registrado con éxito.")

    else:
        st.info("\u26a0\ufe0f Sube un archivo válido y escribe un nombre de oposición para comenzar.")

elif modo == "✨ Usar oposición guardada":
    st.subheader("\ud83c\udf3f Generar Test Oficial")

    oposiciones = obtener_oposiciones_guardadas()

    if oposiciones:
        seleccion = st.selectbox("Selecciona una oposición:", list(oposiciones.keys()))
        st.info(obtener_criterio_test(seleccion))

        if st.button("\ud83c\udf1f Generar Test según examen real"):
            test = generar_test_con_criterio_real(seleccion)
            if test:
                st.success("Test generado con éxito.")
                for i, p in enumerate(test):
                    st.markdown(f"**{i+1}. {p['pregunta']}**")
                    for letra, opcion in zip(["A", "B", "C", "D"], p["opciones"]):
                        st.markdown(f"- {letra}. {opcion}")
                    st.markdown(f"**Respuesta correcta:** {p['respuesta']}")
                    st.divider()
            else:
                st.error("No se pudo generar el test.")
    else:
        st.warning("\u26a0\ufe0f Aún no hay oposiciones registradas. Sube un temario primero.")
