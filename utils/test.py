import json
import random
import os
from datetime import datetime
from utils.drive import descargar_archivo_de_drive, CARPETA_TEMAS_JSON
from utils.temas import cargar_temas_desde_json_local

CARPETA_TEST_JSON = "1dNkIuLDfV_qGmrCepkFYo5IWlfFwkl7w"

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

    return ruta_local, preguntas

def generar_test_examen_completo(nombre_oposicion, num_preguntas=25):
    nombre_archivo_json = f"temas_{nombre_oposicion.strip().lower().replace(' ', '_')}.json"
    path_local = f"/tmp/{nombre_archivo_json}"
    json_ok = descargar_archivo_de_drive(nombre_archivo_json, CARPETA_TEMAS_JSON, path_local)

    if not json_ok:
        return None, ["Error: No se pudo acceder al temario completo para esta oposición."]

    temas_dict = cargar_temas_desde_json_local(path_local)
    contenido_total = " ".join(temas_dict.values())

    bloques = [contenido_total[i:i+400] for i in range(0, len(contenido_total), 400)]
    seleccionados = random.sample(bloques, min(num_preguntas, len(bloques)))

    preguntas = [
        {
            "pregunta": f"Sobre el siguiente fragmento: \n\n{bloque.strip()}\n\n ¿Cuál de las siguientes afirmaciones es correcta?",
            "opciones": [
                "A) Opción simulada 1",
                "B) Opción simulada 2",
                "C) Opción simulada 3",
                "D) Opción simulada 4"
            ],
            "respuesta_correcta": "A) Opción simulada 1"
        }
        for bloque in seleccionados
    ]

    nombre_archivo = f"{nombre_oposicion}_examen_completo_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    ruta_local = os.path.join("test_generados", nombre_archivo)
    os.makedirs("test_generados", exist_ok=True)

    with open(ruta_local, "w") as f:
        json.dump(preguntas, f, indent=2)

    return ruta_local, preguntas
