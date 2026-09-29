import os
import json
import streamlit as st
from PIL import Image

# 1. Configuración de la página
st.set_page_config(
    page_title="Galería Fotográfica",
    page_icon="📸",
    layout="wide"
)

# 2. Estilo CSS para borde dorado y destello en el logo
st.markdown("""
    <style>
    img {
        border-radius: 12px;
        border: 2px solid #D4AF37;
        box-shadow: 0px 0px 15px rgba(212, 175, 55, 0.4);
    }
    </style>
""", unsafe_allow_html=True)

# 3. Mostrar el logo en la parte superior
st.image("logo.jpeg", width=220)

# 4. Carpeta principal de galerías
BASE_DIR = "galerias_clientes"
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

# Funciones auxiliares para guardar y obtener datos del evento
def guardar_info_evento(nombre_evento, datos):
    ruta_info = os.path.join(BASE_DIR, nombre_evento, "info.json")
    with open(ruta_info, "w") as f:
        json.dump(datos, f)

def obtener_info_evento(nombre_evento):
    ruta_info = os.path.join(BASE_DIR, nombre_evento, "info.json")
    if os.path.exists(ruta_info):
        with open(ruta_info, "r") as f:
            return json.load(f)
    return None

# 5. Menú lateral para seleccionar la galería
st.sidebar.title("📌 Menú de Galerías")

# Listar las carpetas de eventos existentes dentro de galerias_clientes
eventos = [d for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d))]

if not eventos:
    st.title("Bienvenido a la Galería Studio 📸")
    st.info("No hay galerías activas en este momento. Agrega carpetas de clientes dentro de 'galerias_clientes' para comenzar.")
else:
    evento_seleccionado = st.sidebar.selectbox("Selecciona tu galería/evento:", eventos)
    
    if evento_seleccionado:
        st.title(f"🖼️ Galería: {evento_seleccionado}")
        
        ruta_galeria = os.path.join(BASE_DIR, evento_seleccionado)
        
        # Filtrar solo archivos de imagen
        extensiones_validas = (".jpg", ".jpeg", ".png", ".webp")
        fotos = [f for f in os.listdir(ruta_galeria) if f.lower().endswith(extensiones_validas)]
        
        if not fotos:
            st.warning("Esta galería aún no contiene fotografías.")
        else:
            # Cargar selecciones previas si existen
            datos_previos = obtener_info_evento(evento_seleccionado) or {}
            favoritas_previas = datos_previos.get("seleccionadas", [])
            
            st.write("Selecciona tus fotografías favoritas marcando la casilla de cada una:")
            
            # Formulario para guardar selecciones
            with st.form("form_seleccion"):
                seleccionadas = []
                cols = st.columns(3) # Mostrar fotos en 3 columnas
                
                for index, foto in enumerate(fotos):
                    col = cols[index % 3]
                    ruta_foto = os.path.join(ruta_galeria, foto)
                    
                    with col:
                        # Mostrar la imagen
                        imagen = Image.open(ruta_foto)
                        st.image(imagen, use_column_width=True)
                        
                        # Marcar si ya estaba seleccionada
                        marcado = foto in favoritas_previas
                        if st.checkbox(f"Seleccionar ({foto})", value=marcado, key=foto):
                            seleccionadas.append(foto)
                
                st.markdown("---")
                guardar_btn = st.form_submit_button("💾 Guardar Selección de Fotos")
                
                if guardar_btn:
                    guardar_info_evento(evento_seleccionado, {"seleccionadas": seleccionadas})
                    st.success(f"¡Selección guardada con éxito! Elegiste {len(seleccionadas)} fotos.")