# utils/test.py
import json
import random
import os
from datetime import datetime
from utils.drive import subir_archivo_a_drive

# ID de las carpetas en Drive
CARPETA_TEST_JSON = "1dNkIuLDfV_qGmrCepkFYo5IWlfFwkl7w"
CARPETA_TEST_PDF = "1dNkIuLDfV_qGmrCepkFYo5IWlfFwkl7w"  # Actualiza si deseas separar

def generar_test_desde_tema(nombre_oposicion, tema, num_preguntas):
    preguntas = [
        {
            "pregunta": f"{tema} - Pregunta {i+1}",
            "opciones": [f"Opción {j+1}" for j in range(4)],
            "respuesta_correcta": "Opción 1"
        }
        for i in range(num_preguntas)
    ]

    nombre_archivo = f"{nombre_oposicion}_{tema}_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    ruta_local = os.path.join("test_generados", nombre_archivo)
    os.makedirs("test_generados", exist_ok=True)

    with open(ruta_local, "w") as f:
        json.dump(preguntas, f, indent=2)

    subir_archivo_a_drive(ruta_local, CARPETA_TEST_JSON)
    return ruta_local, preguntas

def generar_test_examen_completo(nombre_oposicion, preguntas):
    nombre_archivo = f"{nombre_oposicion}_examen_completo_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    ruta_local = os.path.join("test_generados", nombre_archivo)
    os.makedirs("test_generados", exist_ok=True)

    with open(ruta_local, "w") as f:
        json.dump(preguntas, f, indent=2)

    subir_archivo_a_drive(ruta_local, CARPETA_TEST_JSON)
    return ruta_local, preguntas
