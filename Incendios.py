import streamlit as st
import requests
import time
import os
from twilio.rest import Client

# =======================
# CONFIGURACIÓN DE PÁGINA
# =======================
st.set_page_config(
    page_title="🔥 Detector de Humo IoT",
    page_icon="🔥",
    layout="centered"
)

# =======================
# ESTILO OSCURO PERSONALIZADO Y EFECTOS
# =======================
st.markdown("""
    <style>
    body {
        background: radial-gradient(circle at top left, #1a1a1a, #0d0d0d);
        color: #e6e6e6;
        font-family: 'Segoe UI', sans-serif;
    }
    .stApp { background-color: transparent; }
    .title {
        font-size:46px; 
        color:#ff5b5b; 
        font-weight:800; 
        text-align:center; 
        text-shadow: 0px 0px 20px rgba(255, 90, 90, 0.6);
        margin-bottom:10px;
    }
    .subtitle {
        font-size:17px; 
        color:#b9c0c7; 
        text-align:center; 
        margin-bottom:25px;
    }
    .status-box {
        border-radius: 14px;
        padding: 14px;
        background: rgba(30,30,30,0.8);
        text-align:center;
        box-shadow: 0 6px 22px rgba(0,0,0,0.6);
        margin-bottom: 16px;
        font-size: 16px;
    }
    .alert-box {
        border-radius: 25px;
        padding: 40px;
        text-align:center;
        font-weight:800;
        font-size:28px;
        color:#ff4b4b;
        animation: blink 1s infinite;
        background: linear-gradient(135deg, #400000, #ff1a1a);
        box-shadow: 0px 0px 50px rgba(255, 20, 20, 0.5);
    }
    @keyframes blink {
        0% { opacity: 1; transform: scale(1.02);}
        50% { opacity: 0.7; transform: scale(1.07);}
        100% { opacity: 1; transform: scale(1.02);}
    }
    .ok-box {
        border-radius: 22px;
        padding: 36px;
        text-align:center;
        font-weight:700;
        font-size:26px;
        color:#88ffb7;
        background: linear-gradient(135deg, #0f3d22, #00b86b);
        box-shadow: 0px 0px 40px rgba(0,255,120,0.2);
    }
    .footer {
        text-align:center;
        margin-top:30px;
        font-size:13px;
        color:#666;
    }
    </style>
""", unsafe_allow_html=True)

# =======================
# TÍTULO Y ENCABEZADO
# =======================
st.markdown("<div class='title'>🔥 Sistema IoT — Detector de Humo</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>ESP32 + Sensor MQ-7 + Notificación por WhatsApp</div>", unsafe_allow_html=True)
st.divider()

# =======================
# CONFIGURACIÓN DEL SERVIDOR
# =======================
SERVER_URL = os.getenv("SERVER_URL", "https://serverfire-1.onrender.com/ultimos")

st.subheader("📡 Estado del servidor Flask")
status_placeholder = st.empty()
try:
    r = requests.get(SERVER_URL, timeout=6)
    if r.status_code == 200:
        status_placeholder.markdown("<div class='status-box' style='color:#7fffbf;'>✅ Servidor conectado</div>", unsafe_allow_html=True)
    else:
        status_placeholder.markdown("<div class='status-box' style='color:#ffd27f;'>⚠️ Servidor accesible pero sin datos válidos</div>", unsafe_allow_html=True)
except Exception as e:
    status_placeholder.markdown(f"<div class='status-box' style='color:#ff7f7f;'>❌ No se pudo conectar: {e}</div>", unsafe_allow_html=True)

st.divider()

# =======================
# SESIÓN Y CONFIGURACIÓN
# =======================
if "alert_active" not in st.session_state:
    st.session_state.alert_active = False
if "whatsapp_sent" not in st.session_state:
    st.session_state.whatsapp_sent = False

refresh_rate = st.sidebar.slider("Intervalo de actualización (s)", 2, 10, 5)

# =======================
# CONFIGURACIÓN TWILIO
# =======================
ACCOUNT_SID = "AC8d93fa0d9e45de116e1c0e2dcf0009cb"
AUTH_TOKEN = "3ee2f9f361f5d71ffbd180161962eb85"
TO_NUMBER = "whatsapp:+573205639118"
FROM_NUMBER = "whatsapp:+14155238886"

def enviar_mensaje_whatsapp():
    try:
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        message = client.messages.create(
            from_=FROM_NUMBER,
            to=TO_NUMBER,
            body="🚨 *ALERTA DE HUMO DETECTADA*\n\nEl sistema IoT ha detectado humo en el área.\nPor favor, verifica la zona inmediatamente."
        )
        st.session_state.whatsapp_sent = True
        st.success("📲 Mensaje de alerta enviado por WhatsApp.")
        print(f"Mensaje enviado con SID: {message.sid}")
    except Exception as e:
        st.error(f"❌ Error al enviar mensaje: {e}")

# =======================
# OBTENER DATOS DEL SERVIDOR
# =======================
def obtener_ultimo_estado():
    try:
        resp = requests.get(SERVER_URL, timeout=6)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list) and len(data) > 0:
                return data[-1]
        return None
    except:
        return None

# =======================
# LÓGICA PRINCIPAL
# =======================
data = obtener_ultimo_estado()
if data is None:
    st.markdown("<div class='status-box'>Esperando lecturas del sensor...</div>", unsafe_allow_html=True)
    time.sleep(refresh_rate)
    st.rerun()

humo = int(data.get("humo_detectado", 0))

if humo == 1:
    st.session_state.alert_active = True
    st.markdown("<div class='alert-box'>🚨 ¡PELIGRO! HUMO DETECTADO</div>", unsafe_allow_html=True)

    if not st.session_state.whatsapp_sent:
        enviar_mensaje_whatsapp()
else:
    st.session_state.alert_active = False
    st.session_state.whatsapp_sent = False
    st.markdown("<div class='ok-box'>✅ Aire limpio y seguro</div>", unsafe_allow_html=True)

time.sleep(refresh_rate)
st.rerun()

# =======================
# FOOTER
# =======================
st.markdown("<div class='footer'>Desarrollado por Juan Pablo Pedraza Contreras — Universidad Santo Tomás</div>", unsafe_allow_html=True)


