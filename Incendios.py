import streamlit as st
import requests
import pandas as pd
import time

# ---------------- CONFIGURACIÓN ----------------
SERVER_URL = "https://serverfire-1.onrender.com/ultimos"

st.set_page_config(page_title="Detección de Humo IoT", page_icon="🔥", layout="wide")

# Estilo oscuro elegante
st.markdown("""
    <style>
    body {
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        color: white;
    }
    .stApp {
        background-color: transparent;
    }
    .titulo {
        font-size: 42px !important;
        font-weight: bold;
        color: #ff5757;
        text-align: center;
        margin-bottom: 10px;
    }
    .estado {
        font-size: 38px !important;
        font-weight: bold;
        text-align: center;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 0 25px rgba(255,255,255,0.1);
    }
    .alerta {
        background-color: rgba(255, 87, 87, 0.15);
        color: #ff4b4b;
    }
    .ok {
        background-color: rgba(87, 255, 135, 0.15);
        color: #4bff72;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='titulo'>🔥 Sistema de Detección de Humo - ESP32 + MQ-7</h1>", unsafe_allow_html=True)
st.caption("Monitoreo IoT en tiempo real desde servidor Flask (Render)")

# ---------------- FUNCIÓN PARA LEER DATOS ----------------
def obtener_datos():
    try:
        response = requests.get(SERVER_URL, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                df = pd.DataFrame(data)
                df["humo_detectado"] = df["humo_detectado"].astype(int)
                return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error al conectar con el servidor: {e}")
        return pd.DataFrame()

# ---------------- CONTENEDOR PRINCIPAL ----------------
placeholder = st.empty()

# ---------------- LOOP DE MONITOREO ----------------
while True:
    df = obtener_datos()
    if not df.empty:
        humo = df["humo_detectado"].iloc[-1]
        with placeholder.container():
            if humo == 1:
                st.markdown("<div class='estado alerta'>🚨 ¡Humo detectado! Riesgo de incendio</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='estado ok'>✅ Aire limpio y seguro</div>", unsafe_allow_html=True)
        time.sleep(5)
        placeholder.empty()
    else:
        st.warning("Sin datos aún... esperando lecturas de la ESP32.")
        time.sleep(5)

