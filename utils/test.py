import json
import os
import random
from datetime import datetime

from utils.drive import subir_archivo_a_drive, CARPETA_TEST_JSON, CARPETA_TEST_PDF
from utils.pdf import generar_pdf_test
from utils.estructura import estructura_bloques, clasificacion_temas
import openai
import streamlit as st

openai.api_key = st.secrets["openai_api_key"]

def generar_preguntas_desde_tema(texto_tema, num_preguntas=5):
    prompt = (
        f"Genera {num_preguntas} preguntas tipo test con 4 opciones y una única respuesta correcta. "
        f"Responde en formato JSON como lista de objetos con los campos: 'pregunta', 'opciones', 'respuesta_correcta'.\n\n"
        f"TEMA:\n{texto_tema}"
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Eres un generador de tests para oposiciones con formato estructurado."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        contenido = response.choices[0].message.content.strip()
        return json.loads(contenido)
    except Exception as e:
        print(f"Error al generar preguntas con OpenAI: {e}")
        return []

def generar_test_desde_tema(nombre_oposicion, tema, num_preguntas):
    preguntas = generar_preguntas_desde_tema(tema, num_preguntas)

    nombre_archivo = f"{nombre_oposicion}_{tema}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    ruta_local = os.path.join("test_generados", f"{nombre_archivo}.json")
    os.makedirs("test_generados", exist_ok=True)

    with open(ruta_local, "w", encoding="utf-8") as f:
        json.dump(preguntas, f, indent=2, ensure_ascii=False)

    subir_archivo_a_drive(ruta_local, nombre_oposicion, CARPETA_TEST_JSON)
    return ruta_local, preguntas

def generar_test_examen_completo(nombre_oposicion, temas_dict):
    bloques = {k: [] for k in estructura_bloques}
    
    for titulo_tema, contenido in temas_dict.items():
        bloque = clasificacion_temas.get(titulo_tema, "otros")
        if bloque in bloques:
            preguntas = generar_preguntas_desde_tema(contenido, 5)
            bloques[bloque].extend(preguntas)

    preguntas_finales = []
    for bloque, cantidad in estructura_bloques.items():
        seleccionadas = random.sample(bloques[bloque], min(len(bloques[bloque]), cantidad))
        preguntas_finales.extend(seleccionadas)

    random.shuffle(preguntas_finales)

    fecha = datetime.now().strftime("%Y%m%d%H%M%S")
    nombre_archivo = f"{nombre_oposicion}_examen_oficial_{fecha}"
    ruta_local_json = os.path.join("test_generados", f"{nombre_archivo}.json")
    os.makedirs("test_generados", exist_ok=True)

    with open(ruta_local_json, "w", encoding="utf-8") as f:
        json.dump(preguntas_finales, f, indent=2, ensure_ascii=False)

    ruta_pdf = generar_pdf_test(nombre_oposicion, preguntas_finales, nombre_archivo)

    subir_archivo_a_drive(ruta_local_json, nombre_oposicion, CARPETA_TEST_JSON)
    subir_archivo_a_drive(ruta_pdf, nombre_oposicion, CARPETA_TEST_PDF)

    return ruta_local_json, ruta_pdf, preguntas_finales
