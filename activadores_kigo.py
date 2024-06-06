import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from google.cloud import bigquery
from google.oauth2 import service_account
import plotly.express as px



st.set_page_config(
    page_title="Kigo - Activadores",
    layout="wide"
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.write()

with col2:
    st.image('https://main.d1jmfkauesmhyk.amplifyapp.com/img/logos/logos.png')

with col3:
    st.title('Kigo Analítica')

with col4:
    st.write()

# Create API client.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials=credentials)

def usuarios_activador(Qr):
    activadores = f"""
    SELECT EXTRACT(DATE FROM TIMESTAMP_ADD(timestamp, INTERVAL -6 HOUR)) AS fecha, COUNT(distinct Number) AS usuarios
    FROM parkimovil-app.geosek_guest.autoregistro 
    WHERE qr = '{Qr}'
    GROUP BY EXTRACT(DATE FROM TIMESTAMP_ADD(timestamp, INTERVAL -6 HOUR))  
    ORDER BY fecha
    """

    df_usuarios_activador = client.query(activadores).to_dataframe()
    return df_usuarios_activador

qr_activadores = ['EZU[', 'EZU(', 'EZU{', 'EZUJ']
qr_seleccionada = st.selectbox('Selecciona un QR:', qr_activadores)

df_qr_activadores = usuarios_activador(qr_seleccionada)

@st.cache_data(ttl=3600)
def operaciones_activador(Qr):
    operaciones = f"""
    SELECT EXTRACT(DATE FROM TIMESTAMP_ADD(timestamp, INTERVAL -6 HOUR)) AS fecha, COUNT(*) AS operaciones
    FROM parkimovil-app.geosek_guest.autoregistro 
    WHERE qr = '{Qr}'
    GROUP BY EXTRACT(DATE FROM TIMESTAMP_ADD(timestamp, INTERVAL -6 HOUR)) 
    ORDER BY fecha
    """
    df_operaciones_activador = client.query(operaciones).to_dataframe()
    return df_operaciones_activador

df_operaciones_activador = operaciones_activador(qr_seleccionada)

@st.cache_data(ttl=3600)
def registro_activador(Qr):
    registro = f"""
    SELECT TIMESTAMP_ADD(A.timestamp, INTERVAL -6 HOUR) AS fecha, A.QR, P.alias AS plaza, A.nombre, A.number AS telefono
    FROM parkimovil-app.geosek_guest.autoregistro A
    JOIN parkimovil-app.geosek_guest.plazas P
        ON  A.plaza = P.codigo
    WHERE A.qr = '{Qr}'
    ORDER BY fecha DESC
    """

    df_registro_activador = client.query(registro).to_dataframe()
    return df_registro_activador

df_registro_activador = registro_activador(qr_seleccionada)

if qr_seleccionada == 'EZU[':
    titulo = 'Pueblo Serena'
elif qr_seleccionada == 'EZU{':
    titulo = 'Punto Valle'
elif qr_seleccionada == 'EZU(':
    titulo = 'Arboleda'
elif qr_seleccionada == 'EZUJ':
    titulo = 'Solesta'
else:
    titulo = ' '


fig_usuarios = go.Figure()

fig_usuarios.add_trace(go.Bar(
    x=df_qr_activadores['fecha'],
    y=df_qr_activadores['usuarios'],
    name='Usuarios por Activador',
    marker_color='#F24405'
))

fig_usuarios.update_layout(
    title= 'Usuarios' + ' ' + titulo,
    xaxis_title='Fecha',
    yaxis_title='Usuarios'
)

fig_operaciones = go.Figure()

fig_operaciones.add_trace(go.Bar(
    x=df_operaciones_activador['fecha'],
    y=df_operaciones_activador['operaciones'],
    name='Operaciones por Activador',
    marker_color='#030140'
))

fig_operaciones.update_layout(
    title= 'Operaciones' + ' ' + titulo,
    xaxis_title='Fecha',
    yaxis_title='Usuarios'
)

fig_usuarios_indicador = go.Figure(go.Indicator(
    mode="number",
    value=df_qr_activadores['usuarios'].sum(),
    domain={'x': [0, 1], 'y': [0, 1]},
    title={'text': "Usuarios Diferentes", 'font': {'color': "black"}, 'align': 'center'}
))
fig_usuarios_indicador.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",  # Fondo transparente
    plot_bgcolor="rgba(0,0,0,0)",  # Fondo transparente
    margin=dict(l=20, r=20, t=20, b=20),  # Márgenes ajustados
    height=100,  # Altura ajustada
    width=200,  # Ancho ajustado
    font=dict(color="black"),  # Color del texto
)

# Ajustar bordes redondeados y color del borde
fig_usuarios_indicador.update_traces(title_font=dict(size=14))
fig_usuarios_indicador.update_traces(gauge=dict(axis=dict(tickcolor="black", tick0=2)))

fig_operaciones_indicador = go.Figure(go.Indicator(
    mode="number",
    value=df_operaciones_activador['operaciones'].sum(),
    domain={'x': [0, 1], 'y': [0, 1]},
    title={'text': "Operaciones", 'font': {'color': "black"}, 'align': 'center'}
))
fig_operaciones_indicador.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",  # Fondo transparente
    plot_bgcolor="rgba(0,0,0,0)",  # Fondo transparente
    margin=dict(l=20, r=20, t=20, b=20),  # Márgenes ajustados
    height=100,  # Altura ajustada
    width=200,  # Ancho ajustado
    font=dict(color="black"),  # Color del texto
)
fig_operaciones_indicador.update_traces(title_font=dict(size=14))
fig_operaciones_indicador.update_traces(gauge=dict(axis=dict(tickcolor="black", tick0=2)))

#heatmap
df_registro_activador['hour'] = df_registro_activador['fecha'].dt.hour
df_registro_activador['day_of_week'] = df_registro_activador['fecha'].dt.day_name()

# Pivot
heatmap_data = df_registro_activador.pivot_table(
    index='day_of_week',
    columns='hour',
    aggfunc='size',
    fill_value=0
)

# Asegurar el orden de los dias
days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
heatmap_data = heatmap_data.reindex(days_order)

#Escala de Colores de Gradiente
color_scale = [
    [0.0, '#FFFFFF'],  # Blanco
    [1.0, '#F24405']   # #Naranja Kigo
]

# Creacion del heatmap
fig_heatmap = px.imshow(
    heatmap_data,
    labels=dict(x="Horas del Día", y="Día de la Semana", color="Count"),
    x=heatmap_data.columns,
    y=heatmap_data.index,
    title="Mapa de Calor de horas de Uso en los días de la semana",
    color_continuous_scale=color_scale
)



st.title(titulo)

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig_usuarios_indicador, use_container_width=True)

with col2:
    st.plotly_chart(fig_operaciones_indicador, use_container_width=True)

col3, col4 = st.columns(2)
with col3:
    st.plotly_chart(fig_usuarios, use_container_width=True)
with col4:
    st.plotly_chart(fig_operaciones, use_container_width=True)

st.write(df_registro_activador)
st.plotly_chart(fig_heatmap, use_container_width=True)