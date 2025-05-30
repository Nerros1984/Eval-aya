# utils/test.py
import json
import os
import random
from datetime import datetime

from utils.drive import subir_archivo_a_drive, CARPETA_TEST_JSON, CARPETA_TEST_PDF
from utils.pdf import generar_pdf_test
from utils.estructura import estructura_bloques, clasificacion_temas

def generar_test_desde_tema(nombre_oposicion, tema, num_preguntas):
    preguntas = [
        {
            "pregunta": f"{tema} - Pregunta {i+1}",
            "opciones": [f"Opcion {j+1}" for j in range(4)],
            "respuesta_correcta": "Opcion 1"
        }
        for i in range(num_preguntas)
    ]

    nombre_archivo = f"{nombre_oposicion}_{tema}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    ruta_local = os.path.join("test_generados", f"{nombre_archivo}.json")
    os.makedirs("test_generados", exist_ok=True)

    with open(ruta_local, "w", encoding="utf-8") as f:
        json.dump(preguntas, f, indent=2, ensure_ascii=False)

    subir_archivo_a_drive(ruta_local, CARPETA_TEST_JSON)
    return ruta_local, preguntas

def generar_test_examen_completo(nombre_oposicion, temas_dict):
    bloques = {k: [] for k in estructura_bloques}
    for tema, preguntas in temas_dict.items():
        bloque = clasificacion_temas.get(tema, "otros")
        if bloque in bloques:
            bloques[bloque].extend(preguntas)

    preguntas_finales = []
    for bloque, cantidad in estructura_bloques.items():
        disponibles = bloques.get(bloque, [])
        seleccionadas = random.sample(disponibles, min(len(disponibles), cantidad))
        preguntas_finales.extend(seleccionadas)

    random.shuffle(preguntas_finales)

    fecha = datetime.now().strftime("%Y%m%d%H%M%S")
    nombre_archivo = f"{nombre_oposicion}_examen_oficial_{fecha}"
    ruta_local_json = os.path.join("test_generados", f"{nombre_archivo}.json")
    os.makedirs("test_generados", exist_ok=True)

    with open(ruta_local_json, "w", encoding="utf-8") as f:
        json.dump(preguntas_finales, f, indent=2, ensure_ascii=False)

    ruta_pdf = generar_pdf_test(nombre_oposicion, preguntas_finales, nombre_archivo)

    subir_archivo_a_drive(ruta_local_json, CARPETA_TEST_JSON)
    subir_archivo_a_drive(ruta_pdf, CARPETA_TEST_PDF)

    return ruta_local_json, ruta_pdf, preguntas_finales


# utils/pdf.py
from fpdf import FPDF
import os
from utils.drive import subir_archivo_a_drive, CARPETA_TEST_PDF

def generar_pdf_test(nombre_oposicion, preguntas, nombre_base):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Examen Simulado - {nombre_oposicion}", ln=True, align="C")
    pdf.ln(10)

    for idx, pregunta in enumerate(preguntas, 1):
        if not isinstance(pregunta, dict) or 'pregunta' not in pregunta:
            continue
        pdf.set_font("Arial", style="B", size=12)
        pdf.multi_cell(0, 10, f"{idx}. {pregunta['pregunta']}")
        pdf.set_font("Arial", size=12)
        for opcion in pregunta.get("opciones", []):
            pdf.cell(10)
            pdf.multi_cell(0, 10, f"- {opcion}")
        pdf.ln(5)

    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, txt="Hoja de Respuestas", ln=True, align="C")
    pdf.ln(10)

    for idx, pregunta in enumerate(preguntas, 1):
        if not isinstance(pregunta, dict) or 'respuesta_correcta' not in pregunta:
            continue
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, f"{idx}. {pregunta['respuesta_correcta']}", ln=True)

    os.makedirs("test_generados", exist_ok=True)
    ruta_pdf = os.path.join("test_generados", f"{nombre_base}.pdf")
    pdf.output(ruta_pdf)

    subir_archivo_a_drive(ruta_pdf, nombre_oposicion, CARPETA_TEST_PDF)
    return ruta_pdf


# app.py (fragmento clave)
import streamlit as st
from utils.test import generar_test_examen_completo

if st.button("Generar examen oficial"):
    with st.spinner("Generando test..."):
        ruta_json, ruta_pdf, preguntas = generar_test_examen_completo(nombre_oposicion, temas_dict)
        st.success("Test generado correctamente")

        # Mostrar preguntas
        for idx, p in enumerate(preguntas, 1):
            st.markdown(f"**{idx}. {p['pregunta']}**")
            for o in p['opciones']:
                st.markdown(f"- {o}")

        with open(ruta_pdf, "rb") as f:
            st.download_button(
                label="Descargar PDF con test y hoja de respuestas",
                data=f,
                file_name=os.path.basename(ruta_pdf),
                mime="application/pdf"
            )
