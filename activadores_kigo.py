import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from google.cloud import bigquery
from google.oauth2 import service_account


st.set_page_config(
    page_title="Kigo - Activadores",
    layout="wide"
)

# Create API client.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials=credentials)

def usuarios_activador(Qr):
    activadores = f"""
    SELECT EXTRACT(DATE FROM timestamp) AS fecha, COUNT(distinct Number) AS usuarios
    FROM parkimovil-app.geosek_guest.autoregistro 
    WHERE qr = '{Qr}'
    GROUP BY EXTRACT(DATE FROM timestamp)
    ORDER BY fecha
    """

    df_usuarios_activador = client.query(activadores).to_dataframe()
    return df_usuarios_activador

qr_activadores = ['EZU[', 'EZU(', 'EZU{', 'EZUJ']
qr_seleccionada = st.selectbox('Selecciona un QR:', qr_activadores)

df_qr_activadores = usuarios_activador(qr_seleccionada)

def operaciones_activador(Qr):
    operaciones = f"""
    SELECT EXTRACT(DATE FROM timestamp) AS fecha, COUNT(*) AS operaciones
    FROM parkimovil-app.geosek_guest.autoregistro 
    WHERE qr = '{Qr}'
    GROUP BY EXTRACT(DATE FROM timestamp)
    ORDER BY fecha
    """
    df_operaciones_activador = client.query(operaciones).to_dataframe()
    return df_operaciones_activador

df_operaciones_activador = operaciones_activador(qr_seleccionada)

if qr_seleccionada == 'EZU[':
    titulo = 'Pueblo Serena'
elif qr_seleccionada == 'EZU(':
    titulo = 'Punto Valle'
elif qr_seleccionada == 'EZU{':
    titulo = 'Arboleda'
elif qr_seleccionada == 'EZUJ':
    titulo = 'Solesta'
else:
    titulo = ' '


fig_usuarios = go.Figure()

fig_usuarios.add_trace(go.Bar(
    x=df_qr_activadores['fecha'],
    y=df_qr_activadores['usuarios'],
    name='Usuarios por Activador'
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
    name='Operaciones por Activador'
))

fig_operaciones.update_layout(
    title= 'Operacones' + ' ' + titulo,
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
    title={'text': "Usuarios Diferentes", 'font': {'color': "black"}, 'align': 'center'}
))
fig_operaciones_indicador.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",  # Fondo transparente
    plot_bgcolor="rgba(0,0,0,0)",  # Fondo transparente
    margin=dict(l=20, r=20, t=20, b=20),  # Márgenes ajustados
    height=100,  # Altura ajustada
    width=200,  # Ancho ajustado
    font=dict(color="black"),  # Color del texto
)

# Ajustar bordes redondeados y color del borde
fig_operaciones_indicador.update_traces(title_font=dict(size=14))
fig_operaciones_indicador.update_traces(gauge=dict(axis=dict(tickcolor="black", tick0=2)))


st.title(titulo)

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig_usuarios_indicador, use_container_width=True)

with col2:
    st.plotly_chart(fig_operaciones_indicador, use_container_width=True)

st.plotly_chart(fig_usuarios, use_container_width=True)
st.plotly_chart(fig_operaciones, use_container_width=True)