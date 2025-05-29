import random
import json
import os
import tempfile
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# Criterios por oposición
def obtener_criterio_test(nombre_oposicion):
    criterios = {
        "Auxiliar Administrativo – Ayuntamiento de Sevilla": {
            "descripcion": "70 preguntas teóricas (bloques 1, 2, 3, 4 y 6) + 20 preguntas de ofimática (bloque 5)",
            "bloques_teoricos": [1, 2, 3, 4, 6],
            "bloques_ofimatica": [5],
            "n_teoricas": 70,
            "n_ofimatica": 20
        }
    }
    return criterios.get(nombre_oposicion)

# Carga preguntas previamente guardadas en Drive/JSON locales (mejorable)
def cargar_preguntas_json(nombre_oposicion):
    nombre_archivo = nombre_oposicion.lower().replace(" ", "_").replace("–", "-")
    path = f"data/test_{nombre_archivo}.json"
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return json.load(f)

# Generación estructurada
def generar_test_con_criterio_real(nombre_oposicion):
    criterio = obtener_criterio_test(nombre_oposicion)
    preguntas = cargar_preguntas_json(nombre_oposicion)
    if not preguntas or not criterio:
        return []

    preguntas_por_bloque = {i: [] for i in range(1, 7)}
    for p in preguntas:
        bloque = int(p.get("bloque", 1))
        preguntas_por_bloque[bloque].append(p)

    seleccionadas = []

    # Reparto proporcional
    n_bloques_teo = len(criterio["bloques_teoricos"])
    por_bloque_teo = criterio["n_teoricas"] // n_bloques_teo

    for bloque in criterio["bloques_teoricos"]:
        disponibles = preguntas_por_bloque.get(bloque, [])
        seleccionadas.extend(random.sample(disponibles, min(por_bloque_teo, len(disponibles))))

    for bloque in criterio["bloques_ofimatica"]:
        disponibles = preguntas_por_bloque.get(bloque, [])
        seleccionadas.extend(random.sample(disponibles, min(criterio["n_ofimatica"], len(disponibles))))

    random.shuffle(seleccionadas)
    return seleccionadas

# Exportación como JSON
def exportar_test_json(preguntas):
    return json.dumps(preguntas, indent=2)

# Exportación como PDF
def descargar_pdf_test(preguntas):
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    c = canvas.Canvas(temp_file.name, pagesize=A4)
    width, height = A4
    c.setFont("Helvetica", 12)

    y = height - 60
    for i, p in enumerate(preguntas):
        c.drawString(50, y, f"{i + 1}. {p['pregunta']}")
        y -= 20
        for opcion in p['opciones']:
            c.drawString(70, y, f"- {opcion}")
            y -= 18
        y -= 10
        if y < 100:
            c.showPage()
            y = height - 60

    c.save()
    return temp_file.name
