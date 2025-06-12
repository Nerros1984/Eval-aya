# ui/layout.py

import streamlit as st

def mostrar_titulo():
    st.set_page_config(page_title="EvalúaYa", layout="centered")
    st.title("📝 EvalúaYa – Generador de Tests de Oposición")
    st.markdown("---")

def mostrar_footer():
    st.markdown("---")
    st.markdown("Hecho con ❤️ por Javi • EvalúaYa 2025")

def mostrar_confirmacion(texto):
    st.success(f"✅ {texto}")

def mostrar_error(texto):
    st.error(f"❌ {texto}")

def mostrar_spinner(texto):
    return st.spinner(texto)

