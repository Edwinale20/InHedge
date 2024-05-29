import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
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
col1, col2, col3 = st.columns([1, 1, 1])

with col2:  # Usar la columna central para los inputs
    toneladas_cubrir = st.number_input("💲 Cantidad a cubrir en toneladas:", min_value=0, step=1, key="toneladas")
    mes_cobertura = st.selectbox("📅 Selecciona el mes de cobertura:", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"])

# Guardar los valores de entrada en session_state para su uso en otros lugares del script
st.session_state['toneladas_cubrir'] = toneladas_cubrir
st.session_state['mes_cobertura'] = mes_cobertura

# Paso 3: Cargar los datos del CSV
df = pd.read_csv('inhedge.csv')

# Convertir la columna Fecha a datetime
df['Fecha'] = pd.to_datetime(df['Fecha'])

# Filtrar los datos para el mes seleccionado
meses = {"Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4, "Mayo": 5, "Junio": 6, "Julio": 7, "Agosto": 8, "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12}
mes_seleccionado = meses[mes_cobertura]
datos_mes = df[df['Fecha'].dt.month == mes_seleccionado]

# Obtener el precio del quinto día del mes
precio_dia = datos_mes.iloc[4]['LME Precio']
fecha_compra = datos_mes.iloc[4]['Fecha']

# Calcular el número de contratos
tamano_contrato = 25  # Cada contrato cubre 25 toneladas
contratos = toneladas_cubrir / tamano_contrato

# Calcular el costo de la cobertura usando el precio del LME y la fórmula del collar
precio_strike = precio_dia
costo_total = contratos * precio_strike

# Crear dataframe con las especificaciones de la operación
especificaciones = pd.DataFrame({
    "Dólares cubiertos": [f"${costo_total:,.2f} USD"],
    "Cantidad cubierta en pesos": [f"${costo_total * 18.75:,.2f} MXN"],  # Suponiendo un tipo de cambio de 18.75 MXN/USD
    "Fecha de compra": [fecha_compra.strftime('%Y-%m-%d')],
    "Precio promedio del día": [f"${precio_dia:,.2f} USD"]
})

# Paso 4: Simulación de la cobertura seleccionada
resultados = []
precios_spot = np.arange(precio_dia - 500, precio_dia + 500, 50)
for spot in precios_spot:
    perdida_maxima = contratos * max(0, precio_strike - spot)
    ganancia_maxima = contratos * max(0, spot - precio_strike)
    ganancia_sin_cobertura = contratos * (spot - precio_strike)
    resultado_lme = ganancia_sin_cobertura - perdida_maxima
    ganancia_cobertura = ganancia_maxima - perdida_maxima
    resultados.append([spot, perdida_maxima, ganancia_maxima, precio_strike, ganancia_sin_cobertura, resultado_lme, ganancia_cobertura])

resultados_df = pd.DataFrame(resultados, columns=["Precio Spot", "Pérdida Máxima", "Ganancia Máxima", "Precio Strike", "Ganancia sin cobertura", "Resultado LME", "Ganancia con cobertura"])

# Mostrar resultados
st.subheader("Resultados de la Cobertura")
st.dataframe(resultados_df)

# Gráfica de barras de pérdidas y ganancias
fig = px.bar(resultados_df, x="Precio Spot", y=["Pérdida Máxima", "Ganancia Máxima"], title="Pérdida y Ganancia Máxima")
st.plotly_chart(fig)

# Desplegar especificaciones de la operación
st.subheader("📊 Cantidad Cubierta")
st.write(especificaciones)

st.subheader("📊 Orden de Compra Generada")
st.write(f"Cantidad a cubrir: {toneladas_cubrir} toneladas en {mes_cobertura}")
st.write(f"Costo Total de la Cobertura: ${costo_total:,.2f} USD")
st.write("Estado de la Orden: Confirmada")

