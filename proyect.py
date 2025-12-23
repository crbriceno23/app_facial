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
    "¿Por qué los pájaros no usan Facebook? Porque ya tienen Twitter. 🐦",
    "¿Cuál es el colmo de un informático? Tener un 'bug' en la cama. 💻"
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
if 'mission_result' not in st.session_state: st.session_state.mission_result = None

# --- ESTILOS CSS (ESTRUCTURA SEGURA) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&family=Roboto:wght@300;400&display=swap');
    
    .stApp { background: #0a192f; color: #e6f1ff; font-family: 'Roboto', sans-serif; }
    
    .main-title {
        font-family: 'Orbitron', sans-serif; color: #fff; text-align: center; font-size: 3rem;
        text-shadow: 0 0 10px #00f2fe, 0 0 20px #00f2fe; margin-bottom: 0;
    }
    
    /* Caja de Misión Onichan (Estilo Anterior) */
    .mission-box {
        background: rgba(255, 215, 0, 0.05); 
        border: 2px dashed #ffd700; 
        padding: 20px; 
        border-radius: 10px; 
        text-align: center; 
        margin: 20px 0;
    }

    /* Paneles de Resultados */
    .result-card {
        background: rgba(10, 25, 47, 0.85); 
        border: 1px solid #00f2fe; 
        border-radius: 10px; 
        padding: 15px;
    }
    
    .bar-bg { background-color: #1a2a4e; border-radius: 10px; width: 100%; height: 12px; margin-bottom: 8px; }
    .bar-fill { background: linear-gradient(90deg, #00f2fe, #4c5fdc); height: 100%; border-radius: 10px; }
    
    .stButton>button {
        width: 100%; border: 2px solid #00f2fe !important; background: transparent !important; color: #00f2fe !important;
        font-family: 'Orbitron', sans-serif;
    }
    .stButton>button:hover { background: #00f2fe !important; color: #0a192f !important; }
    </style>
""", unsafe_allow_html=True)

# --- FUNCIÓN DE PROCESAMIENTO ---
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
        st.error(f"Error técnico: {e}")
    return None, None, None

# --- UI PRINCIPAL ---
st.markdown("<h1 class='main-title'>Jaime Roldós Aguilera</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#ffd700; font-family:Orbitron;'>PRESENTADO POR: LOS ONICHAN 😎</p>", unsafe_allow_html=True)

# Recuperamos el Panel de Misión con el estilo DASHED amarillo
st.markdown(f"""
    <div class="mission-box">
        <h3 style="color:#ffd700; margin:0; font-family:'Orbitron'">{st.session_state.mission['task']}</h3>
    </div>
""", unsafe_allow_html=True)

col_cam, col_res = st.columns([1, 1], gap="large")

with col_cam:
    st.markdown("<h4 style='font-family:Orbitron;'>📡 SCANNER BIOMÉTRICO</h4>", unsafe_allow_html=True)
    # Importante: Usar key para evitar el error de removeChild
    foto = st.camera_input("Scanner", label_visibility="collapsed", key="camara_onichan")
    
    if foto:
        if st.button("🔍 ANALIZAR DATOS", key="btn_analisis"):
            with st.spinner('⚡ SINCRONIZANDO...'):
                res_data, processed_img, dom_emo = procesar_imagen(foto)
                if res_data:
                    st.session_state.res_all = res_data['emotion']
                    st.session_state.dom_emo = dom_emo
                    st.session_state.img_display = processed_img
                    
                    target = st.session_state.mission['target']
                    score = st.session_state.res_all.get(target, 0)
                    st.session_state.mission_result = "SUCCESS" if score > 60 else "FAIL"
                    if st.session_state.mission_result == "SUCCESS": st.balloons()
                else:
                    st.warning("No se detectó rostro.")

with col_res:
    if st.session_state.res_all:
        # Indicador de Misión
        res_color = "#00ff00" if st.session_state.mission_result == "SUCCESS" else "#ff0000"
        res_text = "✅ MISIÓN COMPLETADA" if st.session_state.mission_result == "SUCCESS" else "❌ FALLO DE MISIÓN"
        
        st.markdown(f"""
            <div style="border: 2px solid {res_color}; padding:10px; border-radius:10px; text-align:center; margin-bottom:15px;">
                <h2 style="color:{res_color}; margin:0; font-family:Orbitron;">{res_text}</h2>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(f"<h4>ESTADO: {TRADUCCIONES.get(st.session_state.dom_emo, '').upper()}</h4>", unsafe_allow_html=True)
        
        if st.session_state.img_display is not None:
            st.image(st.session_state.img_display, use_container_width=True)

        # MOSTRAR IMAGEN DE LA CARPETA EMOCIONES (CORREGIDO)
        if IMG_FOLDER.exists():
            archivos = os.listdir(IMG_FOLDER)
            # Busca un archivo que tenga el nombre de la emoción detectada
            img_ref = next((f for f in archivos if st.session_state.dom_emo.lower() in f.lower()), None)
            if img_ref:
                st.image(str(IMG_FOLDER / img_ref), width=150, caption="Referencia Onichan")
        
        st.write(f"🤖 *Humor Bot:* {random.choice(CHISTES)}")
        
        # Barras de Análisis
        for emo, prob in st.session_state.res_all.items():
            if prob > 1:
                st.write(f"{TRADUCCIONES.get(emo, emo)}: {prob:.1f}%")
                st.markdown(f"<div class='bar-bg'><div class='bar-fill' style='width:{prob}%;'></div></div>", unsafe_allow_html=True)
    else:
        st.info("Esperando captura de datos biométricos...")

# --- EQUIPO ONICHAN ---
st.divider()
st.markdown("<h3 style='text-align:center; font-family:Orbitron;'>EQUIPO: LOS ONICHAN</h3>", unsafe_allow_html=True)
cols_e = st.columns(4)
nombres = ["Carlos", "Macas", "Jadiel", "Herrera"]

for i, nombre in enumerate(nombres):
    with cols_e[i]:
        if INTEGRANTES_FOLDER.exists():
            img_int = next((f for f in os.listdir(INTEGRANTES_FOLDER) if nombre.lower() in f.lower()), None)
            if img_int:
                st.image(str(INTEGRANTES_FOLDER / img_int), use_container_width=True)
        st.markdown(f"<p style='text-align:center; color:#ffd700;'>{nombre.upper()}</p>", unsafe_allow_html=True)

# Botón de Video Final
if INTEGRANTES_FOLDER.exists():
    video_img = next((f for f in os.listdir(INTEGRANTES_FOLDER) if "despedida" in f.lower()), None)
    if video_img:
        st.markdown("---")
        _, vid_col, _ = st.columns([1, 2, 1])
        with vid_col:
            st.image(str(INTEGRANTES_FOLDER / video_img), use_container_width=True)
            st.markdown("""
                <div style="text-align: center; margin-top: 15px;">
                    <a href="https://www.youtube.com/watch?v=He7dSGhyeHA" target="_blank" 
                       style="background: #00f2fe; color: #0a192f; padding: 15px 30px; text-decoration: none; 
                       border-radius: 5px; font-weight: bold; font-family: 'Orbitron'; display: inline-block;">
                       📺 VER VIDEO DEL PROYECTO
                    </a>
                </div>
            """, unsafe_allow_html=True)