import os
import zipfile
import io
import json
import streamlit as st
from PIL import Image
# Logo Horizontal Ampliado
if os.path.exists("logo.jpeg"):
    col_logo, _ = st.columns([2, 1])
    with col_logo:
        st.image("logo.jpeg", width=400)
st.set_page_config(page_title="Galería Fotográfica", layout="wide")
# Estilos Personalizados en Verde Olivo
st.markdown("""
    <style>
    /* Bordes y sombras verde olivo en imágenes */
    img {
        border-radius: 8px;
        border: 2px solid #556B2F;
        box-shadow: 0px 4px 10px rgba(85, 107, 47, 0.25);
    }
    
    /* Botones principales en Verde Olivo */
    div.stButton > button:first-child {
        background-color: #556B2F !important;
        color: #FFFFFF !important;
        font-weight: bold;
        border-radius: 6px;
        border: none;
    }
    
    /* Efecto al pasar el mouse por los botones */
    div.stButton > button:first-child:hover {
        background-color: #6B8E23 !important;
        color: #FFFFFF !important;
    }
    </style>
""", unsafe_allow_html=True)
BASE_DIR = "galerias_clientes"
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

def guardar_info_evento(nombre_evento, datos):
    ruta_info = os.path.join(BASE_DIR, nombre_evento, "info.json")
    with open(ruta_info, "w") as f:
        json.dump(datos, f)

def obtener_info_evento(nombre_evento):
    ruta_info = os.path.join(BASE_DIR, nombre_evento, "info.json")
    if os.path.exists(ruta_info):
        with open(ruta_info, "r") as f:
            return json.load(f)
    return {}

st.title("📸 Sistema de Gestión y Entrega Fotográfica")

modo = st.sidebar.radio("Navegación", ["Panel Fotógrafa (Cargar Fotos)", "Portal Cliente (Ver y Descargar)"])

# ==========================================
# 1. PANEL DE LA FOTÓGRAFA
# ==========================================
if modo == "Panel Fotógrafa (Cargar Fotos)":
    st.header("📤 Cargar Nuevo Proyecto / Galería")
    
    nombre_evento = st.text_input("Nombre del Cliente o Evento (Ej: Boda_Sofia_y_Lucas)").strip()
    clave_evento = st.text_input("Contraseña de acceso para el cliente", type="password").strip()
    
    archivos_subidos = st.file_uploader(
        "Selecciona las fotos en alta resolución", 
        type=["jpg", "jpeg", "png"], 
        accept_multiple_files=True
    )
    
    if st.button("Guardar y Crear Galería"):
        if nombre_evento and clave_evento and archivos_subidos:
            ruta_evento = os.path.join(BASE_DIR, nombre_evento)
            os.makedirs(ruta_evento, exist_ok=True)
            
            for archivo in archivos_subidos:
                ruta_guardado = os.path.join(ruta_evento, archivo.name)
                with open(ruta_guardado, "wb") as f:
                    f.write(archivo.getbuffer())
            
            guardar_info_evento(nombre_evento, {"password": clave_evento, "favoritas": []})
            st.success(f"¡Éxito! Galería '{nombre_evento}' creada con contraseña.")
        else:
            st.error("Por favor completa el nombre, la contraseña y sube al menos una foto.")

    st.markdown("---")
    st.subheader("📋 Ver Selección de Clientes")
    eventos_existentes = [folder for folder in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, folder))]
    if eventos_existentes:
        evento_revisar = st.selectbox("Selecciona un evento para ver las fotos elegidas por el cliente:", eventos_existentes)
        if evento_revisar:
            info = obtener_info_evento(evento_revisar)
            favs = info.get("favoritas", [])
            if favs:
                st.write(f"**El cliente seleccionó {len(favs)} foto(s) favorita(s):**")
                for f in favs:
                    st.write(f"- {f}")
            else:
                st.info("El cliente aún no ha guardado su selección de favoritas.")
                # ==========================================
# 2. PORTAL DEL CLIENTE
# ==========================================
else:
    st.header("🖼️ Tu Galería Privada")
    
    eventos_disponibles = [folder for folder in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, folder))]
    
    if not eventos_disponibles:
        st.info("Aún no hay galerías disponibles.")
    else:
        evento_seleccionado = st.selectbox("Selecciona tu evento / proyecto:", eventos_disponibles)
        
        if evento_seleccionado:
            info_evento = obtener_info_evento(evento_seleccionado)
            clave_correcta = info_evento.get("password", "")
            
            clave_ingresada = st.text_input("Ingresa tu clave de acceso:", type="password")
            
            if clave_correcta and clave_ingresada != clave_correcta:
                st.warning("🔒 Por favor ingresa la contraseña correcta para ver esta galería.")
            else:
                st.success("🔓 Acceso concedido")
                
                ruta_galeria = os.path.join(BASE_DIR, evento_seleccionado)
                fotos = [f for f in os.listdir(ruta_galeria) if f.lower().endswith(('jpg', 'jpeg', 'png'))]
                
                st.subheader(f"Fotos de: {evento_seleccionado} ({len(fotos)} imágenes)")
                
                # Botón de Descarga ZIP
                buffer_zip = io.BytesIO()
                with zipfile.ZipFile(buffer_zip, "w") as zf:
                    for foto in fotos:
                        ruta_foto = os.path.join(ruta_galeria, foto)
                        zf.write(ruta_foto, arcname=foto)
                buffer_zip.seek(0)
                
                st.download_button(
                    label="📦 Descargar Galería Completa (.ZIP)",
                    data=buffer_zip,
                    file_name=f"{evento_seleccionado}_alta_resolucion.zip",
                    mime="application/zip",
                    use_container_width=True
                )
                
                st.markdown("---")
                
                # Mostrar fotos y capturar selección
                columnas = st.columns(3)
                favoritas_seleccionadas = []
                
                for index, foto in enumerate(fotos):
                    ruta_foto = os.path.join(ruta_galeria, foto)
                    col = columnas[index % 3]
                    
                    with col:
                        imagen = Image.open(ruta_foto)
                        st.image(imagen, use_container_width=True)
                        
                        es_fav = st.checkbox("❤️ Favorita", key=f"fav_{index}")
                        if es_fav:
                            favoritas_seleccionadas.append(foto)
                        
                        with open(ruta_foto, "rb") as file_data:
                            st.download_button(
                                label="⬇️ Descargar",
                                data=file_data,
                                file_name=foto,
                                mime="image/jpeg",
                                key=f"dl_{index}"
                            )
                
                st.markdown("---")
                if st.button("📩 Enviar / Guardar Selección de Favoritas"):
                    info_evento["favoritas"] = favoritas_seleccionadas
                    guardar_info_evento(evento_seleccionado, info_evento)
                    st.success(f"¡Selección guardada! Elegiste {len(favoritas_seleccionadas)} foto(s). La fotógrafa ya puede verlas en su panel.")
