# Paso 1: Importar las librerías necesarias
import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
import plotly.express as px
from streamlit_lottie import st_lottie
import json

# Configuración de la página
st.set_page_config(page_title="📊 InHedge APP- Estrategias de Cobertura", page_icon="📊", layout="wide")

# Función para cargar una animación Lottie desde un archivo JSON
@st.cache_data
def load_lottiefile(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)

# Cargar la animación Lottie
lottie_animation = load_lottiefile("inhedge.json")  # Asegúrate de tener un archivo Lottie JSON válido en el mismo directorio

# Personalización de estilos y título
st.markdown("""
<style>
body { background-color: #EFEEE7; }
.stButton>button { color: white; background-color: #2596be; }
h1 { text-align: center; }
</style>
<h1>📊 InHedge - Estrategias de Cobertura 📊</h1>
""", unsafe_allow_html=True)

# Mostrar la animación Lottie en el centro de la página usando columnas
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st_lottie(lottie_animation, key='hedge_logo', height=300, width=300)

# Paso 2: Crear un formulario centrado en la página principal para recoger información del usuario
st.header("📈 Visualización de Estrategias de Cobertura")
col1, col2, col3 = st.columns([1, 1, 1])

with col2:  # Usar la columna central para los inputs
    toneladas_cubrir = st.number_input("💲 Cantidad de toneladas de aluminio a cubrir:", min_value=0, step=25, key="toneladas")
    contratos = toneladas_cubrir / 25

# Guardar los valores de entrada en session_state para su uso en otros lugares del script
st.session_state['toneladas_cubrir'] = toneladas_cubrir
st.session_state['contratos'] = contratos

# Paso 3: Definir la fórmula de cobertura con collar
def calcular_cobertura(toneladas, precio_actual):
    # Definir los precios de ejercicio de la opción de compra y de la opción de venta
    precio_ejercicio_compra = precio_actual * 1.05  # 5% por encima del precio actual
    precio_ejercicio_venta = precio_actual * 0.95   # 5% por debajo del precio actual

    # Definir la prima (costo) de las opciones
    prima_compra = 1000  # Ejemplo de prima de compra por contrato
    prima_venta = 500    # Ejemplo de prima de venta por contrato

    # Calcular el costo total de la cobertura
    costo_cobertura = contratos * (prima_compra - prima_venta)
    
    # Calcular la pérdida máxima y ganancia máxima
    perdida_maxima = (precio_actual - precio_ejercicio_venta) * toneladas - costo_cobertura
    ganancia_maxima = (precio_ejercicio_compra - precio_actual) * toneladas - costo_cobertura

    return perdida_maxima, ganancia_maxima, costo_cobertura

# Paso 4: Obtener el precio actual del aluminio y realizar cálculos
# Usar datos de ejemplo para el precio del aluminio
precio_aluminio_actual = 2500  # Precio por tonelada en USD
toneladas_cubrir = st.session_state.get('toneladas_cubrir', 0)

perdida_maxima, ganancia_maxima, costo_cobertura = calcular_cobertura(toneladas_cubrir, precio_aluminio_actual)

# Mostrar resultados de la cobertura
st.write(f"**Cobertura para {toneladas_cubrir} toneladas de aluminio ({contratos} contratos)**")
st.write(f"- Costo total de la cobertura: ${costo_cobertura:.2f}")
st.write(f"- Pérdida máxima: ${perdida_maxima:.2f}")
st.write(f"- Ganancia máxima: ${ganancia_maxima:.2f}")

# Paso 5: Crear una gráfica de la cobertura
precios = np.linspace(precio_aluminio_actual * 0.8, precio_aluminio_actual * 1.2, 100)
ganancias = [calcular_cobertura(toneladas_cubrir, precio)[1] for precio in precios]
fig = px.line(x=precios, y=ganancias, labels={'x': 'Precio del Aluminio', 'y': 'Ganancia de la Cobertura'}, title="Cobertura con Collar para Aluminio")
st.plotly_chart(fig, use_container_width=True)

# Paso 6: Simulación de una orden de compra
if st.button('Generar Orden de Compra'):
    st.write("### Orden de Compra Generada")
    st.write(f"**Cantidad a cubrir:** {toneladas_cubrir} toneladas")
    st.write(f"**Contratos:** {contratos}")
    st.write(f"**Costo Total:** ${costo_cobertura:.2f}")
    st.write(f"**Pérdida Máxima:** ${perdida_maxima:.2f}")
    st.write(f"**Ganancia Máxima:** ${ganancia_maxima:.2f}")
    st.write("**Estado de la Orden:** Confirmada")

# Fin del código


