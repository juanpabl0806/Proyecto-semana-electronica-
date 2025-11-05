import streamlit as st
import requests
import time
from streamlit_lottie import st_lottie

# ==============================
# ⚙️ CONFIGURACIÓN DE PÁGINA
# ==============================
st.set_page_config(
    page_title="Sistema IoT Alerta de Gas",
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
    .gas-box {
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        font-weight: bold;
        font-size: 22px;
        box-shadow: 0 0 25px rgba(255, 255, 255, 0.2);
        transition: all 0.3s ease;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==============================
# 🎨 CARGAR ANIMACIÓN LOTTIE
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
        <h1 style='font-size: 42px; color: #ff4b4b;'>Alerta de Gas IoT 🔥</h1>
        <p style='font-size: 18px; color: #bdbdbd;'>Monitoreo en tiempo real con ESP32 y servidor Flask en Render</p>
        """,
        unsafe_allow_html=True
    )

st.divider()

# ==============================
# 🌍 CONFIGURAR SERVIDOR
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
            "<div class='status-box' style='color:#ffcc00;'>⚠️ Servidor accesible, pero no devolvió datos válidos</div>",
            unsafe_allow_html=True
        )
except Exception as e:
    status_box.markdown(
        f"<div class='status-box' style='color:#ff4040;'>❌ Error al conectar con el servidor: {e}</div>",
        unsafe_allow_html=True
    )

st.divider()

# ==============================
# 📊 MONITOREO EN TIEMPO REAL
# ==============================
st.subheader("📈 Lectura Actual del Sensor de Gas")

placeholder = st.empty()
refresh_rate = st.slider("⏱️ Intervalo de actualización (segundos)", 2, 10, 4)


# ==============================
# 🔁 BUCLE PRINCIPAL
# ==============================
while True:
    try:
        resp = requests.get(f"{URL_BASE}/lecturas", timeout=5)
        if resp.status_code == 200:
            lecturas = resp.json()

            # Si hay datos, tomar el último
            if isinstance(lecturas, list) and len(lecturas) > 0:
                ultima = lecturas[-1]
                gas = ultima.get("gas", None)

                with placeholder.container():
                    if gas is not None:
                        color = "#ff4b4b" if gas > 400 else "#00ff88"
                        mensaje = (
                            "⚠️ Nivel peligroso de gas. ¡Activa el protocolo de seguridad!"
                            if gas > 400
                            else "✅ Nivel seguro de gas detectado."
                        )

                        st.markdown(
                            f"""
                            <div class='gas-box' style='background-color: rgba(255,255,255,0.05); border: 2px solid {color}; box-shadow: 0 0 20px {color};'>
                                <h2 style='color:{color};'>Nivel de gas detectado: <strong>{gas} ppm</strong></h2>
                                <p style='color:#ccc;'>{mensaje}</p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    else:
                        st.warning("⚠️ No se encontró el valor 'gas' en la lectura.")

                # Mantener el valor visible por unos segundos
                time.sleep(refresh_rate)

                # Limpiar para que desaparezca
                placeholder.empty()

            else:
                with placeholder.container():
                    st.warning("Esperando lecturas desde el sensor...")

        else:
            st.error("❌ No se pudo obtener datos del servidor.")
    except Exception as e:
        st.error(f"Error al conectar con el servidor: {e}")

    time.sleep(refresh_rate)

