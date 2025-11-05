import streamlit as st
import pandas as pd
import requests
from streamlit_lottie import st_lottie

# ----------------- CONFIGURACIÓN GENERAL -----------------
st.set_page_config(
    page_title="Sistema de Alerta Temprana IoT",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ----------------- ESTILOS PERSONALIZADOS -----------------
st.markdown("""
    <style>
        /* Fondo general */
        .stApp {
            background: linear-gradient(135deg, #1a1a2e, #16213e);
            color: white;
        }

        /* Título principal */
        h1 {
            text-align: center;
            color: #ff4b5c;
            text-shadow: 2px 2px 8px #000;
        }

        /* Tarjetas */
        .metric-card {
            background-color: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
            transition: 0.3s;
        }
        .metric-card:hover {
            transform: scale(1.05);
            background-color: rgba(255, 255, 255, 0.15);
        }

        /* Texto */
        .small {
            font-size: 14px;
            color: #ccc;
        }
    </style>
""", unsafe_allow_html=True)

# ----------------- FUNCIÓN PARA ANIMACIÓN -----------------
def load_lottie_url(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Animación Lottie
alert_animation = load_lottie_url("https://assets2.lottiefiles.com/packages/lf20_x62chJ.json")
ok_animation = load_lottie_url("https://assets10.lottiefiles.com/packages/lf20_lk80fpsm.json")

# ----------------- TÍTULO -----------------
st.markdown("<h1>🔥 Sistema de Alerta Temprana IoT</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center' class='small'>Monitoreo en tiempo real de temperatura y gas con notificación de alerta.</p>", unsafe_allow_html=True)
st.markdown("---")

# ----------------- LECTURA DE DATOS -----------------
try:
    response = requests.get("http://TU_SERVIDOR_IP:5000/lecturas")
    data = response.json()
    df = pd.DataFrame(data)

    # ----------------- DASHBOARD -----------------
    col1, col2 = st.columns(2)
    temp_actual = df["temperature"].iloc[-1]
    gas_actual = df["gas"].iloc[-1]

    with col1:
        st.markdown(f"<div class='metric-card'><h3>🌡 Temperatura</h3><h1>{temp_actual:.1f} °C</h1></div>", unsafe_allow_html=True)

    with col2:
        st.markdown(f"<div class='metric-card'><h3>🧪 Nivel de Gas</h3><h1>{gas_actual:.1f} ppm</h1></div>", unsafe_allow_html=True)

    st.markdown("---")

    # ----------------- GRÁFICA -----------------
    st.subheader("📊 Registro en tiempo real")
    st.line_chart(df[["temperature", "gas"]])

    # ----------------- ALERTA -----------------
    st.markdown("---")
    if temp_actual > 60 or gas_actual > 400:
        st_lottie(alert_animation, height=200, key="alert")
        st.error("🚨 **¡ALERTA! Posible incendio detectado.** Verifica la zona inmediatamente.")
    else:
        st_lottie(ok_animation, height=200, key="ok")
        st.success("✅ **Sistema estable.** No se detectan anomalías.")

except Exception as e:
    st.error(f"⚠️ Error al conectar con el servidor Flask.\n\nDetalles: {e}")
