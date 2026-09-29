import os
import json
import zipfile
import io
import streamlit as st
from PIL import Image

# 1. Configuración de la página
st.set_page_config(
    page_title="Galería Fotográfica Studio",
    page_icon="📸",
    layout="wide"
)

# 2. Estilo CSS para la identidad visual (Dorado y Neón)
st.markdown("""
    <style>
    /* Borde dorado y resplandor para imágenes */
    img {
        border-radius: 12px;
        border: 2px solid #D4AF37;
        box-shadow: 0px 0px 12px rgba(212, 175, 55, 0.4);
    }
    /* Estilo del botón principal */
    div.stButton > button:first-child {
        background-color: #D4AF37;
        color: #000000;
        font-weight: bold;
        border-radius: 8px;
        border: none;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Mostrar el logo en la parte superior
if os.path.exists("logo.jpeg"):
    st.image("logo.jpeg", width=220)

# 4. Carpeta base
BASE_DIR = "galerias_clientes"
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

def guardar_info_evento(nombre_evento, datos):
    ruta_info = os.path.join(BASE_DIR, nombre_evento, "info.json")
    with open(ruta_info, "w") as f:
        json.dump(datos, f, indent=4)

def obtener_info_evento(nombre_evento):
    ruta_info = os.path.join(BASE_DIR, nombre_evento, "info.json")
    if os.path.exists(ruta_info):
        with open(ruta_info, "r") as f:
            return json.load(f)
    return None

def generar_zip(ruta_galeria, lista_fotos):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zip_file:
        for foto in lista_fotos:
            path_foto = os.path.join(ruta_galeria, foto)
            if os.path.exists(path_foto):
                zip_file.write(path_foto, arcname=foto)
    buffer.seek(0)
    return buffer

# 5. Menú lateral para elegir la galería
st.sidebar.title("📌 Menú de Galerías")
eventos = [d for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d))]

if not eventos:
    st.title("Bienvenido a la Galería Studio 📸")
    st.info("No hay galerías activas en este momento. Agrega carpetas de clientes dentro de 'galerias_clientes' para comenzar.")
else:
    evento_seleccionado = st.sidebar.selectbox("Selecciona tu galería/evento:", eventos)
    
    if evento_seleccionado:
        st.title(f"🖼️ Galería: {evento_seleccionado}")
        ruta_galeria = os.path.join(BASE_DIR, evento_seleccionado)
        
        # Archivos de imagen válidos
        extensiones_validas = (".jpg", ".jpeg", ".png", ".webp")
        fotos = [f for f in os.listdir(ruta_galeria) if f.lower().endswith(extensiones_validas)]
        
        if not fotos:
            st.warning("Esta galería no contiene fotografías disponibles.")
        else:
            datos_previos = obtener_info_evento(evento_seleccionado) or {}
            favoritas_previas = datos_previos.get("seleccionadas", [])
            
            # Pestañas de la aplicación
            tab_galeria, tab_resumen, tab_descarga = st.tabs([
                "📸 Selección de Fotos", 
                "📋 Resumen de Selección", 
                "📦 Zona de Descargas"
            ])
            
            # --- PESTAÑA 1: Galería y Selección ---
            with tab_galeria:
                st.write("Marca la casilla de cada fotografía para añadirla a tu lista de seleccionadas:")
                
                with st.form("form_seleccion"):
                    seleccionadas = []
                    cols = st.columns(3)
                    
                    for index, foto in enumerate(fotos):
                        col = cols[index % 3]
                        ruta_foto = os.path.join(ruta_galeria, foto)
                        
                        with col:
                            imagen = Image.open(ruta_foto)
                            st.image(imagen, use_container_width=True)
                            
                            marcado = foto in favoritas_previas
                            if st.checkbox(f"Seleccionar ({foto})", value=marcado, key=foto):
                                sele