import streamlit as st
import requests
import time
import os
from twilio.rest import Client  # 👈 Importar Twilio

# =======================
# CONFIGURACIÓN DE PÁGINA
# =======================
st.set_page_config(page_title="Alerta de Humo IoT", page_icon="🔥", layout="centered")

# =======================
# ESTILO OSCURO PERSONALIZADO
# =======================
st.markdown("""
    <style>
    body {
        background: linear-gradient(135deg, #0e1117, #16202b);
        color: #f6f7f9;
    }
    .stApp { background-color: transparent; }
    .title { font-size:40px; color:#ff5b5b; font-weight:700; text-align:center; }
    .subtitle { font-size:14px; color:#b9c0c7; text-align:center; margin-bottom:18px; }
    .status-box {
        border-radius: 12px;
        padding: 12px;
        background: #111318;
        text-align:center;
        box-shadow: 0 6px 22px rgba(0,0,0,0.6);
        margin-bottom: 16px;
    }
    .alert-box {
        border-radius: 18px;
        padding: 26px;
        text-align:center;
        font-weight:700;
        font-size:22px;
        box-shadow: 0 8px 30px rgba(255,0,0,0.12);
    }
    .ok-box {
        border-radius: 18px;
        padding: 26px;
        text-align:center;
        font-weight:700;
        font-size:22px;
        box-shadow: 0 8px 30px rgba(0,255,120,0.06);
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>🔥 Sistema IoT — Detección de Humo (ESP32 + MQ-7)</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Interfaz en tiempo real — con notificación por WhatsApp</div>", unsafe_allow_html=True)
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
# VARIABLES DE SESIÓN
# =======================
if "alert_active" not in st.session_state:
    st.session_state.alert_active = False
if "alert_resolved" not in st.session_state:
    st.session_state.alert_resolved = False
if "whatsapp_sent" not in st.session_state:
    st.session_state.whatsapp_sent = False

# Configuración lateral
refresh_rate = st.sidebar.slider("Intervalo de actualización (s)", 2, 10, 5)

# =======================
# CONFIGURACIÓN TWILIO
# =======================
ACCOUNT_SID = "AC8d93fa0d9e45de116e1c0e2dcf0009cb"  # ⚠️ Tu SID real
AUTH_TOKEN = "3ee2f9f361f5d71ffbd180161962eb85"      # ⚠️ Tu Token real
TO_NUMBER = "whatsapp:+573205639118"                # ⚠️ Tu número (con prefijo)
FROM_NUMBER = "whatsapp:+14155238886"               # Número de Twilio sandbox

# =======================
# FUNCIONES AUXILIARES
# =======================
def enviar_mensaje_whatsapp():
    """Envía mensaje de alerta por WhatsApp."""
    try:
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        message = client.messages.create(
            from_=FROM_NUMBER,
            to=TO_NUMBER,
            body="🚨 ALERTA DE HUMO DETECTADA ⚠️\nEl sistema IoT ha detectado humo. Revisa la zona inmediatamente."
        )
        st.session_state.whatsapp_sent = True
        st.success("📲 Mensaje de alerta enviado por WhatsApp.")
        print(f"Mensaje enviado con SID: {message.sid}")
    except Exception as e:
        st.error(f"❌ Error al enviar mensaje: {e}")

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
# ACTUALIZACIÓN Y LÓGICA
# =======================
data = obtener_ultimo_estado()
if data is None:
    st.markdown("<div class='status-box'>Esperando lecturas del sensor...</div>", unsafe_allow_html=True)
    time.sleep(refresh_rate)
    st.rerun()

humo = int(data.get("humo_detectado", 0))

if humo == 1:
    st.session_state.alert_active = True
    st.markdown("<div class='alert-box' style='background:#2b0000; border:2px solid #ff4b4b;'>🚨 HUMO DETECTADO</div>", unsafe_allow_html=True)
    
    # Enviar mensaje si aún no se envió
    if not st.session_state.whatsapp_sent:
        enviar_mensaje_whatsapp()
else:
    st.session_state.alert_active = False
    st.session_state.whatsapp_sent = False
    st.markdown("<div class='ok-box'>✅ Aire limpio y seguro</div>", unsafe_allow_html=True)

time.sleep(refresh_rate)
st.rerun()


