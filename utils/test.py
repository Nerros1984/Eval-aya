import os
import json
import random
from datetime import datetime
from fpdf import FPDF
from drive import subir_archivo_a_drive, CARPETA_TEST_JSON, CARPETA_TEST_PDF

estructura_bloques = {"normativa": 10, "procesos": 10, "transparencia": 5}
clasificacion_temas = {"tema_01": "normativa", "tema_02": "procesos", "tema_03": "transparencia"}  # ejemplo mínimo

def generar_test_examen(nombre_oposicion, temas_dict):
    bloques = {k: [] for k in estructura_bloques}
    for tema, preguntas in temas_dict.items():
        bloque = clasificacion_temas.get(tema, "otros")
        if bloque in bloques:
            bloques[bloque].extend(preguntas)

    seleccionadas = []
    for bloque, cantidad in estructura_bloques.items():
        seleccionadas.extend(random.sample(bloques[bloque], min(len(bloques[bloque]), cantidad)))
    random.shuffle(seleccionadas)

    fecha = datetime.now().strftime("%Y%m%d%H%M%S")
    nombre_archivo = f"{nombre_oposicion}_examen_oficial_{fecha}"

    # Guardar JSON
    os.makedirs("test_generados", exist_ok=True)
    ruta_json = os.path.join("test_generados", f"{nombre_archivo}.json")
    with open(ruta_json, "w", encoding="utf-8") as f:
        json.dump(seleccionadas, f, indent=2, ensure_ascii=False)
    subir_archivo_a_drive(ruta_json, nombre_oposicion, CARPETA_TEST_JSON)

    # Generar PDF
    ruta_pdf = generar_pdf(nombre_oposicion, seleccionadas, nombre_archivo)
    subir_archivo_a_drive(ruta_pdf, nombre_oposicion, CARPETA_TEST_PDF)
    return ruta_pdf, seleccionadas

def generar_pdf(nombre_oposicion, preguntas, nombre_base):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Examen Simulado - {nombre_oposicion}", ln=True, align="C")
    pdf.ln(10)

    for idx, preg in enumerate(preguntas, 1):
        pdf.set_font("Arial", style="B", size=12)
        pdf.multi_cell(0, 10, f"{idx}. {preg['pregunta']}")
        pdf.set_font("Arial", size=12)
        for opcion in preg.get("opciones", []):
            pdf.cell(10)
            pdf.multi_cell(0, 10, f"- {opcion}")
        pdf.ln(3)

    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, txt="Hoja de Respuestas", ln=True, align="C")
    pdf.ln(10)
    for idx, preg in enumerate(preguntas, 1):
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, f"{idx}. {preg['respuesta_correcta']}", ln=True)

    ruta = os.path.join("test_generados", f"{nombre_base}.pdf")
    pdf.output(ruta)
    return ruta
