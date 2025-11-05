import streamlit as st
import requests
import pandas as pd
import time
from streamlit_lottie import st_lottie

# ==============================
# 🔥 CONFIGURACIÓN INICIAL
# ==============================
st.set_page_config(
    page_title="Sistema de Alerta IoT",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==============================
# 🎨 FUNCIÓN PARA CARGAR LOTTIE
# ==============================
def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# ==============================
# 🌈 ENCABEZADO Y DISEÑO
# ==============================
col1, col2 = st.columns([1, 2])

with col1:
    lottie = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_tfb3estd.json")
    if lottie:
        st_lottie(lottie, height=200, key="alerta")

with col2:
    st.markdown(
        """
        <h1 style='font-size: 42px; color: #ff4b4b;'>Sistema de Alerta Temprana IoT 🔥</h1>
        <p style='font-size: 18px; color: #555;'>Monitoreo en tiempo real de gases inflamables con ESP32 y servidor Flask en Render</p>
        """,
        unsafe_allow_html=True
    )

st.divider()

# ==============================
# 🌍 CONFIGURACIÓN DEL SERVIDOR
# ==============================
URL_BASE = "https://serverfire-1.onrender.com"

st.subheader("📡 Estado de conexión con el servidor")

try:
    resp = requests.get(f"{URL_BASE}/lecturas", timeout=5)
    if resp.status_code == 200:
        st.success("✅ Conectado correctamente con el servidor Render")
    else:
        st.warning("⚠️ Servidor accesible, pero no devolvió datos válidos")
except Exception as e:
    st.error(f"❌ Error al conectar con el servidor: {e}")

st.divider()

# ==============================
# 📊 MONITOREO EN TIEMPO REAL
# ==============================
st.subheader("📈 Monitoreo en tiempo real de lecturas del sensor de gas")

placeholder = st.empty()

refresh_rate = st.slider("⏱️ Intervalo de actualización (segundos)", 2, 20, 5)

st.info("El sistema actualizará los datos automáticamente según el intervalo seleccionado.")

# Bucle de actualización en tiempo real
while True:
    try:
        resp = requests.get(f"{URL_BASE}/lecturas", timeout=5)
        if resp.status_code == 200:
            lecturas = resp.json()
            
            if isinstance(lecturas, list) and len(lecturas) > 0:
                df = pd.DataFrame(lecturas)
                
                # Normalizar nombres de columnas esperadas
                if "gas" in df.columns:
                    df = df.rename(columns={"gas": "Nivel de Gas (ppm)"})
                if "tiempo" in df.columns:
                    df = df.rename(columns={"tiempo": "Tiempo"})
                
                with placeholder.container():
                    st.line_chart(df.set_index(df.columns[0]))
                    ultima = df.iloc[-1]
                    st.metric(label="Último nivel detectado (ppm)", value=ultima.iloc[1])
                    
                    if ultima.iloc[1] > 400:
                        st.error("🚨 Nivel peligroso de gas detectado. Activar protocolo de seguridad.")
                    else:
                        st.success("✅ Nivel seguro de gas detectado.")
            else:
                st.warning("⚠️ No hay lecturas disponibles aún.")
        else:
            st.error("❌ No se pudo obtener datos del servidor.")
    except Exception as e:
        st.error(f"Error al obtener lecturas: {e}")
    
    time.sleep(refresh_rate)

