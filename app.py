import streamlit as st
import os
import json
import io
import zipfile
import shutil
import base64
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

# Variables de estado para almacenar archivos subidos
if "archivos_subidos_temp" not in st.session_state:
    st.session_state["archivos_subidos_temp"] = []

# --- ENCABEZADO PRINCIPAL ---
st.markdown(
    """
    <div style="text-align: center; padding: 20px 0 10px 0; border-bottom: 1px solid #ddd; margin-bottom: 20px;">
        <h2 style="font-family: sans-serif; letter-spacing: 4px; margin: 0;">CAMY.INSTANTES.PH</h2>
        <p style="font-style: italic; color: #666; margin-top: 5px;">Fotografía & Gestión de Entregas</p>
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
                    <div style="border: 1px solid #eee; padding: 25px; text-align: center; border-radius: 8px; margin: 15px 0;">
                        <span style="font-size: 11px; letter-spacing: 2px; color: #888;">CAMY.INSTANTES.PH</span>
                        <h1 style="font-size: 36px; margin: 10px 0;">{evento_seleccionado.capitalize()}</h1>
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
                        <h2 style="margin:0;">{evento_seleccionado.capitalize()}</h2>
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
# 2. PANEL DE LA FOTÓGRAFA
# =========================================================
with tab_fotografo:
    # --- PANTALLA DE LOGIN ---
    if not st.session_state["fotografo_autenticado"]:
        st.subheader("🔑 Acceso Restringido - Panel de Camila")
        p_input = st.text_input("Ingresa tu contraseña de Administradora:", type="password", key="pass_admin").strip()

        if st.button("INGRESAR AL PANEL", use_container_width=True, type="primary"):
            if p_input == PASSWORD_FOTOGRAFA:
                st.session_state["fotografo_autenticado"] = True
                st.rerun()
            else:
                st.error("Contraseña incorrecta.")

    # --- PANEL ADMINISTRATIVO DENTRO DE SESIÓN ---
    else:
        col_admin1, col_admin2 = st.columns([3, 1])
        with col_admin1:
            st.subheader("📷 Panel de Gestión de Camila")
        with col_admin2:
            if st.button("🔴 CERRAR SESIÓN", use_container_width=True):
                st.session_state["fotografo_autenticado"] = False
                st.session_state["archivos_subidos_temp"] = []
                st.rerun()

        ruta_fotografo = obtener_ruta_fotografo()
        st.markdown("---")

        # --- SECCIÓN A: CARGAR ÁLBUM (CARGA MÚLTIPLE COMPATIBLE CON ANDROID) ---
        st.subheader("➕ Cargar Nuevo Álbum de Cliente")
        
        nombre_evento = st.text_input("Nombre del Cliente o Evento (Ej: Boda Ayelen):").strip()
        clave_evento = st.text_input("Contraseña de acceso para el cliente:", type="password").strip()

        st.write("📸 **Selecciona las fotos de tu álbum:**")
        
        # Componente de subida múltiple alternativo
        archivos_cargados = st.file_uploader(
            "Puedes seleccionar todas las fotos juntas de la galería:",
            type=["jpg", "jpeg", "png", "webp"],
            accept_multiple_files=True,
            key=f"uploader_archivos_{nombre_evento}"
        )

        if archivos_cargados:
            st.session_state["archivos_subidos_temp"] = archivos_cargados
            st.success(f"📌 ¡Se han seleccionado **{len(archivos_cargados)}** foto(s) correctamente!")

        if st.button("GUARDAR Y CREAR GALERÍA", type="primary", use_container_width=True):
            archivos_a_guardar = st.session_state.get("archivos_subidos_temp", [])
            if nombre_evento and clave_evento and archivos_a_guardar:
                ruta_evento = os.path.join(ruta_fotografo, nombre_evento)
                os.makedirs(ruta_evento, exist_ok=True)

                for archivo in archivos_a_guardar:
                    ruta_guardado = os.path.join(ruta_evento, archivo.name)
                    with open(ruta_guardado, "wb") as f:
                        f.write(archivo.getbuffer())

                guardar_info_evento(nombre_evento, {"password": clave_evento, "favoritas": []})
                st.session_state["archivos_subidos_temp"] = []
                st.success(f"¡Éxito! El álbum '{nombre_evento}' fue creado con {len(archivos_a_guardar)} foto(s).")
                st.rerun()
            else:
                st.error("Por favor completa el nombre, la contraseña y selecciona al menos una foto.")

        st.markdown("---")

        eventos_existentes = [f for f in os.listdir(ruta_fotografo) if os.path.isdir(os.path.join(ruta_fotografo, f))]

        # --- SECCIÓN B: REVISAR FOTOS FAVORITAS ---
        st.subheader("❤️ Fotos Favoritas Elegidas por el Cliente")
        if eventos_existentes:
            evento_fav_sel = st.selectbox("Selecciona un álbum para ver sus favoritas:", eventos_existentes, key="select_fav_album")
            if evento_fav_sel:
                ruta_ev = os.path.join(ruta_fotografo,
