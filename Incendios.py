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
        st_lottie(lottie, height=200, key="alerta")

with col2:
    st.markdown(
        """
        <h1 style='font-size: 42px; color: #ff4b4b;'>Alerta de Gas IoT 🔥</h1>
        <p style='font-size: 18px; color: #555;'>Monitoreo en tiempo real desde tu ESP32 conectado al servidor Flask en Render</p>
        """,
        unsafe_allow_html=True
    )

st.divider()

# ==============================
# 🌍 CONFIGURAR SERVIDOR
# ==============================
URL_BASE = "https://serverfire-1.onrender.com/"

st.subheader("📡 Estado del sistema")

# ==============================
# 🔁 MONITOREO SIN HISTORIAL
# ==============================
placeholder = st.empty()
refresh_rate = st.slider("⏱️ Intervalo de actualización (segundos)", 2, 10, 4)

st.info("El sistema muestra el último valor detectado y lo limpia automáticamente.")

while True:
    try:
        resp = requests.get(f"{URL_BASE}/lecturas", timeout=5)
        if resp.status_code == 200:
            lecturas = resp.json()

            # Si hay datos, toma el último valor
            if isinstance(lecturas, list) and len(lecturas) > 0:
                ultima = lecturas[-1]
                gas = ultima.get("gas", None)

                with placeholder.container():
                    if gas is not None:
                        st.markdown(
                            f"""
                            <div style="text-align:center; padding: 30px; border-radius: 20px;
                            background-color: {'#ffcccc' if gas > 400 else '#ccffcc'}; 
                            box-shadow: 0 4px 10px rgba(0,0,0,0.2);">
                                <h2 style="color: {'#b30000' if gas > 400 else '#006600'};">
                                    Nivel de gas detectado: <strong>{gas} ppm</strong>
                                </h2>
                                <p>{'⚠️ Nivel peligroso de gas. ¡Activa el protocolo de seguridad!' if gas > 400 else '✅ Nivel seguro.'}</p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    else:
                        st.warning("⚠️ No se encontró dato 'gas' en la lectura.")

                # Esperar antes de borrar el valor
                time.sleep(refresh_rate)

                # Limpiar el valor (desaparece)
                placeholder.empty()

            else:
                with placeholder.container():
                    st.warning("Esperando lecturas desde el sensor...")

        else:
            st.error("❌ No se pudo obtener datos del servidor.")
    except Exception as e:
        st.error(f"Error al conectar con el servidor: {e}")
    
    time.sleep(refresh_rate)

