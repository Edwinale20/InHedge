# Paso 1: Importar las librerías necesarias
import streamlit as st
import pandas as pd
import plotly.express as px
import json
from streamlit_lottie import st_lottie

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

# Paso 2: Crear un formulario para ingresar la cantidad a cubrir y el mes
st.header("📈 Visualización de Estrategias de Cobertura")
meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
mes_seleccionado = st.selectbox("📝 Selecciona el mes para cubrir:", meses)
toneladas_a_cubrir = st.number_input("💲 Cantidad a cubrir en toneladas:", min_value=0, step=25, key="toneladas")

# Paso 3: Cargar los precios históricos del aluminio
precios_aluminio = pd.read_csv("inhedge.csv")
precios_aluminio['Fecha'] = pd.to_datetime(precios_aluminio['Fecha'])

# Convertir las columnas de precios a numéricas, manejando los valores no numéricos o faltantes
precios_aluminio['LME Precio'] = pd.to_numeric(precios_aluminio['LME Precio'], errors='coerce')
precios_aluminio['SHFE Precio'] = pd.to_numeric(precios_aluminio['SHFE Precio'], errors='coerce')
precios_aluminio['Tipo de cambio'] = pd.to_numeric(precios_aluminio['Tipo de cambio'], errors='coerce')

precios_2023 = precios_aluminio[precios_aluminio['Fecha'].dt.year == 2023]

# Filtrar los precios del mes seleccionado
mes_index = meses.index(mes_seleccionado) + 1
precios_mes = precios_2023[precios_2023['Fecha'].dt.month == mes_index]

# Mostrar una tabla con los precios de aluminio en el mes seleccionado
st.subheader(f"📅 Precios del Aluminio en {mes_seleccionado} 2023")
st.dataframe(precios_mes)

# Paso 4: Definir la fórmula de cobertura con collar
def calcular_cobertura(toneladas, precio_lme, precio_shfe, tipo_cambio, precio_ejercicio_compra, precio_ejercicio_venta, prima_compra, prima_venta):
    contratos = toneladas / 25
    costo_cobertura = contratos * (prima_compra - prima_venta) * tipo_cambio
    perdida_maxima = (precio_lme - precio_ejercicio_venta) * toneladas - costo_cobertura
    ganancia_maxima = (precio_ejercicio_compra - precio_lme) * toneladas - costo_cobertura
    return perdida_maxima, ganancia_maxima, costo_cobertura

# Paso 5: Calcular la cobertura para el mes seleccionado
if st.button('Simular Estrategia'):
    if toneladas_a_cubrir > 0:
        precio_lme = precios_mes['LME Precio'].mean()
        precio_shfe = precios_mes['SHFE Precio'].mean()
        tipo_cambio = precios_mes['Tipo de cambio'].mean()
        precio_ejercicio_compra = precio_lme * 1.05
        precio_ejercicio_venta = precio_lme * 0.95
        prima_compra = 1000
        prima_venta = 500
        perdida_maxima, ganancia_maxima, costo_cobertura = calcular_cobertura(toneladas_a_cubrir, precio_lme, precio_shfe, tipo_cambio, precio_ejercicio_compra, precio_ejercicio_venta, prima_compra, prima_venta)
        
        # Mostrar los resultados en un dataframe
        df_resultados = pd.DataFrame({
            "Mes": [mes_seleccionado],
            "Toneladas a cubrir": [toneladas_a_cubrir],
            "Precio LME": [precio_lme],
            "Precio SHFE": [precio_shfe],
            "Tipo de Cambio": [tipo_cambio],
            "Pérdida Máxima": [perdida_maxima],
            "Ganancia Máxima": [ganancia_maxima],
            "Costo Cobertura": [costo_cobertura]
        })
        st.subheader("📊 Resultados de la Cobertura")
        st.dataframe(df_resultados)
        
        # Paso 6: Crear gráficos de resultados
        # Gráfico de líneas de Pérdida y Ganancia Máxima
        fig_line = px.line(df_resultados, x="Mes", y=["Pérdida Máxima", "Ganancia Máxima"], title="Pérdida y Ganancia Máxima por Mes", labels={"value": "USD", "Mes": "Mes"})
        st.plotly_chart(fig_line, use_container_width=True)
        
        # Gráfico de barras del Costo de Cobertura
        fig_bar = px.bar(df_resultados, x="Mes", y="Costo Cobertura", title="Costo de Cobertura por Mes", labels={"Costo Cobertura": "USD", "Mes": "Mes"})
        st.plotly_chart(fig_bar, use_container_width=True)
        
        # Paso 7: Simulación de una orden de compra
        st.write("### Orden de Compra Generada")
        st.write("**Cantidad a cubrir:**")
        st.write(f"{toneladas_a_cubrir} toneladas en {mes_seleccionado}")
        st.write("**Costo Total de la Cobertura:**")
        st.write(f"${costo_cobertura} USD")
        st.write("**Estado de la Orden:** Confirmada")

# Fin del código


