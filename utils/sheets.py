from utils.google_auth import obtener_cliente

# Reemplaza con tu ID real de la hoja
ID_HOJA = "1AtfqsCJeIFCllD5jyYjO1zsb8HUkrKzXygbqD-LvtJA"
NOMBRE_HOJA = "Tests_Generados"

def registrar_en_sheet(nombre_oposicion, nombre_archivo, tipo, enlace_pdf, enlace_json, fecha):
    cliente = obtener_cliente()
    hoja = cliente.open_by_key(ID_HOJA).worksheet(NOMBRE_HOJA)

    fila = [
        nombre_oposicion,
        nombre_archivo,
        tipo,
        enlace_pdf,
        enlace_json,
        fecha
    ]
    hoja.append_row(fila)
    print(f"✅ Registrado en hoja: {fila}")
