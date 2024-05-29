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
#center_logo {
    display: flex;
    justify-content: center;
    align-items: center;
}
</style>
<h1>📊 InHedge - Estrategias de Cobertura 📊</h1>
""", unsafe_allow_html=True)

# Mostrar la animación Lottie en el centro de la página usando div
st.markdown('<div id="center_logo">', unsafe_allow_html=True)
st_lottie(lottie_animation, key='hedge_logo', height=300, width=300)
st.markdown('</div>', unsafe_allow_html=True)

# Paso 2: Crear un formulario centrado en la página principal para recoger información del usuario
st.header("📈 Visualización de Estrategias de Cobertura")
col1, col2, col3 = st.columns([1, 1, 1])

with col2:  # Usar la columna central para los inputs
    monto_inversion = st.number_input("💲 Cantidad a invertir inicialmente:", min_value=0, step=1000, key="inversion")
    monto_aportacion = st.number_input("📆 ¿De cuánto serán tus aportaciones mensuales?", min_value=0, step=100, key="aportacion")
    enfoque_inversion = st.selectbox("📝 ¿Cuál es tu objetivo de cobertura?", ["Commodity", "Divisa", "Ambos"])

# Guardar los valores de entrada en session_state para su uso en otros lugares del script
st.session_state['monto_inversion'] = monto_inversion
st.session_state['monto_aportacion'] = monto_aportacion

# Paso 3: Definir estrategias de cobertura
st.header("📊 Estrategias de Cobertura")
estrategias = {
    "Long Call": "Compra de una opción de compra para protegerse contra aumentos de precio.",
    "Collar": "Combina la compra de una opción de venta y la venta de una opción de compra para limitar pérdidas y ganancias.",
    "Futuro": "Contrato para comprar o vender un activo en una fecha futura a un precio acordado.",
    "Straddle": "Compra simultánea de una opción de compra y una opción de venta con el mismo precio de ejercicio y fecha de vencimiento."
}

# Seleccionar estrategia
estrategia_seleccionada = st.selectbox("🛡️ Selecciona una estrategia de cobertura:", list(estrategias.keys()))
st.write(f"**Descripción de la estrategia:** {estrategias[estrategia_seleccionada]}")

# Espacio para dos animaciones Lottie adicionales
st.subheader("Animaciones de Estrategias de Cobertura")
st.write("A continuación, podrás ver dos animaciones que ilustran nuestras estrategias de cobertura:")

# Cargar y mostrar la primera animación Lottie adicional
lottie_animation_1 = load_lottiefile("animacion1.json")  # Asegúrate de tener un archivo Lottie JSON válido
st_lottie(lottie_animation_1, key='strategy1', height=200, width=200)

# Cargar y mostrar la segunda animación Lottie adicional
lottie_animation_2 = load_lottiefile("animacion2.json")  # Asegúrate de tener un archivo Lottie JSON válido
st_lottie(lottie_animation_2, key='strategy2', height=200, width=200)

# Paso 4: Simulación de la cobertura seleccionada
if st.button('Simular Estrategia'):
    # Asegurar que monto_inversion y monto_aportacion estén inicializados
    monto_inversion = st.session_state.get('monto_inversion', 0)
    monto_aportacion = st.session_state.get('monto_aportacion', 0)

    # Subpaso 1: Calcular la inversión total
    total_inversion = monto_inversion + monto_aportacion
    st.write(f'Esta es tu inversión hasta el momento: ${total_inversion}')

    # Subpaso 2: Crear un gráfico de pie con la distribución de la inversión en acciones
    acciones = ['AC.MX', 'GCARSOA1.MX', 'GRUMAB.MX', 'ALSEA.MX', 'GAPB.MX', 'ASURB.MX', 'VOO', 'SPY']
    pesos = [15.4, 5.00, 5.00, 5.00, 20.00, 12.1, 20.00, 17.5]  # Porcentajes como valores decimales
    inversion_por_accion = [total_inversion * peso / 100 for peso in pesos]
    fig_pie = px.pie(names=acciones, values=inversion_por_accion)
    st.write("## ➗ Distribución de tus inversiones")
    st.plotly_chart(fig_pie, use_container_width=True)

    # Subpaso 3: Gráfica de comparación de los últimos 10 años de nuestro portafolio con la inflación
    df = pd.read_csv('comparacion.csv')
    fig_line = px.line(df, x='Fecha', y=['Inflacion', 'InHedge'], labels={'value': 'Valor', 'variable': 'Índice'})
    st.write("## 💹 Comparación de Inversión InHedge vs Inflación")
    st.plotly_chart(fig_line, use_container_width=True)

    # Subpaso 4: Proyección de crecimiento de las aportaciones anuales
    aportacion_anual = monto_aportacion * 12  # Convertir aportación mensual a anual
    rendimiento_anual = 0.1389  # Tasa de rendimiento anual de 13.89%
    anos = list(range(2024, 2061))  # Años desde 2024 hasta 2060
    saldo = [aportacion_anual]  # Iniciar con la primera aportación anual
    for i in range(1, len(anos)):
        saldo_nuevo = saldo[-1] * (1 + rendimiento_anual) + aportacion_anual
        saldo.append(saldo_nuevo)  # Aplicar rendimiento y agregar nueva aportación anual

    fig_crecimiento = px.line(x=anos, y=saldo, labels={'x': 'Año', 'y': 'Monto Acumulado ($)'})
    fig_crecimiento.update_layout(title="Proyección del Crecimiento de las Aportaciones Anuales")
    st.write("## 📈 Proyección del Crecimiento de las Aportaciones Anuales")
    st.plotly_chart(fig_crecimiento, use_container_width=True)

    # Subpaso 5: Mostrar el monto final en 2060 en una tabla
    monto_final = saldo[-1]  # Último valor del saldo
    df_final = pd.DataFrame({'Año': [2060], 'Monto Acumulado ($)': [monto_final]})
    st.write("## 📈 Monto Acumulado en 2060")
    st.table(df_final)

# Subpaso 6: Simulación ajustada por volatilidad
def calcular_crecimiento_inversion(aportacion_anual, rendimiento_anual, volatilidad):
    anos = list(range(2024, 2061))
    saldo = [aportacion_anual]  # Iniciar con la primera aportación anual
    for _ in range(1, len(anos)):
        # Aplicar rendimiento ajustado por volatilidad y agregar nueva aportación
        saldo.append(saldo[-1] * (1 + rendimiento_anual - volatilidad) + aportacion_anual)
    return anos, saldo

with st.form("form_inversion"):
    rendimiento_anual = st.slider("Tasa de Rendimiento Anual (%)", min_value=0.0, max_value=20.0, value=14.81, step=0.01, key="rendimiento")
    volatilidad = st.slider("Volatilidad Anual (%)", min_value=0.0, max_value=30.0, value=3.36, step=0.01, key="volatilidad")
    aportacion_mensual = st.number_input("Aportación Mensual ($)", min_value=0, max_value=100000, step=100, value=1000)
    submitted = st.form_submit_button("Actualizar Inversión")

if submitted:
    aportacion_anual = aportacion_mensual * 12  # Convertir aportación mensual a anual
    anos, saldo = calcular_crecimiento_inversion(aportacion_anual, rendimiento_anual / 100, volatilidad / 100)

    fig = px.line(x=anos, y=saldo, labels={'x': 'Año', 'y': 'Monto Acumulado ($)'})
    fig.update_layout(title="Simulación del Crecimiento de la Inversión Ajustada por Volatilidad")
    st.plotly_chart(fig, use_container_width=True)

    st.write("## Detalles de la Inversión")
    st.write(f"- Volatilidad Anual: {volatilidad:.2f}%")
    st.write(f"- Rendimiento Anual: {rendimiento_anual:.2f}%")
    df_acciones = pd.DataFrame({'Acciones': acciones, 'Pesos (%)': pesos})
    st.write("### Distribución de Acciones y Pesos")
    st.table(df_acciones)


