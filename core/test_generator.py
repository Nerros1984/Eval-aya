# core/test_generator.py

import uuid
from datetime import datetime
from utils.gpt import generar_preguntas_gpt


def obtener_estructura_basica(nombre_oposicion):
    """Genera una estructura simple de 5 bloques de 10 preguntas cada uno."""
    return [{"tema": "TEMA_01", "num_preguntas": 10} for _ in range(5)]


def dividir_temario_por_tema(temario_texto):
    """Devuelve el temario entero como único bloque."""
    return {"TEMA_01": temario_texto}


class TestGenerator:
    def __init__(self, nombre_oposicion: str, temario_texto: str):
        self.nombre_oposicion = nombre_oposicion
        self.temario_texto = temario_texto
        self.test_id = str(uuid.uuid4())
        self.fecha = datetime.now().strftime("%Y-%m-%d")

    def generar_test_oficial(self) -> dict:
        estructura = obtener_estructura_basica(self.nombre_oposicion)
        temas_dict = dividir_temario_por_tema(self.temario_texto)

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

        if len(preguntas_finales) < 30:
            raise ValueError("El número de preguntas generadas es insuficiente para validar el test.")

        return {
            "test_id": self.test_id,
            "nombre_oposicion": self.nombre_oposicion,
            "fecha": self.fecha,
            "preguntas": preguntas_finales
        }
