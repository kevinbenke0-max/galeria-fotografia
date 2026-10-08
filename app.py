import streamlit as st
import os
import json
import io
import zipfile
import shutil
from PIL import Image, ImageOps

# Configuración inicial: fondo blanco y menú lateral cerrado
st.set_page_config(
    page_title="CAMY.INSTANTES.PH",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilo CSS estético en fondo blanco (Pixieset Style)
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600&family=Montserrat:wght@300;400;500;600&display=swap');
    
    /* Fondo Blanco General */
    .stApp {
        background-color: #FFFFFF !important;
        color: #1A1A1A !important;
        font-family: 'Montserrat', sans-serif;
    }
    
    /* Forzar textos en oscuro */
    .stApp p, .stApp label, .stApp span, .stApp div, .stApp h1, .stApp h2, .stApp h3, .stApp h4 {
        color: #1A1A1A !important;
    }

    /* Encabezado Principal */
    .header-marca {
        text-align: center;
        padding: 30px 0 10px 0;
        border-bottom: 1px solid #EAEAEA;
        margin-bottom: 25px;
    }
    .titulo-marca {
        font-family: 'Montserrat', sans-serif;
        font-size: 20px;
        font-weight: 500;
        letter-spacing: 5px;
        color: #1A1A1A !important;
        text-transform: uppercase;
    }
    .subtitulo-marca {
        font-family: 'Cormorant Garamond', serif;
        font-size: 16px;
        font-style: italic;
        color: #777777 !important;
        margin-top: 5px;
    }

    /* Tarjetas Blancas */
    .card-blanca {
        background-color: #FAFAFA;
        border: 1px solid #E0E0E0;
        padding: 35px 25px;
        border-radius: 6px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
        margin-bottom: 25px;
    }
    
    /* Botones Estilizados Minimalistas */
    .stButton>button {
        background-color: #1A1A1A !important;
        color: #FFFFFF !important;
        border-radius: 2px !important;
        border: none !important;
        font-family: 'Montserrat', sans-serif !important;
        letter-spacing: 2px !important;
        font-size: 12px !important;
        padding: 10px 20px !important;
        text-transform: uppercase !important;
    }
    .stButton>button:hover {
        background-color: #333333 !important;
    }

    /* Ocultar barra lateral si se despliega */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

BASE_DIR = "galerias_clientes"
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

# Contraseña del panel de la fotógrafa
PASSWORD_FOTOGRAFA = "151124"

def obtener_ruta_fotografo():
    ruta_usr = os.path.join(BASE_DIR, "camy_instantes")
    os.makedirs(ruta_usr, exist_ok=True)
    return ruta_usr

def guardar_info_evento(nombre_evento, datos):
    ruta_usr = obtener_ruta_fotografo()
    ruta_info = os.path.join(ruta_usr, nombre_evento, "info.json")
    with open(ruta_info, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)

def obtener_info_evento_por_ruta(ruta_evento):
    ruta_info = os.path.join(ruta_evento, "info.json")
    if os.path.exists(ruta_info):
        try:
            with open(ruta_info, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

# Control de Sesión Administrativa
if "fotografo_autenticado" not in st.session_state:
    st.session_state["fotografo_autenticado"] = False

# --- ENCABEZADO PRINCIPAL ---
st.markdown(
    """
    <div class="header-marca">
        <div class="titulo-marca">CAMY.INSTANTES.PH</div>
        <div class="subtitulo-marca">Fotografía & Gestión de Entregas</div>
    </div>
    """,
    unsafe_allow_html=True
)

# Navegación mediante Pestañas Elegantes
tab_cliente, tab_fotografo = st.tabs(["🖼 Portal Cliente", "🔒 Panel Administración"])

# =========================================================
# 1. PORTAL DEL CLIENTE (ELEGANTES PORTADAS BLANCAS)
# =========================================================
with tab_cliente:
    mapa_eventos = {}
    ruta_fotografo_dir = obtener_ruta_fotografo()
    
    if os.path.exists(ruta_fotografo_dir):
        for ev in os.listdir(ruta_fotografo_dir):
            ruta_ev = os.path.join(ruta_fotografo_dir, ev)
            if os.path.isdir(ruta_ev):
                mapa_eventos[ev] = ruta_ev

    if not mapa_eventos:
        st.info("Aún no hay galerías disponibles.")
    else:
        evento_seleccionado = st.selectbox("Selecciona tu galería:", sorted(list(mapa_eventos.keys())))

        if evento_seleccionado:
            ruta_galeria = mapa_eventos[evento_seleccionado]
            info_evento = obtener_info_evento_por_ruta(ruta_galeria)
            clave_correcta = info_evento.get("password", "")

            key_acceso = f"acceso_concedido_{evento_seleccionado}"
            if key_acceso not in st.session_state:
                st.session_state[key_acceso] = False

            todas_los_archivos = sorted(os.listdir(ruta_galeria))
            fotos = [
                f for f in todas_los_archivos
                if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))
                and not f.startswith('.')
            ]

            if fotos:
                ruta_portada = os.path.join(ruta_galeria, fotos[0])
                img_portada = Image.open(ruta_portada)
                img_portada = ImageOps.exif_transpose(img_portada)
                st.image(img_portada, use_container_width=True)

            # --- TARJETA DE ACCESO CON CLAVE DE ÁLBUM ---
            if not st.session_state[key_acceso]:
                st.markdown(
                    f"""
                    <div class="card-blanca">
                        <div style="font-size: 11px; letter-spacing: 3px; color: #888; text-transform: uppercase;">CAMY.INSTANTES.PH</div>
                        <div style="font-family: 'Cormorant Garamond', serif; font-size: 38px; font-weight: 500; margin: 10px 0;">{evento_seleccionado.capitalize()}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                clave_ingresada = st.text_input("Ingresa tu clave de acceso al álbum:", type="password", key=f"pass_{evento_seleccionado}")

                if st.button("VER GALERÍA", use_container_width=True):
                    if clave_ingresada == clave_correcta:
                        st.session_state[key_acceso] = True
                        st.rerun()
                    else:
                        st.error("Contraseña incorrecta. Consulta con la fotógrafa.")

            # --- GALERÍA DESBLOQUEADA ---
            else:
                st.markdown(
                    f"""
                    <div style="text-align: left; padding: 15px 0;">
                        <span style="font-family: 'Cormorant Garamond', serif; font-size: 32px; color: #1a1a1a;">{evento_seleccionado.capitalize()}</span><br>
                        <span style="font-size: 10px; letter-spacing: 2px; color: #666; text-transform: uppercase;">CAMY.INSTANTES.PH</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # Descarga ZIP completa
                buffer = io.BytesIO()
                with zipfile.ZipFile(buffer, "w") as zip_file:
                    for foto in fotos:
                        ruta_foto = os.path.join(ruta_galeria, foto)
                        zip_file.write(ruta_foto, arcname=foto)
                buffer.seek(0)

                st.download_button(
                    label="📦 DESCARGAR GALERÍA COMPLETA (.ZIP)",
                    data=buffer,
                    file_name=f"{evento_seleccionado}_camy_instantes.zip",
                    mime="application/zip",
                    use_container_width=True
                )

                st.markdown("---")

                cols = st.columns(2)
                for index, foto in enumerate(fotos):
                    ruta_foto = os.path.join(ruta_galeria, foto)
                    col = cols[index % 2]

                    with col:
                        imagen = Image.open(ruta_foto)
                        imagen = ImageOps.exif_transpose(imagen)
                        st.image(imagen, use_container_width=True)

                        favs_actuales = info_evento.get("favoritas", [])
                        if not isinstance(favs_actuales, list):
                            favs_actuales
