import streamlit as st
import cv2
from deepface import DeepFace
import numpy as np
import random

# --- CONFIGURACIÓN Y ESTILOS ---
st.set_page_config(page_title="Detector Emocional", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button { width: 100%; border-radius: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DATOS ---
mensajes = {
    "happy": "✨ ¡Tu sonrisa es contagiosa! Nunca dejes de sonreír.",
    "sad": "Ánimo, recuerda que después de la tormenta siempre sale el sol. 🌈",
    "angry": "Respira profundo... No dejes que un momento arruine tu paz. 🧘‍♂️",
    "surprise": "¡Wow! Qué buena expresión, mantén esa energía.",
    "neutral": "Te ves en paz hoy. Es un buen momento para seguir creando."
}
chistes = [
    "¿Qué le dice un jaguar a otro jaguar? ¡Jaguar you!",
    "¿Cómo se dice pañuelo en japonés? Sakamoko.",
    "¿Por qué los pájaros no usan Facebook? Porque ya tienen Twitter."
]

# --- LÓGICA DE CÁMARA ---
st.title("🎭 Detector de Expresiones Faciales")

# Opción para usar la cámara nativa de Streamlit (más estable)
img_file_buffer = st.camera_input("Toma una foto para analizar tu emoción")

if img_file_buffer is not None:
    try:
        # Convertir la imagen del buffer a un formato que OpenCV entienda
        bytes_data = img_file_buffer.getvalue()
        cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)

        # Análisis de emoción
        with st.spinner('Analizando tu rostro...'):
            results = DeepFace.analyze(cv2_img, actions=['emotion'], enforce_detection=True)
            emocion = results[0]['dominant_emotion']

        # Mostrar resultados según la emoción
        st.write(f"### Sentimos que estás: **{emocion.upper()}**")
        
        if emocion in ['sad', 'angry']:
            st.warning(mensajes.get(emocion, "¡Ánimo!"))
            st.info(f"🃏 Un chiste para ti: {random.choice(chistes)}")
        elif emocion == 'happy':
            st.balloons()
            st.success(mensajes['happy'])
        else:
            st.info(mensajes.get(emocion, "¡Te ves genial!"))

    except ValueError:
        st.error("❌ No se detectó un rostro claro. ¡Asegúrate de que haya buena luz e inténtalo de nuevo!")
    except Exception as e:
        st.error(f"Ocurrió un error inesperado: {e}")
else:
    st.info("👆 Por favor, permite el acceso a la cámara y toma una foto para comenzar.")