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
    initial_sidebar_state="collapsed"
)

# --- GESTIÓN DE RUTAS (COMPATIBILIDAD NUBE/LOCAL) ---
# En Streamlit Cloud, el script corre en la raíz.
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
    "¿Cuál es el colmo de un informático? Tener un 'bug' en la cama. 💻",
    "¿Qué hace una abeja en el gimnasio? ¡Zum-ba! 🐝",
    "Error 404: Chiste no encontrado. 🤖"
]

MISIONES = [
    {"target": "happy", "task": "🎯 MISIÓN ONICHAN: ¡Logra una sonrisa superior al 70%!"},
    {"target": "surprise", "task": "🎯 MISIÓN ONICHAN: ¡Supera el 60% de sorpresa!"},
    {"target": "neutral", "task": "🎯 MISIÓN ONICHAN: ¡Mantén una cara totalmente seria!"},
    {"target": "angry", "task": "🎯 MISIÓN ONICHAN: ¡Muestra tu cara de guerra (Enojo)!"}
]

# Inicialización de estado
if 'res_all' not in st.session_state: st.session_state.res_all = None
if 'dom_emo' not in st.session_state: st.session_state.dom_emo = None
if 'mission' not in st.session_state: st.session_state.mission = random.choice(MISIONES)
if 'mission_result' not in st.session_state: st.session_state.mission_result = None
if 'img_display' not in st.session_state: st.session_state.img_display = None

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&family=Roboto:wght@300;400&display=swap');
    
    .stApp { background: #0a192f; color: #e6f1ff; font-family: 'Roboto', sans-serif; }
    
    /* Títulos */
    .main-title {
        font-family: 'Orbitron', sans-serif; color: #fff; text-align: center; font-size: 3rem;
        text-shadow: 0 0 10px #00f2fe, 0 0 20px #00f2fe; animation: pulse 2s infinite;
    }
    .onichan-text {
        font-family: 'Orbitron', sans-serif; color: #ffd700; text-align: center; 
        font-size: 1.2rem; text-shadow: 0 0 10px #ffd700; margin-bottom: 20px;
    }
    
    /* Paneles */
    .cyber-panel {
        background: rgba(10, 25, 47, 0.85); border: 1px solid #00f2fe; border-radius: 10px;
        padding: 20px; margin-bottom: 15px; box-shadow: 0 0 15px rgba(0, 242, 254, 0.1);
        backdrop-filter: blur(5px);
    }
    
    /* Animación */
    @keyframes pulse {
        0% { text-shadow: 0 0 10px #00f2fe; }
        50% { text-shadow: 0 0 30px #00f2fe; }
        100% { text-shadow: 0 0 10px #00f2fe; }
    }
    
    /* Barras de progreso */
    .bar-bg { background-color: #1a2a4e; border-radius: 10px; width: 100%; height: 12px; margin-bottom: 8px; border: 1px solid #303C55; }
    .bar-fill { background: linear-gradient(90deg, #00f2fe, #4c5fdc); height: 100%; border-radius: 10px; }
    
    /* Botones y Widgets */
    .stButton>button {
        width: 100%; border: 2px solid #00f2fe; background: transparent; color: #00f2fe;
        border-radius: 10px; font-family: 'Orbitron', sans-serif; transition: 0.3s;
    }
    .stButton>button:hover { background: #00f2fe; color: #0a192f; box-shadow: 0 0 20px #00f2fe; }
    
    img { border-radius: 8px; border: 1px solid #00f2fe; }
    </style>
""", unsafe_allow_html=True)

# --- LÓGICA DE PROCESAMIENTO ---
def procesar_imagen(foto_input):
    try:
        file_bytes = np.asarray(bytearray(foto_input.getvalue()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, 1)
        
        # DeepFace Analyze
        results = DeepFace.analyze(
            img, 
            actions=['emotion'], 
            enforce_detection=False, 
            detector_backend='opencv', 
            align=True
        )
        
        if not results:
            return None, None, None

        res = results[0]
        reg = res['region']
        
        # Dibujar rectángulo
        cv2.rectangle(img, (reg['x'], reg['y']), (reg['x'] + reg['w'], reg['y'] + reg['h']), (0, 242, 254), 3)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        return res, img_rgb, res['dominant_emotion']
        
    except Exception as e:
        st.error(f"Error técnico en procesamiento: {str(e)}")
        return None, None, None

# --- INTERFAZ PRINCIPAL ---
st.markdown("<h1 class='main-title'>Jaime Roldós Aguilera</h1>", unsafe_allow_html=True)
st.markdown("<p class='onichan-text'>Presentado por: Los Onichan 😎</p>", unsafe_allow_html=True)

# Panel de Misión
st.markdown(f"""
    <div style="background: rgba(255, 215, 0, 0.05); border: 2px dashed #ffd700; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
        <h3 style="color:#ffd700; margin:0; font-family:'Orbitron'">{st.session_state.mission['task']}</h3>
    </div>
""", unsafe_allow_html=True)

col_cam, col_res = st.columns([1, 1], gap="medium")

with col_cam:
    st.markdown("<div class='cyber-panel'><h4>📡 SCANNERS</h4>", unsafe_allow_html=True)
    foto = st.camera_input("Captura tu rostro", label_visibility="collapsed")
    
    if foto:
        if st.button("🔍 ANALIZAR DATOS BIOMÉTRICOS"):
            with st.spinner('⚡ PROCESANDO RED NEURONAL...'):
                res_data, processed_img, dom_emo = procesar_imagen(foto)
                
                if res_data:
                    st.session_state.res_all = res_data['emotion']
                    st.session_state.dom_emo = dom_emo
                    st.session_state.img_display = processed_img
                    
                    # Evaluar Misión
                    target = st.session_state.mission['target']
                    score = st.session_state.res_all.get(target, 0)
                    
                    if score > 60: # Umbral ajustado
                        st.session_state.mission_result = "SUCCESS"
                        st.balloons()
                    else:
                        st.session_state.mission_result = "FAIL"
                else:
                    st.warning("⚠️ No se detectó rostro humano.")
    st.markdown("</div>", unsafe_allow_html=True)

with col_res:
    if st.session_state.res_all:
        status_color = "#00ff00" if st.session_state.mission_result == "SUCCESS" else "#ff0000"
        status_msg = "✅ MISIÓN COMPLETADA" if st.session_state.mission_result == "SUCCESS" else "❌ FALLO DE MISIÓN"
        
        st.markdown(f"""
            <div class='cyber-panel' style='border-color: {status_color};'>
                <h2 style='color: {status_color}; text-align: center; margin:0;'>{status_msg}</h2>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(f"<div class='cyber-panel'><h4>ESTADO: {TRADUCCIONES.get(st.session_state.dom_emo, 'Desconocido').upper()}</h4>", unsafe_allow_html=True)
        
        # Mostrar imagen procesada
        if st.session_state.img_display is not None:
            st.image(st.session_state.img_display, use_container_width=True)

        st.markdown("---")
        st.write(f"🤖 *Humor Bot:* {random.choice(CHISTES)}")
        
        # Barras de estadística
        st.markdown("<h5>Análisis Espectral:</h5>", unsafe_allow_html=True)
        for emo_en, prob in st.session_state.res_all.items():
            if prob > 0.1:
                st.write(f"{TRADUCCIONES.get(emo_en, emo_en)}: {prob:.1f}%")
                st.markdown(f"<div class='bar-bg'><div class='bar-fill' style='width:{prob}%;'></div></div>", unsafe_allow_html=True)
        
        # Imagen de referencia (Emoji folder)
        if IMG_FOLDER.exists() and st.session_state.dom_emo:
            found_img = next((IMG_FOLDER / f for f in os.listdir(IMG_FOLDER) if f.lower().startswith(st.session_state.dom_emo.lower())), None)
            if found_img: 
                st.image(str(found_img), width=100, caption="Referencia Onichan")
        
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Esperando captura de datos...")

# --- FOOTER Y EQUIPO ---
st.divider()
st.markdown("<h3 style='text-align: center; font-family: Orbitron;'>EQUIPO: LOS ONICHAN</h3>", unsafe_allow_html=True)

nombres = ["Carlos", "Macas", "Jadiel", "Herrera"]
cols = st.columns(4)

if INTEGRANTES_FOLDER.exists():
    files_integrantes = os.listdir(INTEGRANTES_FOLDER)
    for i, nombre in enumerate(nombres):
        with cols[i]:
            img_int = next((INTEGRANTES_FOLDER / f for f in files_integrantes if nombre.lower() in f.lower()), None)
            if img_int:
                st.image(str(img_int), use_container_width=True)
            st.markdown(f"<p style='text-align: center; color: #ffd700;'>{nombre.upper()}</p>", unsafe_allow_html=True)
else:
    st.error(f"⚠️ Carpeta 'integrantes_img' no encontrada en: {INTEGRANTES_FOLDER}")

# Despedida
st.markdown("---")
if INTEGRANTES_FOLDER.exists():
    despedida_img = next((INTEGRANTES_FOLDER / f for f in os.listdir(INTEGRANTES_FOLDER) if "despedida" in f.lower()), None)
    if despedida_img:
        _, c_img, _ = st.columns([1,2,1])
        with c_img:
            st.image(str(despedida_img), use_container_width=True)
            st.markdown("""
                <div style="text-align: center; margin-top: 20px;">
                    <a href="https://www.youtube.com/watch?v=He7dSGhyeHA" target="_blank" 
                       style="background: #00f2fe; color: #0a192f; padding: 12px 24px; text-decoration: none; 
                       border-radius: 5px; font-weight: bold; font-family: 'Orbitron';">
                       📺 VER VIDEO DEL PROYECTO
                    </a>
                </div>
            """, unsafe_allow_html=True)