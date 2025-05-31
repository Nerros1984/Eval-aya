import os
import json
import random
from datetime import datetime
import openai
import streamlit as st

from utils.drive import subir_archivo_a_drive, CARPETA_TEST_JSON, CARPETA_TEST_PDF
from utils.pdf import generar_pdf_test
from utils.estructura import estructura_bloques, clasificacion_temas
from utils.sheets import registrar_en_sheet

# Configurar la API key de OpenAI desde secrets
openai.api_key = st.secrets["openai_api_key"]

def generar_preguntas_desde_tema(nombre_tema, contenido_tema, num_preguntas=5):
    prompt = f"""
    Genera {num_preguntas} preguntas tipo test con 4 opciones cada una sobre el siguiente tema:

    Título del tema: {nombre_tema}

    Contenido:
    {contenido_tema}

    El formato debe ser una lista JSON donde cada ítem sea un diccionario con las claves:
    - "pregunta": texto de la pregunta
    - "opciones": lista de 4 opciones
    - "respuesta_correcta": texto exacto de la opción correcta
    """

    try:
        respuesta = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        texto = respuesta.choices[0].message.content
        preguntas = json.loads(texto)
    except Exception as e:
        print("Error procesando respuesta de OpenAI:", e)
        preguntas = []

    return preguntas

def generar_test_examen_completo(nombre_oposicion, temas_dict):
    preguntas_total = []
    preguntas_reserva = []

    temas_validos = [(tema, contenido) for tema, contenido in temas_dict.items() if tema in clasificacion_temas]
    random.shuffle(temas_validos)

    for tema, contenido in temas_validos:
        preguntas = generar_preguntas_desde_tema(tema, contenido, 4)
        preguntas_total.extend(preguntas)
        if len(preguntas_total) >= 90:
            break

    for tema, contenido in temas_validos:
        preguntas = generar_preguntas_desde_tema(tema, contenido, 2)
        preguntas_reserva.extend(preguntas)
        if len(preguntas_reserva) >= 10:
            break

    preguntas_total = preguntas_total[:90]
    preguntas_reserva = preguntas_reserva[:10]

    for p in preguntas_reserva:
        p["reserva"] = True

    todas = preguntas_total + preguntas_reserva
    random.shuffle(todas)

    # ✅ Mensaje visible en la app
    st.warning(f"Se han generado {len(preguntas_total)} preguntas + {len(preguntas_reserva)} de reserva")

    nombre_archivo = f"{nombre_oposicion}_examen_oficial_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    os.makedirs("test_generados", exist_ok=True)

    ruta_json = os.path.join("test_generados", f"{nombre_archivo}.json")
    with open(ruta_json, "w", encoding="utf-8") as f:
        json.dump(todas, f, indent=2, ensure_ascii=False)

    enlace_json = subir_archivo_a_drive(ruta_json, nombre_oposicion, CARPETA_TEST_JSON)
    ruta_pdf = generar_pdf_test(nombre_oposicion, todas, nombre_archivo)
    enlace_pdf = subir_archivo_a_drive(ruta_pdf, nombre_oposicion, CARPETA_TEST_PDF)

    fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
    registrar_en_sheet(nombre_oposicion, nombre_archivo, "test", enlace_pdf, enlace_json, fecha)

    return ruta_json, ruta_pdf, todas
