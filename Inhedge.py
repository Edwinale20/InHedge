# Paso 1: Importar las librerías necesarias
import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
import plotly.express as px
from streamlit_lottie import st_lottie
import json

# Configuración de la página
st.set_page_config(page_title="📊 InHedge - Estrategias de Cobertura", page_icon="📊", layout="wide")

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
st.subheader("Ingresa la cantidad de toneladas a cubrir por mes en 2023")
df_cobertura = pd.DataFrame(columns=["Mes", "Toneladas a cubrir"])
meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

for mes in meses:
    toneladas = st.number_input(f"💲 Cantidad a cubrir en {mes}:", min_value=0, step=25, key=mes)
    df_cobertura = df_cobertura.append({"Mes": mes, "Toneladas a cubrir": toneladas}, ignore_index=True)

st.dataframe(df_cobertura)

# Paso 3: Cargar los precios históricos del aluminio
uploaded_file = st.file_uploader("Sube un archivo CSV con los precios del aluminio (2021-2023)", type=["csv"])
if uploaded_file is not None:
    precios_aluminio = pd.read_csv(uploaded_file)
    precios_aluminio['Fecha'] = pd.to_datetime(precios_aluminio['Fecha'])
    precios_2023 = precios_aluminio[precios_aluminio['Fecha'].dt.year == 2023]

    # Mostrar una tabla con los precios de aluminio en 2023
    st.subheader("📅 Precios del Aluminio en 2023")
    st.dataframe(precios_2023)

    # Paso 4: Definir la fórmula de cobertura con collar
    def calcular_cobertura(toneladas, precio_actual, precio_ejercicio_compra, precio_ejercicio_venta, prima_compra, prima_venta):
        contratos = toneladas / 25
        costo_cobertura = contratos * (prima_compra - prima_venta)
        perdida_maxima = (precio_actual - precio_ejercicio_venta) * toneladas - costo_cobertura
        ganancia_maxima = (precio_ejercicio_compra - precio_actual) * toneladas - costo_cobertura
        return perdida_maxima, ganancia_maxima, costo_cobertura

    # Paso 5: Calcular la cobertura para cada mes de 2023
    resultados = []
    for mes in df_cobertura['Mes']:
        toneladas = df_cobertura.loc[df_cobertura['Mes'] == mes, 'Toneladas a cubrir'].values[0]
        if toneladas > 0:
            precio_actual = precios_2023[precios_2023['Fecha'].dt.month == meses.index(mes) + 1]['Precio'].mean()
            precio_ejercicio_compra = precio_actual * 1.05
            precio_ejercicio_venta = precio_actual * 0.95
            prima_compra = 1000
            prima_venta = 500
            perdida_maxima, ganancia_maxima, costo_cobertura = calcular_cobertura(toneladas, precio_actual, precio_ejercicio_compra, precio_ejercicio_venta, prima_compra, prima_venta)
            resultados.append([mes, toneladas, precio_actual, perdida_maxima, ganancia_maxima, costo_cobertura])
    
    # Mostrar los resultados en un dataframe
    df_resultados = pd.DataFrame(resultados, columns=["Mes", "Toneladas a cubrir", "Precio Actual", "Pérdida Máxima", "Ganancia Máxima", "Costo Cobertura"])
    st.subheader("📊 Resultados de la Cobertura")
    st.dataframe(df_resultados)

    # Paso 6: Crear gráficos de resultados
    # Gráfico de líneas de Pérdida y Ganancia Máxima por mes
    fig_line = px.line(df_resultados, x="Mes", y=["Pérdida Máxima", "Ganancia Máxima"], title="Pérdida y Ganancia Máxima por Mes", labels={"value": "USD", "Mes": "Mes"})
    st.plotly_chart(fig_line, use_container_width=True)

    # Gráfico de barras del Costo de Cobertura por mes
    fig_bar = px.bar(df_resultados, x="Mes", y="Costo Cobertura", title="Costo de Cobertura por Mes", labels={"Costo Cobertura": "USD", "Mes": "Mes"})
    st.plotly_chart(fig_bar, use_container_width=True)

    # Paso 7: Simulación de una orden de compra
    if st.button('Generar Orden de Compra'):
        st.write("### Orden de Compra Generada")
        st.write("**Cantidad a cubrir por mes:**")
        st.dataframe(df_cobertura)
        st.write("**Costo Total de la Cobertura:**")
        st.dataframe(df_resultados[["Mes", "Costo Cobertura"]])
        st.write("**Estado de la Orden:** Confirmada")

# Fin del código
