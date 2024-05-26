# Paso 1: Importar las librerías necesarias
import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
import plotly.express as px
from streamlit_lottie import st_lottie
import json

# Paso 2: Diseño de pagina de InHedge
st.set_page_config(
    page_title="InHedge App",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Función para cargar una animación Lottie desde un archivo JSON
@st.cache_data
def load_lottiefile(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)

# Cargar la animación Lottie
lottie_animation = load_lottiefile("inhedge.json")  # Asegúrate de tener un archivo Lottie JSON válido en el mismo directorio

# Mostrar la animación Lottie en la página
st_lottie(lottie_animation, key='hedge_logo', height=300, width=300)

# Título de la página
st.title("Bienvenido a la App de Derivados de InHedge")
st.subheader("Una herramienta para gestionar y analizar estrategias de cobertura")

