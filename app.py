import streamlit as st
import os
import unicodedata
import re
import json
import tempfile
from datetime import datetime
from utils.sheets import registrar_en_sheet, obtener_oposiciones_guardadas
from utils.drive import subir_archivo_a_drive, CARPETA_TEMARIOS

# --- Utilidades internas ---
def normalizar_nombre(nombre):
    nombre = unicodedata.normalize('NFKD', nombre).encode('ascii', 'ignore').decode('utf-8')
    nombre = re.sub(r'[^a-zA-Z0-9\s]', '', nombre)
    nombre = nombre.lower().strip().replace(' ', '_')
    return nombre

def extraer_temas_de_texto(texto):
    temas = {}
    bloques = re.split(r'(Tema\s+\d+\.?\s*)', texto, flags=re.IGNORECASE)
    for i in range(1, len(bloques) - 1, 2):
        numero_tema = bloques[i].strip()
        contenido = bloques[i + 1].strip()
        temas[numero_tema] = contenido
    return temas

def guardar_temas_json(temas, nombre_oposicion, carpeta_salida):
    nombre_normalizado = normalizar_nombre(nombre_oposicion)
    ruta_json = os.path.join(carpeta_salida, f"{nombre_normalizado}_temas.json")
    with open(ruta_json, 'w', encoding='utf-8') as f:
        json.dump(temas, f, ensure_ascii=False, indent=2)
    return ruta_json

# --- Interfaz principal ---
st.set_page_config(page_title="EvalúaYa - Generador de Test por Temario", layout="centered")
st.title("\U0001F9E0 EvalúaYa - Generador de Test por Temario")

modo = st.radio("", ["📂 Subir nuevo temario", "✨ Usar oposición guardada"], horizontal=True)

if modo == "📂 Subir nuevo temario":
    st.subheader("\U0001F4C4 Subida de Temario")
    archivo_subido = st.file_uploader("Sube un archivo DOCX o PDF con tu temario:", type=["pdf", "docx"])
    tipo_contenido = st.selectbox("\U0001F50D ¿Qué contiene este archivo?", ["Temario completo", "Resumen", "Tema individual"])
    nombre_oposicion = st.text_input("\U0001F338 Nombre de la oposición (Ej: Administrativo Junta Andalucía)")
    nombre_temario = st.text_input("\U0001F4D1 Nombre del documento de temario (Ej: Temario bloque I)")

    if archivo_subido and nombre_oposicion.strip() and nombre_temario.strip():
        if st.button("✅ Guardar y registrar temario"):
            try:
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    tmp.write(archivo_subido.read())
                    tmp_path = tmp.name

                url_drive = subir_archivo_a_drive(tmp_path, nombre_oposicion, CARPETA_TEMARIOS)

                with open(tmp_path, 'r', encoding='utf-8', errors='ignore') as f:
                    contenido = f.read()
                temas = extraer_temas_de_texto(contenido)
                ruta_json = guardar_temas_json(temas, nombre_oposicion, "/tmp")

                registrar_en_sheet(
                    nombre_oposicion,
                    tipo_contenido,
                    nombre_temario,
                    "",
                    url_drive,
                    datetime.now().strftime("%Y-%m-%d %H:%M")
                )

                st.success("✅ Temario subido y registrado correctamente.")
            except Exception as e:
                st.error(f"❌ Error al guardar el temario: {e}")
    else:
        st.info("\U0001F4C4 Sube un archivo válido y escribe un nombre de oposición para comenzar.")

elif modo == "✨ Usar oposición guardada":
    st.subheader("🎯 Generar Test Oficial")
    oposiciones = obtener_oposiciones_guardadas()
    if oposiciones:
        seleccion = st.selectbox("Selecciona una oposición:", list(oposiciones.keys()))
        st.markdown(f"Criterio de test para {seleccion}: 70 preguntas teóricas + 20 de ofimática")
        if st.button("✅ Generar Test según examen real"):
            st.success("(Aquí iría la lógica para generar el test real con los criterios definidos)")
    else:
        st.info("⚠️ Aún no hay temarios registrados en la plataforma.")
