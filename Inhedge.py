import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_lottie import st_lottie

# Configuración de la página
st.set_page_config(page_title="📊 InHedge - Estrategias de Cobertura", page_icon="📊", layout="wide")

# Función para cargar la animación Lottie desde un archivo JSON
@st.cache_data
def load_lottiefile(filepath: str):
    import json
    with open(filepath, "r") as f:
        return json.load(f)

# Cargar la animación Lottie
lottie_animation = load_lottiefile("inhedge.json")

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
    monto_inversion = st.number_input("💲 Cantidad a cubrir de Aluminio (toneladas):", min_value=0, step=1, key="inversion")
    enfoque_inversion = st.selectbox("📝 Selecciona el mes de cobertura:", [f"2023-{i:02d}" for i in range(1, 13)])

# Guardar los valores de entrada en session_state para su uso en otros lugares del script
st.session_state['monto_inversion'] = monto_inversion
st.session_state['enfoque_inversion'] = enfoque_inversion

# Cargar datos del CSV
precios = pd.read_csv('inhedge.csv', parse_dates=['Fecha'])

# Filtrar precios para el mes seleccionado
mes_seleccionado = st.session_state['enfoque_inversion']
precios_mes = precios[(precios['Fecha'].dt.strftime('%Y-%m') == mes_seleccionado)]

# Obtener el precio promedio del quinto día del mes
precio_lme = precios_mes.iloc[4]['LME Precio']
tipo_cambio = precios_mes.iloc[4]['Tipo de cambio']
precio_cme = precios_mes.iloc[4]['dolares cme']

# Calcular la cantidad de contratos y costos
contratos = monto_inversion / 25
costo_total_mensual = contratos * precio_lme * 25
costo_total_anual = costo_total_mensual * 12

# Calcular cantidad cubierta en dólares y pesos
dolares_cubiertos = contratos * precio_lme * 25
cubiertos_pesos = dolares_cubiertos * tipo_cambio

# Generar la orden de compra de divisas si es un mes múltiplo de 3
if int(mes_seleccionado.split('-')[1]) % 3 == 0:
    contratos_fx = (cubiertos_pesos / 2) // 500000
    costo_total_fx = contratos_fx * 500000
    st.write(f"Contratos FX: {contratos_fx}, Costo total FX: {costo_total_fx}")

# Mostrar información de la operación
st.subheader("Cantidad Cubierta")
st.write(f"Dólares cubiertos: ${dolares_cubiertos:.2f} USD")
st.write(f"Cantidad cubierta en pesos: ${cubiertos_pesos:.2f} MXN")
st.write(f"Fecha de compra: {precios_mes.iloc[4]['Fecha'].strftime('%Y-%m-%d')}")
st.write(f"Precio promedio del día: ${precio_lme:.2f} USD")

# Crear DataFrame para la orden de compra
orden_compra = {
    'Cantidad a cubrir': [f"{monto_inversion} toneladas en {mes_seleccionado}"],
    'Costo Total de la Cobertura': [f"${costo_total_mensual:.2f} USD"],
    'Estado de la Orden': ['Confirmada']
}
df_orden = pd.DataFrame(orden_compra)

st.subheader("Orden de Compra Generada")
st.table(df_orden)

# Crear DataFrame para resultados de la cobertura
resultados = []
for i in range(10):
    spot = precio_lme + (i - 5) * 50
    perdida_max = max(0, precio_lme - spot) * contratos * 25
    ganancia_max = max(0, spot - precio_lme) * contratos * 25
    ganancia_sin_cobertura = (spot - precio_lme) * contratos * 25
    resultado_lme = ganancia_sin_cobertura - perdida_max
    ganancia_con_cobertura = resultado_lme + ganancia_max - perdida_max
    resultados.append([spot, perdida_max, ganancia_max, precio_lme, ganancia_sin_cobertura, resultado_lme, ganancia_con_cobertura])

df_resultados = pd.DataFrame(resultados, columns=['Precio Spot', 'Pérdida Máxima', 'Ganancia Máxima', 'Precio Strike', 'Ganancia sin cobertura', 'Resultado LME', 'Ganancia con cobertura'])

st.subheader("Resultados de la Cobertura Actualizada con FX")
st.table(df_resultados)

# Gráfica de Pérdida y Ganancia Máxima
df_grafica = df_resultados[['Pérdida Máxima', 'Ganancia Máxima']].melt(var_name='variable', value_name='value')
fig = px.bar(df_grafica, x=df_grafica.index, y='value', color='variable', barmode='group', title="Pérdida y Ganancia Máxima")
st.plotly_chart(fig, use_container_width=True)

