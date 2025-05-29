import streamlit as st
from datetime import datetime
from utils.drive import subir_archivo_a_drive
from utils.sheets import registrar_en_sheet, obtener_oposiciones_guardadas
import tempfile
import os

st.set_page_config(page_title="EvalúaYa - Generador de Test por Temario", layout="centered")

st.title("🧠 EvalúaYa - Generador de Test por Temario")
st.markdown("---")

# Bloque principal con botones iniciales
st.markdown("## Elige una opción para comenzar:")
col1, col2 = st.columns(2)
accion = None
with col1:
    if st.button("📂 Subir nuevo temario"):
        accion = "subir"
with col2:
    if st.button("✨ Usar oposición guardada"):
        accion = "usar"

st.markdown("---")

# SUBIR NUEVO TEMARIO
if accion == "subir":
    st.subheader("📤 Subida de Temario")
    archivo_subido = st.file_uploader("📄 Sube un archivo DOCX o PDF con tu temario:", type=["pdf", "docx"])
    tipo_contenido = st.selectbox("🔍 ¿Qué contiene este archivo?", ["Temario completo", "Resumen", "Tema individual"])
    nombre_oposicion = st.text_input("🏛️ Nombre de la oposición (Ej: Administrativo Ayuntamiento de Sevilla)")

    if archivo_subido and nombre_oposicion.strip():
        if st.button("✅ Guardar y registrar temario"):
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(archivo_subido.name)[-1]) as tmp:
                    tmp.write(archivo_subido.read())
                    tmp_path = tmp.name

                url_drive = subir_archivo_a_drive(tmp_path, nombre_oposicion, carpeta_padre_id="1x08mfjA7JhnVk9OxvXJD54MLmtdZDCJb")
                registrar_en_sheet(
                    nombre_oposicion,
                    tipo_contenido,
                    url_drive,
                    "",  # tema
                    url_drive,
                    datetime.now().strftime("%Y-%m-%d %H:%M")
                )
                st.success("✅ Temario registrado correctamente.")
            except Exception as e:
                st.error(f"❌ Error al registrar el temario: {e}")
    else:
        st.info("🔼 Sube un archivo válido y escribe un nombre de oposición para continuar.")

# USAR OPOSICIÓN GUARDADA
elif accion == "usar":
    st.subheader("🎯 Generar Test Oficial")
    oposiciones = obtener_oposiciones_guardadas()
    if oposiciones:
        seleccion = st.selectbox("Selecciona una oposición:", list(oposiciones.keys()))
        st.markdown(f"📘 {oposiciones[seleccion]}")
        st.button("🧪 Generar test según examen real")
    else:
        st.warning("⚠️ Aún no hay oposiciones registradas.")
