import streamlit as st
import pandas as pd
import requests
import time

# URL de tu servidor en Render
SERVER_URL = "https://serverfire-1.onrender.com/ultimos"

st.set_page_config(page_title="Panel IoT ESP32", page_icon="🌡️", layout="wide")

st.title("🌡️ Panel de Monitoreo IoT - ESP32 con Sensor de Humo MQ-7")
st.caption("Datos recibidos en tiempo real desde Flask (Render)")

# Contenedor principal
placeholder = st.empty()

def obtener_datos():
    try:
        response = requests.get(SERVER_URL, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                df = pd.DataFrame(data)
                df["temperatura"] = df["temperatura"].astype(float)
                df["humedad"] = df["humedad"].astype(float)
                df["humo_detectado"] = df["humo_detectado"].astype(int)
                return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error al conectar con el servidor: {e}")
        return pd.DataFrame()

# Actualización automática cada 10 segundos
while True:
    df = obtener_datos()
    if not df.empty:
        with placeholder.container():
            col1, col2, col3 = st.columns(3)
            col1.metric("Temperatura actual (°C)", f"{df['temperatura'].iloc[-1]:.1f}")
            col2.metric("Humedad (%)", f"{df['humedad'].iloc[-1]:.1f}")
            estado = "🔥 Humo detectado" if df['humo_detectado'].iloc[-1] == 1 else "✅ Aire limpio"
            col3.metric("Estado", estado)

            st.subheader("📈 Gráficas en tiempo real")
            st.line_chart(df[["temperatura", "humedad"]])

            st.subheader("📋 Últimos registros")
            st.dataframe(df.tail(10))
    else:
        st.warning("Sin datos aún... esperando lecturas de la ESP32.")

    time.sleep(10)
