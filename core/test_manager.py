# core/test_manager.py

import os
import json
from datetime import datetime
from utils.drive import subir_archivo_a_drive
from utils.pdf import generar_pdf_test

RUTA_LOCAL_JSON = "data/tests_json"
RUTA_LOCAL_PDF = "data/tests_pdf"


def guardar_test_json(test_dict: dict) -> str:
    os.makedirs(RUTA_LOCAL_JSON, exist_ok=True)
    nombre_archivo = f"{test_dict['nombre_oposicion'].replace(' ', '_')}_{test_dict['test_id']}.json"
    ruta = os.path.join(RUTA_LOCAL_JSON, nombre_archivo)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(test_dict, f, ensure_ascii=False, indent=2)
    return ruta


def generar_y_guardar_pdf(test_dict: dict) -> str:
    os.makedirs(RUTA_LOCAL_PDF, exist_ok=True)
    nombre_archivo = f"{test_dict['nombre_oposicion'].replace(' ', '_')}_{test_dict['test_id']}.pdf"
    ruta = os.path.join(RUTA_LOCAL_PDF, nombre_archivo)
    generar_pdf_test(test_dict, ruta)
    return ruta


def registrar_test_en_drive(test_dict: dict, ruta_pdf: str) -> str:
    carpeta_drive = "test_pdf"
    enlace = subir_a_drive(ruta_pdf, carpeta_destino=carpeta_drive)
    return enlace


def registrar_metadata_en_sheets(test_dict: dict, enlace_pdf: str):
    from utils.sheets import registrar_test_generado

    data = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "nombre_oposicion": test_dict["nombre_oposicion"],
        "test_id": test_dict["test_id"],
        "num_preguntas": len(test_dict["preguntas"]),
        "enlace_pdf": enlace_pdf
    }
    registrar_test_generado(data)

