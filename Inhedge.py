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

# Mostrar precios filtrados para depuración
st.write("Precios del mes seleccionado:", precios_mes)

# Verificar que el archivo tenga suficientes datos
if len(precios_mes) < 5:
    st.error("El archivo CSV no tiene suficientes datos para el mes seleccionado.")
else:
    # Obtener el precio promedio del quinto día del mes
    precio_lme = precios_mes.iloc[4]['LME Precio']
    tipo_cambio = precios_mes.iloc[4]['Tipo de cambio']
    precio_cme = precios_mes.iloc[4]['dolares cme']

    # Calcular la cantidad de contratos y costos
    contratos = monto_inversion / 25  # Cada contrato cubre 25 toneladas
    costo_total_mensual = contratos * precio_lme * 25  # Costo mensual
    costo_total_anual = costo_total_mensual * 12  # Costo anual

    # Calcular cantidad cubierta en dólares y pesos
    dolares_cubiertos = contratos * precio_lme * 25
    cubiertos_pesos = dolares_cubiertos * tipo_cambio

    # Mostrar valores intermedios para depuración
    st.write(f"Contratos: {contratos}")
    st.write(f"Costo total mensual: {costo_total_mensual}")
    st.write(f"Dólares cubiertos: {dolares_cubiertos}")
    st.write(f"Pesos cubiertos: {cubiertos_pesos}")

    # Generar la orden de compra de divisas si es un mes múltiplo de 3
    contratos_fx = 0
    costo_total_fx = 0
    if int(mes_seleccionado.split('-')[1]) % 3 == 0:
        contratos_fx = int(cubiertos_pesos / 2 / 500000)  # Cada contrato de FX cubre 500,000 pesos
        costo_total_fx = contratos_fx * 500000

    # Mostrar valores de FX para depuración
    st.write(f"Contratos FX: {contratos_fx}")
    st.write(f"Costo total FX: {costo_total_fx}")

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

    # Crear DataFrame para resultados de la cobertura de aluminio
    resultados = []
    for i in range(10):
        spot = precio_lme + (i - 5) * 50  # Ajustar el precio spot para generar diferentes escenarios
        perdida_max = max(0, precio_lme - spot) * contratos * 25  # Pérdida máxima
        ganancia_max = max(0, spot - precio_lme) * contratos * 25  # Ganancia máxima
        ganancia_sin_cobertura = (spot - precio_lme) * contratos * 25  # Ganancia sin cobertura
        resultado_lme = ganancia_sin_cobertura - perdida_max  # Resultado de la operación
        ganancia_con_cobertura = resultado_lme + ganancia_max - perdida_max  # Ganancia con cobertura
        resultados.append([spot, perdida_max, ganancia_max, precio_lme, ganancia_sin_cobertura, resultado_lme, ganancia_con_cobertura])

    df_resultados = pd.DataFrame(resultados, columns=['Precio Spot', 'Pérdida Máxima', 'Ganancia Máxima', 'Precio Strike', 'Ganancia sin cobertura', 'Resultado LME', 'Ganancia con cobertura'])

    st.subheader("Resultados de la Cobertura de Aluminio")
    st.table(df_resultados)

    # Gráfica de Pérdida y Ganancia Máxima
    df_grafica = df_resultados[['Pérdida Máxima', 'Ganancia Máxima']].melt(var_name='variable', value_name='value')
    fig = px.bar(df_grafica, x=df_grafica.index, y='value', color='variable', barmode='group', title="Pérdida y Ganancia Máxima")
    st.plotly_chart(fig, use_container_width=True)

    # Crear DataFrame para resultados de la cobertura de divisas
    resultados_fx = []
    if contratos_fx > 0:
        for i in range(10):
            spot_fx = precio_cme + (i - 5) * 0.5  # Ajustar el precio spot de divisas para generar diferentes escenarios
            perdida_max_fx = max(0, precio_cme - spot_fx) * contratos_fx * 500000  # Pérdida máxima
            ganancia_max_fx = max(0, spot_fx - precio_cme) * contratos_fx * 500000  # Ganancia máxima
            ganancia_sin_cobertura_fx = (spot_fx - precio_cme) * contratos_fx * 500000  # Ganancia sin cobertura
            resultado_cme = ganancia_sin_cobertura_fx - perdida_max_fx  # Resultado de la operación
            ganancia_con_cobertura_fx = resultado_cme + ganancia_max_fx - perdida_max_fx  # Ganancia con cobertura
            resultados_fx.append([spot_fx, perdida_max_fx, ganancia_max_fx, precio_cme, ganancia_sin_cobertura_fx, resultado_cme, ganancia_con_cobertura_fx])

    df_resultados_fx = pd.DataFrame(resultados_fx, columns=['Precio Spot FX', 'Pérdida Máxima FX', 'Ganancia Máxima FX', 'Precio Strike FX', 'Ganancia sin cobertura FX', 'Resultado CME', 'Ganancia con cobertura FX'])

    st.subheader("Resultados de la Cobertura de Divisas")
    st.table(df_resultados_fx)

    # Gráfica de Pérdida y Ganancia Máxima de Divisas
    df_grafica_fx = df_resultados_fx[['Pérdida Máxima FX', 'Ganancia Máxima FX']].melt(var_name='variable', value_name='value')
    fig_fx = px.bar(df_grafica_fx, x=df_grafica_fx.index, y='value', color='variable', barmode='group', title="Pérdida y Ganancia Máxima de Divisas")
    st.plotly_chart(fig_fx, use_container_width=True)

    # Cargar la animación Lottie adicional
    lottie_tarjeta = load_lottiefile("tarjeta.json")

    # Mostrar la animación Lottie adicional en el centro de la página usando columnas
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st_lottie(lottie_tarjeta, key='tarjeta', height=300, width=300)

    # Explicación del funcionamiento de la cobertura:
    st.write("""
    ### Explicación del Funcionamiento de la Cobertura

    1. **Selección de Mes y Cantidad a Cubrir:**
       - El usuario selecciona el mes y la cantidad de toneladas de aluminio que desea cubrir.

    2. **Cálculo de Contratos y Costos:**
       - Se calcula la cantidad de contratos necesarios, dado que cada contrato de aluminio cubre 25 toneladas.
       - Se calcula el costo total mensual y anual basado en el precio promedio del quinto día del mes seleccionado.

    3. **Cobertura de Divisas (Si Aplica):**
       - Si el mes seleccionado es múltiplo de 3, se genera una orden de compra de divisas para cubrir la mitad de la cantidad cubierta en pesos.
       - Cada contrato de divisas cubre 500,000 pesos.

    4. **Resultados de la Cobertura:**
       - Se generan escenarios de precios spot para evaluar la pérdida y ganancia máxima, así como la ganancia sin cobertura, el resultado de la operación, y la ganancia con cobertura.

    5. **Visualización de Resultados:**
       - Se muestra una tabla con los resultados de la cobertura y una gráfica de barras comparando la pérdida y ganancia máxima.
       - Además, se muestra una tabla y gráfica de la cobertura de divisas, si aplica.
    """)
