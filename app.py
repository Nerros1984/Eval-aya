import streamlit as st
from datetime import datetime
from utils.sheets import registrar_en_sheet, obtener_oposiciones_guardadas
from utils.drive import subir_archivo_a_drive
from utils.test import generar_test_con_criterio_real, obtener_criterio_test

st.set_page_config(page_title="EvalúaYa - Generador de Test por Temario", layout="centered")

st.title("🧠 EvalúaYa - Generador de Test por Temario")

# Estilo limpio con botones para elegir flujo
col1, col2 = st.columns(2)
opcion = None
with col1:
    if st.button("📂 Subir nuevo temario"):
        opcion = "subir"
with col2:
    if st.button("✨ Usar oposición guardada"):
        opcion = "usar"

# Subir temario
if opcion == "subir":
    st.markdown("### Subida de Temario")
    archivo_subido = st.file_uploader("Sube un archivo DOCX o PDF con tu temario:", type=["pdf", "docx"])
    tipo_contenido = st.selectbox("¿Qué contiene este archivo?", ["Temario completo", "Resumen", "Tema individual"])
    nombre_oposicion = st.text_input("📋 Nombre de la oposición (Ej: Administrativo Junta Andalucía)")

    if archivo_subido and nombre_oposicion:
        if st.button("✅ Guardar y registrar temario"):
            # Guardar archivo en Drive y registrar
            with open(f"/tmp/{archivo_subido.name}", "wb") as f:
                f.write(archivo_subido.getvalue())

            url = subir_archivo_a_drive(f"/tmp/{archivo_subido.name}", nombre_oposicion)
            registrar_en_sheet(
                nombre_oposicion,
                tipo_contenido,
                "",
                url,
                datetime.now().strftime("%Y-%m-%d %H:%M")
            )
            st.success("Temario subido y registrado correctamente. Ya puedes generar test desde el panel oficial.")
    else:
        st.info("🔼 Sube un archivo válido y escribe un nombre de oposición para comenzar.")

# Usar temario ya registrado
elif opcion == "usar":
    st.markdown("### 🎯 Generar Test Oficial")
    oposiciones = obtener_oposiciones_guardadas()
    if oposiciones:
        seleccion = st.selectbox("Selecciona una oposición:", list(oposiciones.keys()))
        st.markdown(f"`{oposiciones[seleccion]}`")

        if st.button("🎯 Generar Test según examen real"):
            preguntas = generar_test_con_criterio_real(seleccion)
            if preguntas:
                for i, pregunta in enumerate(preguntas):
                    st.markdown(f"**{i+1}. {pregunta['pregunta']}**")
                    for opcion in pregunta['opciones']:
                        st.markdown(f"- {opcion}")
                st.success("✅ Test generado con éxito.")
            else:
                st.error("❌ No se pudo generar el test. Verifica si hay datos suficientes para esta oposición.")
    else:
        st.warning("⚠️ Aún no hay temarios registrados. Por favor, sube uno antes de generar test.")
