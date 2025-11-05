import streamlit as st
import pandas as pd
import requests
import time
from twilio.rest import Client
from streamlit_lottie import st_lottie

# ----------------- CONFIGURACIÓN GENERAL -----------------
st.set_page_config(page_title="Sistema IoT de Gas", page_icon="🧪", layout="wide")

# ----------------- FUNCIÓN PARA ANIMACIÓN -----------------
def load_lottie_url(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

alert_animation = load_lottie_url("https://assets2.lottiefiles.com/packages/lf20_x62chJ.json")
ok_animation = load_lottie_url("https://assets10.lottiefiles.com/packages/lf20_lk80fpsm.json")

# ----------------- FUNCIÓN PARA ENVIAR WHATSAPP -----------------
def enviar_alerta_whatsapp(mensaje):
    try:
        # 🔐 Ingresa tus credenciales de Twilio aquí
        account_sid = 'AC8d93fa0d9e45de116e1c0e2dcf0009cb'
        auth_token = '60257ba9848f7fadfe41022c35b66495'
        client = Client(account_sid, auth_token)

        from_whatsapp = 'whatsapp:+14155238886',  
        to_whatsapp = 'whatsapp:+573205639118'  

        client.messages.create(body=mensaje, from_=from_whatsapp, to=to_whatsapp)
        st.success("Alerta enviada correctamente por WhatsApp.")
    except Exception as e:
        st.error(f"Error al enviar alerta de WhatsApp: {e}")

# ----------------- INTERFAZ PRINCIPAL -----------------
st.markdown("<h1 style='text-align:center;color:#ff4b5c;'>🧪 Sistema de Prevencion de Incendios</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#ccc;'>Monitoreo en tiempo real del nivel de gas con alerta automática.</p>", unsafe_allow_html=True)
st.markdown("---")

# ----------------- LECTURA DE DATOS -----------------
try:
    response = requests.get("http://10.16.20.252:5000")  # Cambia por la IP real de tu ESP32 / servidor Flask
    data = response.json()
    df = pd.DataFrame(data)

    gas_actual = df["gas"].iloc[-1]

    # Mostrar métrica y gráfico
    st.metric("Nivel de Gas", f"{gas_actual:.1f} ppm")
    st.line_chart(df[["gas"]])

    # ----------------- DETECCIÓN DE ALERTA -----------------
    if gas_actual > 400:
        st_lottie(alert_animation, height=200, key="alert")
        st.error("🚨 ¡Nivel de gas peligroso detectado!")

        st.markdown("### ⚠️ Confirma la alerta en 30 segundos o se notificará automáticamente por WhatsApp.")

        # Variables de sesión
        if "alert_active" not in st.session_state:
            st.session_state.alert_active = True
            st.session_state.start_time = time.time()
            st.session_state.alert_resolved = False
            st.session_state.alert_sent = False

        # Botones
        colA, colB = st.columns(2)
        with colA:
            if st.button("📞 Llamar a urgencias ahora"):
                st.session_state.alert_resolved = True
                enviar_alerta_whatsapp(f"🚨 Alerta IoT: alto nivel de gas detectado ({gas_actual:.1f} ppm).")
                st.success("📡 Se ha notificado a los servicios de emergencia.")
        with colB:
            if st.button("✅ Cancelar alerta (falsa alarma)"):
                st.session_state.alert_resolved = True
                st.info("🟢 Alerta cancelada manualmente.")

        # Temporizador de 30 segundos
        elapsed = time.time() - st.session_state.start_time
        remaining = int(30 - elapsed)

        if not st.session_state.alert_resolved:
            if remaining > 0:
                st.warning(f"Tiempo restante para confirmar: **{remaining} segundos**")
                time.sleep(1)
                st.rerun()
            else:
                st.session_state.alert_resolved = True
                if not st.session_state.alert_sent:
                    enviar_alerta_whatsapp(f"🚨 ALERTA AUTOMÁTICA IoT: No hubo respuesta. Nivel de gas: {gas_actual:.1f} ppm.")
                    st.session_state.alert_sent = True
                st.error("🚨 No hubo respuesta. Se ha notificado automáticamente a urgencias por WhatsApp.")

    else:
        st_lottie(ok_animation, height=200, key="ok")
        st.success("✅ Nivel de gas estable.")
        st.session_state.alert_active = False
        st.session_state.alert_resolved = False
        st.session_state.alert_sent = False

except Exception as e:
    st.error(f"⚠️ Error al conectar con el servidor Flask.\n\nDetalles: {e}")
