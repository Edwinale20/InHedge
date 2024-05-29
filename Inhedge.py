# Paso 1: Importar las librerías necesarias
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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

# Paso 3: Cargar los precios históricos del aluminio (LME)
precios_aluminio = pd.read_csv("inhedge.csv")
precios_aluminio['Fecha'] = pd.to_datetime(precios_aluminio['Fecha'])

# Convertir las columnas de precios a numéricas, manejando los valores no numéricos o faltantes
precios_aluminio['LME Precio'] = pd.to_numeric(precios_aluminio['LME Precio'], errors='coerce')
precios_aluminio['Tipo de cambio'] = pd.to_numeric(precios_aluminio['Tipo de cambio'], errors='coerce')

precios_2023 = precios_aluminio[precios_aluminio['Fecha'].dt.year == 2023]

# Filtrar los precios del mes seleccionado
mes_index = meses.index(mes_seleccionado) + 1
precios_mes = precios_2023[precios_2023['Fecha'].dt.month == mes_index]

# Obtener el precio del quinto día del mes
precio_quinto_dia = precios_mes.iloc[4] if len(precios_mes) > 4 else precios_mes.iloc[-1]
precio_lme = precio_quinto_dia['LME Precio']
tipo_cambio = precio_quinto_dia['Tipo de cambio']
fecha_quinto_dia = precio_quinto_dia['Fecha'].strftime('%Y-%m-%d')

# Mostrar una tabla con los precios de aluminio en el mes seleccionado
st.subheader(f"📅 Precio del Aluminio en {mes_seleccionado} 2023 (Quinto día del mes)")
st.write(f"Fecha: {fecha_quinto_dia}")
st.write(f"Precio LME: ${precio_lme:,.2f} USD")
st.write(f"Tipo de Cambio: ${tipo_cambio:,.2f} MXN/USD")

# Paso 4: Definir la fórmula de cobertura con collar
def calcular_cobertura(toneladas, precio_lme, tipo_cambio, precio_ejercicio_compra, precio_ejercicio_venta, prima_compra, prima_venta, precios_spot):
    contratos = toneladas / 25
    costo_cobertura = contratos * (prima_compra - prima_venta) * tipo_cambio
    resultados = []
    for spot in precios_spot:
        perdida_maxima = max((spot - precio_ejercicio_venta) * toneladas - costo_cobertura, -costo_cobertura)
        ganancia_maxima = max((precio_ejercicio_compra - spot) * toneladas - costo_cobertura, -costo_cobertura)
        resultados.append((spot, perdida_maxima, ganancia_maxima))
    return costo_cobertura, contratos, resultados

# Paso 5: Calcular la cobertura para el mes seleccionado
if st.button('Simular Estrategia'):
    if toneladas_a_cubrir > 0:
        precio_ejercicio_compra = precio_lme * 1.05
        precio_ejercicio_venta = precio_lme * 0.95
        prima_compra = 1000
        prima_venta = 500
        precios_spot = [2000, 2050, 2100, 2150, 2200, 2250, 2300, 2350, 2400, 2450, 2500, 2550]
        costo_cobertura, contratos, resultados = calcular_cobertura(toneladas_a_cubrir, precio_lme, tipo_cambio, precio_ejercicio_compra, precio_ejercicio_venta, prima_compra, prima_venta, precios_spot)
        
        # Crear un dataframe con los resultados
        df_resultados = pd.DataFrame(resultados, columns=["Precio Spot", "Pérdida Máxima", "Ganancia Máxima"])
        df_resultados["Precio Strike"] = precio_ejercicio_compra
        df_resultados["Ganancia sin cobertura"] = (df_resultados["Precio Spot"] - precio_ejercicio_compra) * toneladas_a_cubrir
        df_resultados["Resultado LME"] = df_resultados["Ganancia sin cobertura"] - costo_cobertura
        df_resultados["Ganancia con cobertura"] = df_resultados["Ganancia sin cobertura"] + df_resultados["Resultado LME"]
        
        st.subheader("📊 Resultados de la Cobertura")
        st.dataframe(df_resultados)
        
        # Paso 6: Crear gráficos de resultados
        # Gráfico de barras de Pérdida y Ganancia Máxima
        fig_bar = go.Figure(data=[
            go.Bar(name='Pérdida Máxima', x=df_resultados["Precio Spot"], y=df_resultados["Pérdida Máxima"]),
            go.Bar(name='Ganancia Máxima', x=df_resultados["Precio Spot"], y=df_resultados["Ganancia Máxima"])
        ])
        fig_bar.update_layout(barmode='group', title="Pérdida y Ganancia Máxima por Precio Spot", xaxis_title="Precio Spot", yaxis_title="USD")
        st.plotly_chart(fig_bar, use_container_width=True)
        
        # Gráfico de líneas de Resultados LME y Ganancia con Cobertura
        fig_line = px.line(df_resultados, x="Precio Spot", y=["Resultado LME", "Ganancia con cobertura"], title="Resultados de LME y Ganancia con Cobertura", labels={"value": "USD", "Precio Spot": "Precio Spot"})
        st.plotly_chart(fig_line, use_container_width=True)
        
        # Calcular la cantidad de dólares y pesos cubiertos
        dolares_cubiertos = contratos * precio_ejercicio_compra
        cubiertos_pesos = dolares_cubiertos * tipo_cambio
        
        # Mostrar la cantidad de dólares y pesos cubiertos
        st.subheader("📉 Cantidad Cubierta")
        st.write(f"**Dólares cubiertos:** ${dolares_cubiertos:,.2f} USD")
        st.write(f"**Cantidad cubierta en pesos:** ${cubiertos_pesos:,.2f} MXN")
        
        # Mostrar la fecha de compra y el precio promedio del día
        st.write(f"**Fecha de compra:** {fecha_quinto_dia}")
        st.write(f"**Precio promedio del día:** ${precio_lme:,.2f} USD")
        
        # Paso 7: Simulación de una orden de compra
        st.write("### Orden de Compra Generada")
        st.write("**Cantidad a cubrir:**")
        st.write(f"{toneladas_a_cubrir} toneladas en {mes_seleccionado}")
        st.write("**Costo Total de la Cobertura:**")
        st.write(f"${costo_cobertura:,.2f} USD")
        st.write("**Estado de la Orden:** Confirmada")

# Fin del código

