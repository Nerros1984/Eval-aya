# app.py

import streamlit as st
from ui.layout import mostrar_titulo, mostrar_footer
from ui.steps import paso_subida_temario, paso_generacion

mostrar_titulo()

# Paso 1: subida del temario
nombre_oposicion, temario_texto = paso_subida_temario()

# Paso 2: generación del test
t_generar = st.button("Generar test oficial")
if t_generar:
    paso_generacion(nombre_oposicion, temario_texto)

mostrar_footer()
