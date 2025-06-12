# core/test_generator.py

import uuid
from datetime import datetime

from .estructura import obtener_estructura_test
from core.temas import dividir_temas_en_dict
from utils.gpt import generar_preguntas_gpt


class TestGenerator:
    def __init__(self, nombre_oposicion: str, temario_texto: str):
        self.nombre_oposicion = nombre_oposicion
        self.temario_texto = temario_texto
        self.test_id = str(uuid.uuid4())
        self.fecha = datetime.now().strftime("%Y-%m-%d")

    def generar_test_oficial(self) -> dict:
        """Genera el test completo según la estructura oficial."""
        estructura = obtener_estructura_test(self.nombre_oposicion)
        temas_dict = dividir_temas_en_dict(self.temario_texto)

        preguntas_finales = []
        for bloque in estructura:
            tema = temas_dict.get(bloque["tema"])
            if not tema:
                continue

            preguntas = generar_preguntas_gpt(
                tema_texto=tema,
                num_preguntas=bloque["num_preguntas"]
            )
            preguntas_finales.extend(preguntas)

        if len(preguntas_finales) < 50:
            raise ValueError("El número de preguntas generadas es insuficiente para validar el test.")

        return {
            "test_id": self.test_id,
            "nombre_oposicion": self.nombre_oposicion,
            "fecha": self.fecha,
            "preguntas": preguntas_finales
        }
