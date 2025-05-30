import os
import json
import random
from datetime import datetime
from utils.drive import subir_archivo_a_drive, CARPETA_TEST_JSON, CARPETA_TEST_PDF
from utils.pdf import generar_pdf_test

estructura_bloques = {
    "bloque_1": 3,
    "bloque_2": 3,
    "bloque_3": 4,
    "bloque_4": 5,
    "bloque_5": 5,
    "bloque_6": 5,
}

clasificacion_temas = {
    "#TEMA_1 – La Constitución Española (I)": "bloque_1",
    "#TEMA_2 – Derechos y deberes de los ciudadanos...": "bloque_1",
    "#TEMA_11 – El sistema de Seguridad Social en España": "bloque_6",
    # ... añade el resto manualmente
}

def generar_test_desde_tema(nombre_oposicion, tema, contenido, num_preguntas):
    preguntas = [
        {
            "pregunta": f"{contenido} – Pregunta {i+1}",
            "opciones": [f"Opción A", f"Opción B", f"Opción C", f"Opción D"],
            "respuesta_correcta": "Opción A"
        }
        for i in range(num_preguntas)
    ]

    fecha = datetime.now().strftime("%Y%m%d%H%M%S")
    nombre_archivo = f"{nombre_oposicion}_{tema}_test_{fecha}"
    ruta_local_json = os.path.join("test_generados", f"{nombre_archivo}.json")
    os.makedirs("test_generados", exist_ok=True)

    with open(ruta_local_json, "w", encoding="utf-8") as f:
        json.dump(preguntas, f, indent=2, ensure_ascii=False)

    subir_archivo_a_drive(ruta_local_json, nombre_oposicion, CARPETA_TEST_JSON)

    ruta_local_pdf = os.path.join("test_generados", f"{nombre_archivo}.pdf")
    generar_pdf_test(preguntas, ruta_local_pdf, nombre_archivo)
    subir_archivo_a_drive(ruta_local_pdf, nombre_oposicion, CARPETA_TEST_PDF)

    return ruta_local_json, preguntas

def generar_test_examen_completo(nombre_oposicion, temas_dict):
    bloques = {k: [] for k in estructura_bloques}

    for tema, preguntas in temas_dict.items():
        bloque = clasificacion_temas.get(tema, "otros")
        bloques[bloque].extend(preguntas)

    preguntas_finales = []
    for bloque, cantidad in estructura_bloques.items():
        seleccionadas = random.sample(bloques.get(bloque, []), min(len(bloques.get(bloque, [])), cantidad))
        preguntas_finales.extend(seleccionadas)

    random.shuffle(preguntas_finales)

    fecha = datetime.now().strftime("%Y%m%d%H%M%S")
    nombre_archivo = f"{nombre_oposicion}_examen_oficial_{fecha}"
    ruta_local_json = os.path.join("test_generados", f"{nombre_archivo}.json")
    os.makedirs("test_generados", exist_ok=True)

    with open(ruta_local_json, "w", encoding="utf-8") as f:
        json.dump(preguntas_finales, f, indent=2, ensure_ascii=False)

    subir_archivo_a_drive(ruta_local_json, nombre_oposicion, CARPETA_TEST_JSON)

    ruta_local_pdf = os.path.join("test_generados", f"{nombre_archivo}.pdf")
    generar_pdf_test(preguntas_finales, ruta_local_pdf, nombre_archivo)
    subir_archivo_a_drive(ruta_local_pdf, nombre_oposicion, CARPETA_TEST_PDF)

    return ruta_local_json, preguntas_finales
