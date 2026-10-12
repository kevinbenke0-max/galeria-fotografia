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

BASE_DIR = "galerias_clientes"
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

# Contraseña de acceso al panel administrativo de Camila
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

# Inicializar lista temporal de fotos
if "fotos_pendientes" not in st.session_state:
    st.session_state["fotos_pendientes"] = []

# --- ENCABEZADO PRINCIPAL ---
st.markdown(
    """
    <div style="text-align: center; padding: 20px 0 10px 0; border-bottom: 1px solid #eaeaea; margin-bottom: 20px;">
        <h2 style="font-family: sans-serif; letter-spacing: 4px; margin: 0; font-size: 22px;">CAMY.INSTANTES.PH</h2>
        <p style="font-style: italic; color: #666; font-size: 14px; margin-top: 5px;">Fotografía & Gestión de Entregas</p>
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
                    <div style="border: 1px solid #e0e0e0; padding: 30px 20px; text-align: center; border-radius: 6px; margin: 15px 0; background-color: #fafafa;">
                        <span style="font-size: 11px; letter-spacing: 2px; color: #888;">CAMY.INSTANTES.PH</span>
                        <h1 style="font-size: 34px; margin: 10px 0; font-family: serif;">{evento_seleccionado.capitalize()}</h1>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                clave_ingresada = st.text_input("Ingresa tu clave de acceso al álbum:", type="password", key=f"pass_{evento_seleccionado}")

                if st.button("VER GALERÍA", use_container_width=True, type="primary"):
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
                        <h2 style="margin:0; font-family: serif; font-size: 30px;">{evento_seleccionado.capitalize()}</h2>
                        <span style="font-size: 11px; letter-spacing: 2px; color: #666;">CAMY.INSTANTES.PH</span>
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
                    ruta_foto = os.
