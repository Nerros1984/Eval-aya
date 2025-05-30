# utils/test.py
import json
import random
import os
from datetime import datetime
from utils.drive import subir_archivo_a_drive, CARPETA_TEST_JSON, CARPETA_TEST_PDF
from fpdf import FPDF


def generar_test_desde_tema(nombre_oposicion, tema, contenido_tema, num_preguntas):
    preguntas = [
        {
            "pregunta": f"{contenido_tema[:150]}...\n\n¿Cuál de las siguientes afirmaciones es correcta?",
            "opciones": [
                "A) Opcion simulada 1",
                "B) Opcion simulada 2",
                "C) Opcion simulada 3",
                "D) Opcion simulada 4"
            ],
            "respuesta_correcta": "A) Opcion simulada 1"
        }
        for _ in range(num_preguntas)
    ]

    nombre_archivo = f"{nombre_oposicion}_{tema}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    ruta_json = f"/tmp/{nombre_archivo}.json"
    ruta_pdf = f"/tmp/{nombre_archivo}.pdf"

    with open(ruta_json, "w") as f:
        json.dump(preguntas, f, indent=2)

    generar_pdf_test(preguntas, nombre_oposicion, tema, ruta_pdf)

    enlace_json = subir_archivo_a_drive(ruta_json, nombre_oposicion, CARPETA_TEST_JSON)
    enlace_pdf = subir_archivo_a_drive(ruta_pdf, nombre_oposicion, CARPETA_TEST_PDF)

    return preguntas, enlace_json, enlace_pdf


def generar_test_examen_completo(nombre_oposicion, temas_dict, num_preguntas):
    temas = list(temas_dict.items())
    seleccion = random.sample(temas, min(num_preguntas, len(temas)))

    preguntas = [
        {
            "pregunta": f"Sobre el siguiente fragmento: \n\n{contenido[:200]}...\n\n¿Cuál de las siguientes afirmaciones es correcta?",
            "opciones": [
                "A) Opcion simulada 1",
                "B) Opcion simulada 2",
                "C) Opcion simulada 3",
                "D) Opcion simulada 4"
            ],
            "respuesta_correcta": "A) Opcion simulada 1"
        }
        for _, contenido in seleccion
    ]

    nombre_archivo = f"{nombre_oposicion}_examen_completo_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    ruta_json = f"/tmp/{nombre_archivo}.json"
    ruta_pdf = f"/tmp/{nombre_archivo}.pdf"

    with open(ruta_json, "w") as f:
        json.dump(preguntas, f, indent=2)

    generar_pdf_test(preguntas, nombre_oposicion, "Examen completo", ruta_pdf)

    enlace_json = subir_archivo_a_drive(ruta_json, nombre_oposicion, CARPETA_TEST_JSON)
    enlace_pdf = subir_archivo_a_drive(ruta_pdf, nombre_oposicion, CARPETA_TEST_PDF)

    return preguntas, enlace_json, enlace_pdf


def generar_pdf_test(preguntas, nombre_oposicion, titulo, ruta_pdf):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, f"Test generado para: {nombre_oposicion}\nTitulo: {titulo}\n\n---\n")

    for i, pregunta in enumerate(preguntas, 1):
        pdf.multi_cell(0, 10, f"{i}. {pregunta['pregunta']}")
        for op in pregunta['opciones']:
            pdf.cell(0, 10, op, ln=1)
        pdf.ln(5)

    pdf.add_page()
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Soluciones:", ln=True)
    for i, pregunta in enumerate(preguntas, 1):
        pdf.cell(0, 10, f"{i}. {pregunta['respuesta_correcta']}", ln=True)

    pdf.output(ruta_pdf)
