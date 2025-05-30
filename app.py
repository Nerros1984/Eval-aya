import streamlit as st
import json
import os
from utils.test import generar_test_examen_completo

st.set_page_config(page_title="EvalúaYa - Generador de Test", layout="centered")
st.title("📘 EvalúaYa - Generador de Test de Oposiciones")

modo = st.radio("", ["📂 Subir nuevo temario", "✨ Usar oposición guardada"], index=1)

if modo == "✨ Usar oposición guardada":
    st.subheader("📚 Usar oposición ya registrada")

    # Seleccionar oposición
    nombre_oposicion = st.selectbox("Selecciona una oposición:", [
        "Administrativo Ayuntamiento Sevilla",
        # Agrega más si fuera necesario
    ])

    tipo_test = st.selectbox("Tipo de test", [
        "Simulacro examen oficial"
    ])

    if st.button("📅 Generar test"):
        try:
            # Cargar archivo de temas desde local (test)
            nombre_archivo = f"temas_{nombre_oposicion}.json"
            ruta = os.path.join("temarios_json", nombre_archivo)

            if not os.path.exists(ruta):
                st.warning("No se ha encontrado el archivo de temas. Asegúrate de haber procesado un temario antes.")
            else:
                with open(ruta, "r", encoding="utf-8") as f:
                    temas_dict = json.load(f)

                ruta_json, ruta_pdf, preguntas = generar_test_examen_completo(nombre_oposicion, temas_dict)

                st.success("Test generado correctamente.")

                with open(ruta_pdf, "rb") as pdf:
                    st.download_button(
                        label="📎 Descargar test PDF",
                        data=pdf,
                        file_name=os.path.basename(ruta_pdf),
                        mime="application/pdf"
                    )

                st.markdown("---")
                st.subheader("📝 Realiza el test")
                respuestas_usuario = []

                for idx, pregunta in enumerate(preguntas, 1):
                    st.markdown(f"**{idx}. {pregunta['pregunta']}**")
                    seleccion = st.radio("", pregunta['opciones'], key=f"preg_{idx}")
                    respuestas_usuario.append((pregunta['respuesta_correcta'], seleccion))

                if st.button("✅ Corregir test"):
                    aciertos = sum(1 for correcta, usuario in respuestas_usuario if correcta == usuario)
                    st.success(f"Has obtenido {aciertos} aciertos sobre {len(preguntas)} preguntas.")

        except Exception as e:
            st.error(f"Error inesperado: {e}")

else:
    st.info("Funcionalidad de subida de temario desactivada en esta vista. Dirígete a la pestaña correspondiente.")
