import streamlit as st
import cv2
from deepface import DeepFace
import numpy as np
import random
import os
from pathlib import Path

# --- CONFIGURACIÓN INICIAL ---
st.set_page_config(
    page_title="Cyber-Vision Roldós: Los Onichan Web",
    page_icon="⚡",
    layout="wide",
)

# --- GESTIÓN DE RUTAS ---
ROOT_DIR = Path(__file__).parent
IMG_FOLDER = ROOT_DIR / "emociones_img"
INTEGRANTES_FOLDER = ROOT_DIR / "integrantes_img"

# --- CONSTANTES Y ESTADO ---
TRADUCCIONES = {
    "happy": "Felicidad", "sad": "Tristeza", "angry": "Enojo", 
    "surprise": "Sorpresa", "neutral": "Neutral", "fear": "Miedo", 
    "disgust": "Disgusto"
}

CHISTES = [
    "¿Qué le dice un jaguar a otro? ¡Jaguar you! 😂",
    "¿Cuál es el colmo de un informático? Tener un 'bug' en la cama. 💻",
    "¿Qué hace una abeja en el gimnasio? ¡Zum-ba! 🐝"
]

MISIONES = [
    {"target": "happy", "task": "🎯 MISIÓN ONICHAN: ¡Logra una sonrisa superior al 60%!"},
    {"target": "surprise", "task": "🎯 MISIÓN ONICHAN: ¡Supera el 60% de sorpresa!"},
    {"target": "neutral", "task": "🎯 MISIÓN ONICHAN: ¡Mantén una cara totalmente seria!"},
    {"target": "angry", "task": "🎯 MISIÓN ONICHAN: ¡Muestra tu cara de guerra (Enojo)!"}
]

if 'mission' not in st.session_state: st.session_state.mission = random.choice(MISIONES)
if 'res_all' not in st.session_state: st.session_state.res_all = None
if 'img_display' not in st.session_state: st.session_state.img_display = None
if 'dom_emo' not in st.session_state: st.session_state.dom_emo = None

# --- ESTILOS CSS (MEJORADOS PARA ESTABILIDAD) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&family=Roboto:wght@300;400&display=swap');
    
    .stApp { background: #0a192f; color: #e6f1ff; font-family: 'Roboto', sans-serif; }
    
    .main-title {
        font-family: 'Orbitron', sans-serif; color: #fff; text-align: center; font-size: 3rem;
        text-shadow: 0 0 10px #00f2fe; margin-bottom: 0;
    }
    
    /* Contenedor estilo Cyber */
    [data-testid="stVerticalBlock"] > div:has(div.cyber-card) {
        background: rgba(10, 25, 47, 0.85);
        border: 1px solid #00f2fe;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
    }
    
    .bar-bg { background-color: #1a2a4e; border-radius: 10px; width: 100%; height: 12px; margin-bottom: 8px; }
    .bar-fill { background: linear-gradient(90deg, #00f2fe, #4c5fdc); height: 100%; border-radius: 10px; }
    
    .stButton>button {
        width: 100%; border: 2px solid #00f2fe; background: transparent; color: #00f2fe;
        font-family: 'Orbitron', sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

# --- FUNCION DE PROCESAMIENTO ---
def procesar_imagen(foto_input):
    try:
        file_bytes = np.asarray(bytearray(foto_input.getvalue()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, 1)
        results = DeepFace.analyze(img, actions=['emotion'], enforce_detection=False, detector_backend='opencv')
        if results:
            res = results[0]
            reg = res['region']
            cv2.rectangle(img, (reg['x'], reg['y']), (reg['x'] + reg['w'], reg['y'] + reg['h']), (0, 242, 254), 3)
            return res, cv2.cvtColor(img, cv2.COLOR_BGR2RGB), res['dominant_emotion']
    except Exception as e:
        st.error(f"Error en análisis: {e}")
    return None, None, None

# --- UI PRINCIPAL ---
st.markdown("<h1 class='main-title'>Jaime Roldós Aguilera</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#ffd700; font-family:Orbitron;'>PRESENTADO POR: LOS ONICHAN 😎</p>", unsafe_allow_html=True)

# Panel de Misión Permanente
st.info(st.session_state.mission['task'])

col_cam, col_res = st.columns(2)

with col_cam:
    st.subheader("📡 SCANNER BIOMÉTRICO")
    # Añadimos una KEY única para evitar errores de duplicados
    foto = st.camera_input("Captura", label_visibility="collapsed", key="onichan_cam")
    
    if foto:
        if st.button("🔍 ANALIZAR ROSTRO", key="btn_analizar"):
            res_data, processed_img, dom_emo = procesar_imagen(foto)
            if res_data:
                st.session_state.res_all = res_data['emotion']
                st.session_state.dom_emo = dom_emo
                st.session_state.img_display = processed_img
            else:
                st.error("No se detectó rostro.")

with col_res:
    if st.session_state.res_all:
        emo_detectada = st.session_state.dom_emo
        score_mision = st.session_state.res_all.get(st.session_state.mission['target'], 0)
        
        # Resultado de Misión
        if score_mision > 60:
            st.success("✅ ¡MISIÓN COMPLETADA!")
            st.balloons()
        else:
            st.error("❌ MISIÓN FALLIDA - ¡INTÉNTALO OTRA VEZ!")
        
        st.write(f"### ESTADO: {TRADUCCIONES.get(emo_detectada, emo_detectada).upper()}")
        
        if st.session_state.img_display is not None:
            st.image(st.session_state.img_display, use_container_width=True)
        
        # Mostrar Imagen de la carpeta emociones_img
        if IMG_FOLDER.exists():
            archivos = os.listdir(IMG_FOLDER)
            img_ref = next((f for f in archivos if emo_detectada.lower() in f.lower()), None)
            if img_ref:
                st.image(str(IMG_FOLDER / img_ref), width=150, caption="Tu Onichan interior")

        # Barras de Análisis
        st.write("---")
        for emo, prob in st.session_state.res_all.items():
            if prob > 1:
                st.write(f"{TRADUCCIONES.get(emo, emo)}: {prob:.1f}%")
                st.markdown(f"<div class='bar-bg'><div class='bar-fill' style='width:{prob}%;'></div></div>", unsafe_allow_html=True)
    else:
        st.write("Esperando datos del scanner...")

# --- EQUIPO ---
st.write("---")
st.markdown("<h3 style='text-align:center; font-family:Orbitron;'>EQUIPO: LOS ONICHAN</h3>", unsafe_allow_html=True)
cols_equipo = st.columns(4)
nombres = ["Carlos", "Macas", "Jadiel", "Herrera"]

for i, nombre in enumerate(nombres):
    with cols_equipo[i]:
        if INTEGRANTES_FOLDER.exists():
            img_int = next((f for f in os.listdir(INTEGRANTES_FOLDER) if nombre.lower() in f.lower()), None)
            if img_int:
                st.image(str(INTEGRANTES_FOLDER / img_int), use_container_width=True)
        st.markdown(f"<p style='text-align:center;'>{nombre.upper()}</p>", unsafe_allow_html=True)