import streamlit as st
import json
import os
from utils.test import generar_test_desde_tema, generar_test_examen_completo
from utils.sheets import obtener_temas_para_oposicion
from utils.drive import descargar_archivo_de_drive

st.set_page_config(page_title="EvaluáYa - Generador de Test de Oposiciones", layout="centered")
st.title("📘 EvaluáYa - Generador de Test de Oposiciones")

modo = st.radio("", ["📂 Subir nuevo temario", "✨ Usar oposición guardada"])

if modo == "📂 Subir nuevo temario":
    st.warning("Esta funcionalidad está en desarrollo. Vuelve pronto.")

else:
    st.markdown("### 📚 Usar oposición ya registrada")

    nombre_oposicion = st.selectbox("Selecciona una oposición:", [
        "Administrativo Ayuntamiento Sevilla",
        "Auxiliar Junta de Andalucía",
        "Técnico Administración General"
    ])

    tipo_test = st.selectbox("Tipo de test", [
        "Simulacro examen oficial",
        "Test por tema (próximamente)"
    ])

    if st.button("📅 Generar test"):
        with st.spinner("Generando test..."):
            try:
                # Descargar archivo de temas (JSON)
                nombre_archivo_temas = f"temas_{nombre_oposicion}.json"
                ruta_local_temas = os.path.join("temarios", nombre_archivo_temas)
                os.makedirs("temarios", exist_ok=True)
                exito = descargar_archivo_de_drive(nombre_archivo_temas, carpeta_drive_id="1popTRkA-EjI8_4WqKPjkldWVpCYsJJjm", path_local_destino=ruta_local_temas)

                if not exito:
                    st.warning("No se ha encontrado el archivo de temas. Asegúrate de haber procesado un temario antes.")
                else:
                    with open(ruta_local_temas, "r", encoding="utf-8") as f:
                        temas_dict = json.load(f)

                    ruta_json, ruta_pdf, preguntas = generar_test_examen_completo(nombre_oposicion, temas_dict)

                    st.success("Test generado correctamente.")

                    # Mostrar test en app
                    st.markdown("### 📝 Test generado")
                    respuestas_usuario = []

                    for idx, pregunta in enumerate(preguntas):
                        st.markdown(f"**{idx+1}. {pregunta['pregunta']}**")
                        respuesta = st.radio("Selecciona una opción", pregunta['opciones'], key=idx)
                        respuestas_usuario.append(respuesta)

                    if st.button("✅ Evaluar respuestas"):
                        aciertos = sum([
                            1 for r, p in zip(respuestas_usuario, preguntas)
                            if r == p['respuesta_correcta']
                        ])
                        st.success(f"Has acertado {aciertos} de {len(preguntas)} preguntas. ({round(aciertos/len(preguntas)*100)}%)")

                    # Botón de descarga del PDF
                    with open(ruta_pdf, "rb") as f:
                        st.download_button("📥 Descargar test PDF", f, file_name=os.path.basename(ruta_pdf))

            except Exception as e:
                st.error(f"Error al generar test: {e}")
