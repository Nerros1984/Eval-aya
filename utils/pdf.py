from fpdf import FPDF
import os
from utils.drive import subir_archivo_a_drive, CARPETA_TEST_PDF

def generar_pdf_test(nombre_oposicion, preguntas, nombre_base):
    if not preguntas or not isinstance(preguntas, list):
        print("❌ No hay preguntas para generar el PDF.")
        return None

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

