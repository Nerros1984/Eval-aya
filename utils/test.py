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
            "pregunta": f"{tema}: ¿Cuál de las siguientes afirmaciones es correcta?",
            "opciones": [
                f"A) {tema} - Opción incorrecta 1",
                f"B) {tema} - Opción incorrecta 2",
                f"C) {tema} - Opción incorrecta 3",
                f"D) {tema} - Opción correcta"
            ],
            "respuesta_correcta": f"D) {tema} - Opción correcta"
        }
        for _ in range(num_preguntas)
    ]

    nombre_archivo = f"{nombre_oposicion}_{tema}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    ruta_local = os.path.join("test_generados", f"{nombre_archivo}.json")
    os.makedirs("test_generados", exist_ok=True)

    with open(ruta_local, "w", encoding="utf-8") as f:
        json.dump(preguntas, f, indent=2, ensure_ascii=False)

    subir_archivo_a_drive(ruta_local, nombre_oposicion, CARPETA_TEST_JSON)
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
        if disponibles:
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

    subir_archivo_a_drive(ruta_local_json, nombre_oposicion, CARPETA_TEST_JSON)
    subir_archivo_a_drive(ruta_pdf, nombre_oposicion, CARPETA_TEST_PDF)

    return ruta_local_json, ruta_pdf, preguntas_finales
