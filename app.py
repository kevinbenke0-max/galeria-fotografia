import streamlit as st
import os
import json
import io
import zipfile
import shutil
from PIL import Image, ImageOps

# Configuración inicial
st.set_page_config(
    page_title="CAMY.INSTANTES.PH",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilo CSS para fondo blanco absoluto y limpio
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600&family=Montserrat:wght@300;400;500;600&display=swap');
    
    html, body, .stApp, header, footer, [data-testid="stHeader"], [data-testid="stToolbar"] {
        background-color: #FFFFFF !important;
        color: #1A1A1A !important;
        font-family: 'Montserrat', sans-serif !important;
    }
    
    * {
        color: #1A1A1A !important;
        font-family: 'Montserrat', sans-serif !important;
    }

    .header-marca {
        text-align: center;
        padding: 25px 0 10px 0;
        border-bottom: 1px solid #EAEAEA;
        margin-bottom: 20px;
    }
    .titulo-marca {
        font-family: 'Montserrat', sans-serif;
        font-size: 22px;
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

    .card-blanca {
        background-color: #FAFAFA !important;
        border: 1px solid #E0E0E0 !important;
        padding: 30px 20px;
        border-radius: 6px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        margin-bottom: 20px;
    }
    
    div[data-baseweb="input"], input {
        background-color: #FFFFFF !important;
        color: #1A1A1A !important;
        border: 1px solid #CCCCCC !important;
        border-radius: 4px !important;
    }

    div[data-baseweb="input"] > div, button[aria-label="Show password"], button[aria-label="Hide password"] {
        background-color: #FFFFFF !important;
        color: #1A1A1A !important;
    }

    section[data-testid="stFileUploaderDropzone"] {
        background-color: #FAFAFA !important;
        border: 1px dashed #CCCCCC !important;
    }
    section[data-testid="stFileUploaderDropzone"] * {
        background-color: transparent !important;
        color: #1A1A1A !important;
    }

    [data-testid="stFileUploaderFileData"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E0E0E0 !important;
    }

    button[data-testid="stBaseButton-primary"], .stButton > button, div[data-testid="stFormSubmitButton"] > button {
        background-color: #1A1A1A !important;
        color: #FFFFFF !important;
        border-radius: 4px !important;
        border: none !important;
        font-family: 'Montserrat', sans-serif !important;
        letter-spacing: 2px !important;
        font-size: 12px !important;
        padding: 12px 20px !important;
        text-transform: uppercase !important;
        margin-top: 10px !important;
    }

    div[data-testid="stFormSubmitButton"] > button * {
        color: #FFFFFF !important;
    }

    [data-testid="stSidebar"] {
        display: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

BASE_DIR = "galerias_clientes"
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

# Contraseña fija del panel de Camila
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

# Navegación mediante Pestañas
tab_cliente, tab_fotografo = st.tabs(["🖼 Portal Cliente", "🔒 Panel Administración"])

# =========================================================
# 1. PORTAL DEL CLIENTE
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

            # --- PORTADA Y CLAVE DE ÁLBUM ---
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
                            favs_actuales = []
                        es_fav_previo = foto in favs_actuales

                        es_fav = st.checkbox("❤️ Me gusta", value=es_fav_previo, key=f"fav_{index}_{foto}")

                        if es_fav != es_fav_previo:
                            if es_fav and foto not in favs_actuales:
                                favs_actuales.append(foto)
                            elif not es_fav and foto in favs_actuales:
                                favs_actuales.remove(foto)

                            info_evento["favoritas"] = favs_actuales
                            ruta_json = os.path.join(ruta_galeria, "info.json")
                            with open(ruta_json, "w", encoding="utf-8") as f:
                                json.dump(info_evento, f, ensure_ascii=False, indent=4)

                        with open(ruta_foto, "rb") as file_data:
                            st.download_button(
                                label="📥 Descargar",
                                data=file_data,
                                file_name=foto,
                                mime="image/jpeg",
                                key=f"dl_{index}_{foto}"
                            )

# =========================================================
# 2. PANEL DE LA FOTÓGRAFA (PROTEGIDO)
# =========================================================
with tab_fotografo:
    if not st.session_state["fotografo_autenticado"]:
        st.markdown(
            """
            <div class="card-blanca">
                <div style="font-size: 11px; letter-spacing: 2px; color: #888; text-transform: uppercase;">Acceso Restringido</div>
                <div style="font-family: 'Cormorant Garamond', serif; font-size: 28px; font-weight: 500; margin-top: 5px;">Panel de Camila</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        p_input = st.text_input("Ingresa la contraseña de Administradora:", type="password", key="pass_admin").strip()

        if st.button("INGRESAR AL PANEL", use_container_width=True):
            if p_input == PASSWORD_FOTOGRAFA:
                st.session_state["fotografo_autenticado"] = True
                st.rerun()
            else:
                st.error("Contraseña incorrecta.")

    else:
        col_admin1, col_admin2 = st.columns([3, 1])
        with col_admin1:
            st.subheader("📷 Panel de Gestión de Camila")
        with col_admin2:
            if st.button("🔴 CERRAR SESIÓN", use_container_width=True):
                st.session_state["fotografo_autenticado"] = False
                st.rerun()

        ruta_fotografo = obtener_ruta_fotografo()
        st.markdown("---")

        # --- SECCIÓN A: CARGAR ÁLBUM CON FORMULARIO PROTEGIDO ---
        st.subheader("➕ Cargar Nuevo Álbum de Cliente")
        
        with st.form("form_crear_galeria_album", clear_on_submit=True):
            nombre_evento = st.text_input("Nombre del Cliente o Evento (Ej: Boda Ayelen):").strip()
            clave_evento = st.text_input("Contraseña de acceso para el cliente:", type="password").strip()

            archivos_subidos = st.file_uploader(
                "Selecciona las fotos del álbum:",
                type=["jpg", "jpeg", "png", "webp"],
                accept_multiple_files=True
            )

            btn_guardar = st.form_submit_button("GUARDAR Y CREAR GALERÍA", use_container_width=True)

            if btn_guardar:
                if nombre_evento and clave_evento and archivos_subidos:
                    ruta_evento = os.path.join
