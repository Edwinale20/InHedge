import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
lottie_animation = load_lottiefile("ora.json")  # Asegúrate de tener un archivo Lottie JSON válido en el mismo directorio

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

# Paso 2: Cargar y procesar datos del CSV
df = pd.read_csv('inhedge.csv', parse_dates=['Fecha'])

# Paso 3: Recoger la entrada del usuario
st.header("📈 Visualización de Estrategias de Cobertura")
col1, col2, col3 = st.columns([1, 1, 1])

with col2:
    monto_inversion = st.number_input("💲 Cantidad a cubrir de Aluminio (en toneladas):", min_value=0, step=25, key="inversion")
    mes_seleccionado = st.selectbox("📅 Selecciona el mes de cobertura:", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"])
    enfoque_inversion = st.selectbox("📝 ¿Cuál es tu objetivo de cobertura?", ["Commodity", "Divisa", "Ambos"])

# Asignar número del mes seleccionado
meses = {"Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4, "Mayo": 5, "Junio": 6, "Julio": 7, "Agosto": 8, "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12}
mes_num = meses[mes_seleccionado]

# Filtrar datos para el mes seleccionado y obtener el precio del quinto día
df_mes = df[df['Fecha'].dt.month == mes_num]
precio_quinto_dia = df_mes.iloc[4]['LME Precio']
tipo_cambio_quinto_dia = df_mes.iloc[4]['Tipo de cambio']

# Cálculos para la cobertura de aluminio
contratos = monto_inversion / 25
precio_strike = precio_quinto_dia
costo_total_cobertura = contratos * precio_strike

# Calcular dólares cubiertos y cantidad cubierta en pesos
dolares_cubiertos = contratos * precio_strike
cubiertos_pesos = dolares_cubiertos * tipo_cambio_quinto_dia

# Calcular el precio un mes después para la venta
df_mes_siguiente = df[df['Fecha'].dt.month == (mes_num % 12) + 1]
precio_venta = df_mes_siguiente.iloc[4]['LME Precio']

# Calcular los resultados de la cobertura
precio_spot = [precio_quinto_dia + i * 50 for i in range(-4, 6)]
resultados_cobertura = []

for spot in precio_spot:
    perdida_max = max(0, precio_strike - spot) * contratos * 25
    ganancia_max = max(0, spot - precio_strike) * contratos * 25
    ganancia_sin_cobertura = (spot - precio_venta) * contratos * 25
    resultado_lme = (precio_venta - spot) * contratos * 25
    ganancia_con_cobertura = ganancia_sin_cobertura + ganancia_max - perdida_max
    resultados_cobertura.append([spot, perdida_max, ganancia_max, precio_strike, ganancia_sin_cobertura, resultado_lme, ganancia_con_cobertura])

resultados_df = pd.DataFrame(resultados_cobertura, columns=["Precio Spot", "Pérdida Máxima", "Ganancia Máxima", "Precio Strike", "Ganancia sin cobertura", "Resultado LME", "Ganancia con cobertura"])

# Mostrar los resultados
st.subheader("📈 Resultados de la Cobertura de Aluminio")
st.write(f"Dólares cubiertos: ${dolares_cubiertos:,.2f} USD")
st.write(f"Cantidad cubierta en pesos: ${cubiertos_pesos:,.2f} MXN")
st.write(f"Fecha de compra: {df_mes.iloc[4]['Fecha'].date()}")
st.write(f"Precio promedio del día: ${precio_quinto_dia:,.2f} USD")

if mes_num % 3 == 0:
    contratos_fx = dolares_cubiertos / 500000
    costo_total_cobertura_fx = contratos_fx * 500000
    cubiertos_pesos_fx = dolares_cubiertos * tipo_cambio_quinto_dia

    # Añadir resultados de la cobertura del tipo de cambio
    st.write(f"Cobertura de tipo de cambio realizada en el mismo periodo.")
    st.write(f"Dólares CME cubiertos: {contratos_fx:.2f} contratos")
    st.write(f"Costo de Cobertura FX: ${costo_total_cobertura_fx:,.2f} USD")
    st.write(f"Cantidad cubierta en pesos por FX: ${cubiertos_pesos_fx:,.2f} MXN")

# Mostrar tabla de resultados
st.subheader("📊 Resultados de la Cobertura")
st.write(resultados_df)

# Gráfico de Pérdida y Ganancia Máxima
fig = go.Figure()
fig.add_trace(go.Bar(x=resultados_df["Precio Spot"], y=resultados_df["Pérdida Máxima"], name='Pérdida Máxima', marker_color='indianred'))
fig.add_trace(go.Bar(x=resultados_df["Precio Spot"], y=resultados_df["Ganancia Máxima"], name='Ganancia Máxima', marker_color='lightsalmon'))
fig.update_layout(barmode='group', title="Pérdida y Ganancia Máxima", xaxis_title="Precio Spot", yaxis_title="Valor")
st.plotly_chart(fig, use_container_width=True)

# Añadir resultados a la tabla con cobertura de tipo de cambio
if mes_num % 3 == 0:
    resultados_df["Dólares CME"] = contratos_fx
    resultados_df["Costo de Cobertura FX"] = costo_total_cobertura_fx
    resultados_df["Cubiertos en Pesos FX"] = cubiertos_pesos_fx

# Mostrar la tabla con los resultados actualizados
st.write("## Resultados de la Cobertura Actualizada con FX")
st.write(resultados_df)
