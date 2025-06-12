# EvalúaYa - Generador de Test con IA

Convierte cualquier texto en preguntas tipo test con ayuda de IA (OpenAI).

## Uso

1. Pega un texto en la interfaz.
2. Pulsa "Generar test".
3. Visualiza las preguntas generadas con 4 opciones.

## Configuración

- Añade tu clave de OpenAI en `.streamlit/secrets.toml`:

```
OPENAI_API_KEY = "sk-proj-..."
```

## Requisitos

- Python 3.9+
- streamlit
- openai

## Ejecución local

```bash
streamlit run app.py
```

## Despliegue en Streamlit Cloud

1. Sube este repo a GitHub.
2. Ve a https://streamlit.io/cloud.
3. Conecta el repositorio y añade tu secret desde el panel.

