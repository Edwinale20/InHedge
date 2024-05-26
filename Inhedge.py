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

# Paso 3: Introducción de InHedge
st.header("Introducción")
st.write("""
InHedge es una empresa especializada en asesoría financiera con un enfoque en coberturas para Commodities y FX.
Nuestro propósito es ayudar a las empresas a mitigar los riesgos financieros derivados de la volatilidad de precios y las fluctuaciones del tipo de cambio.
Esta app tiene como objetivo proporcionar herramientas para gestionar y analizar estrategias de cobertura, permitiendo a nuestros clientes tomar decisiones informadas y protegerse contra posibles pérdidas.
""")

# Espacio para dos animaciones Lottie adicionales
st.subheader("Animaciones de Estrategias de Cobertura")
st.write("A continuación, podrás ver dos animaciones que ilustran nuestras estrategias de cobertura:")

# Cargar y mostrar la primera animación Lottie adicional
lottie_animation_1 = load_lottiefile("animacion1.json")  # Asegúrate de tener un archivo Lottie JSON válido
st_lottie(lottie_animation_1, key='strategy1', height=200, width=200)

# Cargar y mostrar la segunda animación Lottie adicional
lottie_animation_2 = load_lottiefile("animacion2.json")  # Asegúrate de tener un archivo Lottie JSON válido
st_lottie(lottie_animation_2, key='strategy2', height=200, width=200)
