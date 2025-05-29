import random

CRITERIOS_TEST = {
    "Auxiliar Administrativo – Ayuntamiento de Sevilla": {
        "total_preguntas": 90,
        "descripcion": "70 preguntas teóricas (bloques 1-4 y 6) y 20 de ofimática (bloque 5)",
        "bloques": {
            "teorico": {
                "bloques_incluidos": [1, 2, 3, 4, 6],
                "n_preguntas": 70
            },
            "ofimatica": {
                "bloques_incluidos": [5],
                "n_preguntas": 20
            }
        }
    }
}

def obtener_criterio_test(nombre_oposicion):
    return CRITERIOS_TEST.get(nombre_oposicion)

# Simulación: cargamos preguntas aleatorias por bloque (en práctica se leerán desde Drive)
def generar_test_con_criterio_real(nombre_oposicion):
    criterio = obtener_criterio_test(nombre_oposicion)
    if not criterio:
        return []

    preguntas_finales = []
    for parte in criterio["bloques"].values():
        for bloque in parte["bloques_incluidos"]:
            preguntas = generar_preguntas_ficticias(bloque, parte["n_preguntas"])
            preguntas_finales.extend(preguntas)
    return preguntas_finales

def generar_preguntas_ficticias(bloque, n):
    opciones = ["A", "B", "C", "D"]
    preguntas = []
    for i in range(n):
        pregunta = {
            "pregunta": f"¿Pregunta simulada del bloque {bloque} número {i+1}?",
            "opciones": [f"Opción {x}" for x in opciones],
            "respuesta": random.choice(opciones)
        }
        preguntas.append(pregunta)
    return preguntas

def descargar_pdf_test(preguntas):
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    import tempfile

    pdf_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    c = canvas.Canvas(pdf_file.name, pagesize=A4)
    width, height = A4
    y = height - 50
    c.setFont("Helvetica", 12)

    for i, p in enumerate(preguntas):
        c.drawString(50, y, f"{i+1}. {p['pregunta']}")
        y -= 20
        for op in p["opciones"]:
            c.drawString(70, y, f"- {op}")
            y -= 15
        y -= 10
        if y < 100:
            c.showPage()
            y = height - 50

    c.save()
    return pdf_file.name
