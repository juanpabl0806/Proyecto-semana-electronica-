import streamlit as st
import pandas as pd
import requests

st.title("🔥 Sistema de Alerta Temprana IoT")

# Leer datos desde la API Flask
response = requests.get("http://TU_SERVIDOR_IP:5000/lecturas")
data = response.json()
df = pd.DataFrame(data)

# Mostrar datos
st.line_chart(df[["temperature", "gas"]])

# Detección de alerta
if df["temperature"].iloc[-1] > 60 or df["gas"].iloc[-1] > 400:
    st.error("🚨 ¡ALERTA! Posible incendio detectado")
else:
    st.success("✅ Sistema estable")
