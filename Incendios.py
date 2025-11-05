import streamlit as st
import requests
import time
import os

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
st.markdown("<div class='subtitle'>Interfaz en tiempo real — solo estado de humo. Actualización automática.</div>", unsafe_allow_html=True)
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
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "alert_resolved" not in st.session_state:
    st.session_state.alert_resolved = False
if "alert_auto_triggered" not in st.session_state:
    st.session_state.alert_auto_triggered = False

# Configuración lateral
refresh_rate = st.sidebar.slider("Intervalo de actualización (s)", 2, 10, 5)
confirm_seconds = st.sidebar.number_input("Segundos para confirmación automática", 5, 120, 30)

# =======================
# FUNCIONES AUXILIARES
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

def activar_alerta_manual():
    st.session_state.alert_resolved = True
    st.session_state.alert_active = False
    st.success("🚨 Alerta confirmada manualmente (simulación).")

def cancelar_alerta():
    st.session_state.alert_resolved = True
    st.session_state.alert_active = False
    st.success("✅ Alerta cancelada.")

def activar_alerta_automatica():
    st.session_state.alert_resolved = True
    st.session_state.alert_active = False
    st.warning("⚠️ Alerta automática activada (visual).")

# =======================
# ACTUALIZACIÓN AUTOMÁTICA
# =======================
# Reemplazamos la función experimental por la estable
st_autorefresh = st.rerun

data = obtener_ultimo_estado()
if data is None:
    st.markdown("<div class='status-box'>Esperando lecturas del sensor...</div>", unsafe_allow_html=True)
    st.rerun()

# =======================
# LÓGICA PRINCIPAL
# =======================
humo = int(data.get("humo_detectado", 0))
now = time.time()

# Detección de humo
if humo == 1 and not st.session_state.alert_active:
    st.session_state.alert_active = True
    st.session_state.start_time = now
    st.session_state.alert_resolved = False
    st.session_state.alert_auto_triggered = False

if humo == 0:
    st.markdown("<div class='ok-box'>✅ Aire limpio y seguro</div>", unsafe_allow_html=True)
    st.session_state.alert_active = False
    st.session_state.alert_resolved = False
    time.sleep(refresh_rate)
    st.rerun()

# Mostrar alerta activa
if st.session_state.alert_active and not st.session_state.alert_resolved:
    elapsed = int(now - st.session_state.start_time)
    remaining = confirm_seconds - elapsed
    if remaining <= 0:
        activar_alerta_automatica()
        st.rerun()

    st.markdown(f"""
        <div class='alert-box' style='background:#2b0000; border:2px solid #ff4b4b;'>
            🚨 <span style='color:#ff4b4b;'>HUMO DETECTADO</span><br>
            <div style='font-size:16px; color:#ffd6d6; margin-top:8px;'>
                Si no cancelas, se activará la alerta automática en <strong>{remaining}s</strong>
            </div>
        </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("📞 Llamar a emergencias (confirmar)", key="confirm_btn"):
            activar_alerta_manual()
            st.rerun()
    with c2:
        if st.button("✅ Cancelar alerta", key="cancel_btn"):
            cancelar_alerta()
            st.rerun()

# Mostrar resultado de alerta resuelta
elif st.session_state.alert_resolved:
    if st.session_state.alert_auto_triggered:
        st.markdown("<div class='status-box' style='color:#ffd27f;'>⚠️ Alerta automática activada</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='status-box' style='color:#7fffbf;'>ℹ️ Alerta resuelta manualmente</div>", unsafe_allow_html=True)
    time.sleep(refresh_rate)
    st.session_state.alert_resolved = False
    st.rerun()

# Refresco automático
time.sleep(refresh_rate)
st.rerun()


