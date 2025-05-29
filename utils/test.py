import json
import random
import os
from datetime import datetime

# Carpeta de destino en Drive
CARPETA_TEST_JSON = "1dNkIuLDfV_qGmrCepkFYo5IWlfFwkl7w"

def generar_test_desde_tema(nombre_oposicion, tema, num_preguntas):
    """
    Genera un test simulado desde un tema específico.
    """
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

    return ruta_local, preguntas


def generar_test_examen_completo(nombre_oposicion, num_preguntas):
    """
    Genera un test simulado tipo examen real a partir de toda la oposición.
    """
    preguntas = [
        {
            "pregunta": f"{nombre_oposicion} - Pregunta {i+1}",
            "opciones": [f"Opción {j+1}" for j in range(4)],
            "respuesta_correcta": "Opción 1"
        }
        for i in range(num_preguntas)
    ]

    nombre_archivo = f"{nombre_oposicion}_examen_completo_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    ruta_local = os.path.join("test_generados", nombre_archivo)
    os.makedirs("test_generados", exist_ok=True)

    with open(ruta_local, "w") as f:
        json.dump(preguntas, f, indent=2)

    return ruta_local, preguntas
