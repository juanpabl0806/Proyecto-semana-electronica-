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
    .muted { color:#9aa4ad; font-size:13px; text-align:center; }
    .small-btn { padding:8px 14px; border-radius:10px; font-weight:600; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>🔥 Sistema IoT — Detección de Humo (ESP32 + MQ-7)</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Interfaz en tiempo real — solo estado de humo. Temporizador de confirmación incluido.</div>", unsafe_allow_html=True)
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
# ESTADO Y PLACEHOLDERS
# =======================
placeholder = st.empty()
controls = st.empty()

# Sesión para almacenar estado de la alerta y temporizador
if "alert_active" not in st.session_state:
    st.session_state.alert_active = False        # True cuando hay detección en curso
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "alert_resolved" not in st.session_state:
    st.session_state.alert_resolved = False     # True si cancelado o confirmado
if "alert_auto_triggered" not in st.session_state:
    st.session_state.alert_auto_triggered = False

# Umbral lógico: si el servidor envía 1 => humo detectado
# Intervalo de actualización (segundos) y tiempo de confirmación (segundos)
refresh_rate = st.sidebar.slider("Intervalo de actualización (s)", min_value=2, max_value=10, value=4)
confirm_seconds = st.sidebar.number_input("Segundos para confirmación automática", min_value=5, max_value=120, value=30)

st.sidebar.markdown("**Notas:**\n- Si aparece humo, tendrás botones para cancelar o confirmar.\n- Si no actúas en el tiempo, se activa la alerta automática (visual).")

# =======================
# FUNCIONES AUXILIARES
# =======================
def obtener_ultimo_estado():
    """Devuelve el último JSON desde SERVER_URL o None"""
    try:
        resp = requests.get(SERVER_URL, timeout=6)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list) and len(data) > 0:
                last = data[-1]
                return last
        return None
    except Exception:
        return None

def activar_alerta_manual():
    st.session_state.alert_resolved = True
    st.session_state.alert_active = False
    st.session_state.alert_auto_triggered = False
    # Placeholder: aquí luego conectarás Twilio u otro servicio.
    st.info("Se confirmó alerta (acción manual). — *No se envió WhatsApp en esta versión*")

def cancelar_alerta():
    st.session_state.alert_resolved = True
    st.session_state.alert_active = False
    st.session_state.alert_auto_triggered = False
    st.session_state.start_time = None
    st.success("Alerta cancelada manualmente.")

def activar_alerta_automatica():
    st.session_state.alert_auto_triggered = True
    st.session_state.alert_active = False
    st.session_state.alert_resolved = True
    st.warning("Alerta automática activada (visual). — *No se envía WhatsApp en esta versión*")
    # Placeholder: aquí colocarás la llamada a la función que envía WhatsApp cuando lo habilites.

# =======================
# BUCLE PRINCIPAL (actualiza, muestra y borra)
# =======================
while True:
    last = obtener_ultimo_estado()
    if last is None:
        with placeholder.container():
            st.markdown("<div class='status-box'>Esperando lecturas del sensor...</div>", unsafe_allow_html=True)
        time.sleep(refresh_rate)
        continue

    # El servidor debe enviar {"humo_detectado": 0} o {"humo_detectado": 1} en cada lectura
    humo = int(last.get("humo_detectado", 0))

    # Si detecta humo y no hay aviso en proceso: iniciar proceso de confirmación
    if humo == 1 and not st.session_state.alert_active and not st.session_state.alert_resolved:
        st.session_state.alert_active = True
        st.session_state.start_time = time.time()
        st.session_state.alert_resolved = False
        st.session_state.alert_auto_triggered = False

    # Si no hay humo: mostrar "todo ok" brevemente y resetear estados
    if humo == 0:
        with placeholder.container():
            st.markdown("<div class='ok-box'>✅ Aire limpio y seguro</div>", unsafe_allow_html=True)
        # reset
        st.session_state.alert_active = False
        st.session_state.start_time = None
        st.session_state.alert_resolved = False
        st.session_state.alert_auto_triggered = False
        time.sleep(refresh_rate)
        placeholder.empty()
        continue

    # Si llegamos aquí, humo == 1 (detected)
    if st.session_state.alert_active and not st.session_state.alert_resolved:
        elapsed = int(time.time() - st.session_state.start_time)
        remaining = confirm_seconds - elapsed
        if remaining < 0:
            remaining = 0

        # Mostrar cuadro de alerta + contador + botones
        with placeholder.container():
            st.markdown(f"""
                <div class='alert-box' style='background:#2b0000; border:2px solid #ff4b4b;'>
                    🚨 <span style='color:#ff4b4b;'>HUMO DETECTADO</span><br>
                    <div style='font-size:16px; color:#ffd6d6; margin-top:8px;'>Si no cancelas, se activará la alerta automática en <strong>{remaining}s</strong></div>
                </div>
            """, unsafe_allow_html=True)

            # Botones en la misma línea
            c1, c2 = controls.columns([1,1])
            with c1:
                if st.button("📞 Llamar a emergencias (confirmar)"):
                    activar_alerta_manual()
            with c2:
                if st.button("✅ Cancelar alerta"):
                    cancelar_alerta()

        # Si el tiempo llegó a 0 y no se resolvió, activar alerta automática (visual only)
        if remaining <= 0 and not st.session_state.alert_resolved:
            activar_alerta_automatica()

        # esperar y repetir (el placeholder se vacía antes de la siguiente iteración)
        time.sleep(1)
        placeholder.empty()
        controls.empty()
        continue

    # Si hubo una alerta ya resuelta (manual o automática), mostramos un mensaje breve
    if st.session_state.alert_resolved:
        with placeholder.container():
            if st.session_state.alert_auto_triggered:
                st.markdown("<div class='status-box' style='color:#ffd27f;'>⚠️ Alerta automática activada (visual)</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='status-box' style='color:#7fffbf;'>ℹ️ Alerta resuelta manualmente</div>", unsafe_allow_html=True)
        time.sleep(refresh_rate)
        placeholder.empty()
        # luego permitimos que el sistema vuelva a detectar nuevas lecturas
        st.session_state.alert_resolved = False
        st.session_state.alert_auto_triggered = False
        st.session_state.start_time = None
        continue

    # Espera mínima para no sobrecargar la UI
    time.sleep(refresh_rate)

