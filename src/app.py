import streamlit as st

# Configuración básica de la página
st.set_page_config(
    page_title="Mentor Saber Pro / ICFES",
    page_icon="🤖",
    layout="centered"
)

# Título de la interfaz gráfica
st.title("🤖 Mentor Saber Pro / ICFES")
st.subheader("Asistente Inteligente con RAG y Multiagentes")

st.markdown("""
---
### ¡Entorno de Trabajo Configurado Correctamente!
Este lienzo está listo para conectar el pipeline RAG y los agentes usando **Gemini**.
""")

# Campo de texto de prueba para interactuar
user_input = st.text_input("Escribe una pregunta de prueba:")
if user_input:
    st.info(f"Has escrito: '{user_input}'. Próximamente Gemini responderá aquí.")