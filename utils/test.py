import json
import os
import random
from datetime import datetime
from utils.drive import subir_archivo_a_drive
from utils.pdf import generar_pdf_test

CARPETA_TEST_JSON = "1dNkIuLDfV_qGmrCepkFYo5IWlfFwkl7w"
CARPETA_TEST_PDF = "1dNkIuLDfV_qGmrCepkFYo5IWlfFwkl7w"

# Estructura tipo oficial (25 preguntas)
estructura_bloques = {
    "constitucion": 3,
    "procedimiento": 5,
    "administracion_local": 3,
    "personal": 4,
    "otros": 10
}

# Clasificación de temas
clasificacion_temas = {
    "TEMA_1 – Constitución Española (I)": "constitucion",
    "TEMA_2 – Constitución Española (II)": "constitucion",
    "TEMA_3 – Administración General del Estado": "administracion_local",
    "TEMA_4 – Organización territorial": "administracion_local",
    "TEMA_5 – Procedimiento Administrativo": "procedimiento",
    "TEMA_6 – Funcionamiento electrónico": "procedimiento",
    "TEMA_7 – Transparencia y acceso a la información": "procedimiento",
    "TEMA_8 – Personal al servicio de la administración": "personal",
    "TEMA_9 – Estatuto del empleado público": "personal",
    "TEMA_10 – Hacienda Pública y control del gasto": "otros",
    # ... Añadir más temas según necesidad
}

def generar_test_examen_completo(nombre_oposicion, temas_dict):
    # Agrupar preguntas por bloque
    bloques = {k: [] for k in estructura_bloques}

    for tema, preguntas in temas_dict.items():
        bloque = clasificacion_temas.get(tema, "otros")
        bloques[bloque].extend(preguntas)

    # Seleccionar aleatoriamente por bloque
    preguntas_finales = []
    for bloque, cantidad in estructura_bloques.items():
        seleccionadas = random.sample(bloques[bloque], min(len(bloques[bloque]), cantidad))
        preguntas_finales.extend(seleccionadas)

    # Mezclar preguntas finales
    random.shuffle(preguntas_finales)

    # Guardar .json local y en Drive
    fecha = datetime.now().strftime("%Y%m%d%H%M%S")
    nombre_archivo = f"{nombre_oposicion}_examen_oficial_{fecha}"
    ruta_local_json = os.path.join("test_generados", f"{nombre_archivo}.json")
    os.makedirs("test_generados", exist_ok=True)

    with open(ruta_local_json, "w") as f:
        json.dump(preguntas_finales, f, indent=2, ensure_ascii=False)

    subir_archivo_a_drive(ruta_local_json, CARPETA_TEST_JSON)

    # Generar PDF
    ruta_local_pdf = os.path.join("test_generados", f"{nombre_archivo}.pdf")
    generar_pdf_test(nombre_archivo, preguntas_finales, ruta_local_pdf)
    subir_archivo_a_drive(ruta_local_pdf, CARPETA_TEST_PDF)

    return ruta_local_json, ruta_local_pdf, preguntas_finales
