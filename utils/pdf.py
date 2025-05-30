from fpdf import FPDF
import os

def generar_pdf_test(preguntas, nombre_archivo, carpeta="test_generados"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Título
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "Simulacro de Examen Oficial", ln=True, align="C")
    pdf.ln(10)

    # Preguntas
    pdf.set_font("Arial", size=12)
    for idx, pregunta in enumerate(preguntas, start=1):
        pdf.multi_cell(0, 10, f"{idx}. {pregunta['pregunta']}")
        for opcion in pregunta['opciones']:
            pdf.cell(0, 10, f"   {opcion}", ln=True)
        pdf.ln(5)

    # Página de soluciones
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, "Soluciones", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    for idx, pregunta in enumerate(preguntas, start=1):
        pdf.cell(0, 10, f"{idx}. {pregunta['respuesta_correcta']}", ln=True)

    # Guardar PDF
    os.makedirs(carpeta, exist_ok=True)
    ruta_pdf = os.path.join(carpeta, f"{nombre_archivo}.pdf")
    pdf.output(ruta_pdf)
    return ruta_pdf
