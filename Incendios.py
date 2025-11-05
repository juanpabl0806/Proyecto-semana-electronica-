import streamlit as st
import requests
import time
from streamlit_lottie import st_lottie

# ==============================
# ⚙️ CONFIGURACIÓN DE PÁGINA
# ==============================
st.set_page_config(
    page_title="Alerta de Gas IoT",
    page_icon="🔥",
    layout="centered"
)

# ==============================
# 🌙 ESTILO OSCURO PERSONALIZADO
# ==============================
st.markdown(
    """
    <style>
    body {
        background-color: #0e1117;
        color: #fafafa;
    }
    .stApp {
        background-color: #0e1117;
    }
    h1, h2, h3, p, div, span {
        color: #fafafa !important;
    }
    .status-box {
        border-radius: 15px;
        padding: 15px;
        text-align: center;
        background-color: #1c1f26;
        box-shadow: 0 0 20px rgba(255, 75, 75, 0.3);
        margin-bottom: 20px;
    }
    .alerta-box {
        border-radius: 25px;
        padding: 40px;
        text-align: center;
        font-size: 26px;
        font-weight: bold;
        box-shadow: 0 0 30px rgba(255,255,255,0.15);
        transition: all 0.3s ease;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==============================
# 🎨 ANIMACIÓN LOTTIE
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
# 🖥️ INTERFAZ PRINCIPAL
# ==============================
col1, col2 = st.columns([1, 3])
with col1:
    lottie = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_tfb3estd.json")
    if lottie:
        st_lottie(lottie, height=180, key="alerta")

with col2:
    st.markdown(
        """
        <h1 style='font-size: 42px; color: #ff4b4b;'>Sistema IoT de Alerta de Gas 🔥</h1>
        <p style='font-size: 18px; color: #bdbdbd;'>Monitoreo en tiempo real desde tu ESP32 y servidor Flask en Render</p>
        """,
        unsafe_allow_html=True
    )

st.divider()

# ==============================
# 🌍 CONFIGURACIÓN DEL SERVIDOR
# ==============================
URL_BASE = "https://serverfire-1.onrender.com"

st.subheader("📡 Estado del Servidor")

status_box = st.empty()

try:
    resp = requests.get(f"{URL_BASE}/lecturas", timeout=5)
    if resp.status_code == 200:
        status_box.markdown(
            "<div class='status-box' style='color:#00ff7f;'>✅ Conectado correctamente con el servidor Render</div>",
            unsafe_allow_html=True
        )
    else:
        status_box.markdown(
            "<div class='status-box' style='color:#ffcc00;'>⚠️ Servidor accesible, pero sin datos válidos</div>",
            unsafe_allow_html=True
        )
except Exception as e:
    status_box.markdown(
        f"<div class='status-box' style='color:#ff4040;'>❌ Error al conectar con el servidor: {e}</div>",
        unsafe_allow_html=True
    )

st.divider()

# ==============================
# 🚨 MONITOREO DE GAS
# ==============================
st.subheader("🚨 Estado del sensor de gas")

placeholder = st.empty()
refresh_rate = st.slider("⏱️ Intervalo de actualización (segundos)", 2, 10, 4)

st.info("El sistema actualiza el estado automáticamente y borra la lectura anterior.")

# ==============================
# 🔁 BUCLE PRINCIPAL
# ==============================
while True:
    try:
        resp = requests.get(f"{URL_BASE}/lecturas", timeout=5)
        if resp.status_code == 200:
            lecturas = resp.json()

            if isinstance(lecturas, list) and len(lecturas) > 0:
                ultima = lecturas[-1]
                gas = ultima.get("gas", None)

                with placeholder.container():
                    if gas is not None:
                        if gas > 400:
                            # 🚨 Gas detectado
                            st.markdown(
                                """
                                <div class='alerta-box' style='background-color:#400000; border:2px solid #ff4b4b; box-shadow:0 0 25px #ff4b4b;'>
                                    🚨 <span style='color:#ff4b4b;'>GAS DETECTADO</span> 🚨<br>
                                    <p style='font-size:20px; color:#ffb3b3;'>¡Atención! Se ha detectado presencia de gas.</p>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                        else:
                            # ✅ Todo en orden
                            st.markdown(
                                """
                                <div class='alerta-box' style='background-color:#003300; border:2px solid #00ff88; box-shadow:0 0 25px #00ff88;'>
                                    ✅ <span style='color:#00ff88;'>TODO EN ORDEN</span><br>
                                    <p style='font-size:20px; color:#b3ffcc;'>No se detecta presencia de gas.</p>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                    else:
                        st.warning("⚠️ No se encontró valor 'gas' en la lectura.")

                # Mantener visible unos segundos
                time.sleep(refresh_rate)
                # Limpiar el mensaje
                placeholder.empty()

            else:
                with placeholder.container():
                    st.warning("Esperando lecturas del sensor...")
        else:
            st.error("❌ No se pudo obtener datos del servidor.")
    except Exception as e:
        st.error(f"Error al conectar con el servidor: {e}")

    time.sleep(refresh_rate)
