import streamlit as st
import os
import json
import io
import zipfile
import shutil
from PIL import Image, ImageOps

# Configuración inicial (inicia con el menú lateral cerrado para evitar molestias en celulares)
st.set_page_config(
    page_title="Panel de Fotografía",
    layout="wide",
    initial_sidebar_state="collapsed"
)

BASE_DIR = "galerias_clientes"
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

USUARIOS_FILE = "usuarios.json"

def cargar_usuarios():
    if not os.path.exists(USUARIOS_FILE):
        usuarios_iniciales = {"camila": "151124"}
        with open(USUARIOS_FILE, "w", encoding="utf-8") as f:
            json.dump(usuarios_iniciales, f)
        return usuarios_iniciales
    with open(USUARIOS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def registrar_usuario(usuario, password):
    usuarios = cargar_usuarios()
    usuarios[usuario.lower()] = password
    with open(USUARIOS_FILE, "w", encoding="utf-8") as f:
        json.dump(usuarios, f)

def obtener_ruta_usuario(usuario):
    ruta_usr = os.path.join(BASE_DIR, usuario.lower())
    os.makedirs(ruta_usr, exist_ok=True)
    return ruta_usr

def guardar_info_evento(usuario, nombre_evento, datos):
    ruta_usr = obtener_ruta_usuario(usuario)
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

# Control de Sesión
if "usuario_autenticado" not in st.session_state:
    st.session_state["usuario_autenticado"] = False
if "usuario_actual" not in st.session_state:
    st.session_state["usuario_actual"] = ""

st.title("📸 Sistema de Gestión y Entrega Fotográfica")

# Navegación principal
tab_fotografo, tab_cliente = st.tabs(["📸 Panel Fotógrafa", "🖼 Portal Cliente"])

# =========================================================
# 1. PANEL DE LA FOTÓGRAFA
# =========================================================
with tab_fotografo:
    usuarios_db = cargar_usuarios()

    # --- PANTALLA DE ACCESO/LOGIN ---
    if not st.session_state["usuario_autenticado"]:
        st.subheader("🔑 Acceso al Panel")
        opcion_cuenta = st.radio("Elige una opción:", ["Iniciar Sesión", "Crear Nuevo Perfil"], horizontal=True)

        if opcion_cuenta == "Iniciar Sesión":
            u_input = st.text_input("Usuario:", key="login_user").strip()
            p_input = st.text_input("Contraseña:", type="password", key="login_pass").strip()

            if st.button("Ingresar al Panel", type="primary", use_container_width=True):
                if u_input and p_input:
                    if u_input.lower() in usuarios_db and usuarios_db[u_input.lower()] == p_input:
                        st.session_state["usuario_autenticado"] = True
                        st.session_state["usuario_actual"] = u_input
                        st.rerun()
                    else:
                        st.error("Usuario o contraseña incorrectos")
                else:
                    st.warning("Por favor completa ambos campos.")

        elif opcion_cuenta == "Crear Nuevo Perfil":
            nuevo_u = st.text_input("Nuevo Usuario:", key="reg_user").strip()
            nuevo_p = st.text_input("Nueva Contraseña:", type="password", key="reg_pass").strip()

            if st.button("Registrar Perfil", use_container_width=True):
                if nuevo_u and nuevo_p:
                    if nuevo_u.lower() in usuarios_db:
                        st.warning("El usuario ya existe. Intenta con otro nombre.")
                    else:
                        registrar_usuario(nuevo_u, nuevo_p)
                        st.success("¡Perfil creado con éxito! Ahora cambia a 'Iniciar Sesión' para ingresar.")
                else:
                    st.error("Completa todos los campos.")

    # --- PANEL DENTRO DE LA SESIÓN ---
    else:
        usuario_actual = st.session_state["usuario_actual"]

        col_header, col_logout = st.columns([3, 1])
        with col_header:
            st.header(f"📷 Bienvenida, {usuario_actual.capitalize()}")
        with col_logout:
            if st.button("🔴 Cerrar Sesión", use_container_width=True):
                st.session_state["usuario_autenticado"] = False
                st.session_state["usuario_actual"] = ""
                st.rerun()

        ruta_fotografo = obtener_ruta_usuario(usuario_actual)

        st.markdown("---")

        # --- SECCIÓN A: CREAR NUEVO ÁLBUM (CARGA MÚLTIPLE HABILITADA) ---
        st.subheader("➕ Cargar Nuevo Álbum de Cliente")
        nombre_evento = st.text_input("Nombre del Cliente o Evento (Ej: Boda Ayelen):").strip()
        clave_evento = st.text_input("Contraseña de acceso para el cliente:", type="password").strip()

        st.info("💡 **Consejo en celulares:** Mantén presionada la primera foto en la galería de tu teléfono para activar la selección múltiple y elegir todas las fotos juntas.")
# Carga múltiple optimizada para celulares
archivos_subidos = st.file_uploader(
    "Selecciona las fotos del álbum:",
    type=["jpg", "jpeg", "png", "webp"],
    accept_multiple_files=True,
    key="uploader_album"
)

# Permitir agregar más fotos en lotes si el celular no envió todas juntas
if "fotos_acumuladas" not in st.session_state:
    st.session_state["fotos_acumuladas"] = []

if archivos_subidos:
    for f in archivos_subidos:
        if f not in st.session_state["fotos_acumuladas"]:
            st.session_state["fotos_acumuladas"].append(f)

# Guardar y procesar la lista completa de imágenes acumuladas
if st.session_state["fotos_acumuladas"]:
    st.write(f"📁 **{len(st.session_state['fotos_acumuladas'])}** foto(s) seleccionada(s) en total.")
    if st.button("❌ Limpiar selección"):
        st.session_state["fotos_acumuladas"] = []
        st.rerun()
if st.button("Guardar y Crear Galería", type="primary"):
    fotos_a_guardar = st.session_state.get("fotos_acumuladas", [])
    if nombre_evento and clave_evento and fotos_a_guardar:
        ruta_evento = os.path.join(ruta_fotografo, nombre_evento)
        os.makedirs(ruta_evento, exist_ok=True)

        for archivo in fotos_a_guardar:
            ruta_guardado = os.path.join(ruta_evento, archivo.name)
            with open(ruta_guardado, "wb") as f:
                f.write(archivo.getbuffer())

        guardar_info_evento(usuario_actual, nombre_evento, {"password": clave_evento, "favoritas": []})
        st.session_state["fotos_acumuladas"] = []  # Limpiar la lista tras guardar
        st.success(f"¡Éxito! El álbum '{nombre_evento}' fue creado con {len(fotos_a_guardar)} foto(s).")
        st.rerun()
    else:
        st.error("Por favor ingresa el nombre, la contraseña y selecciona al menos una foto.")

        st.markdown("---")

        eventos_existentes = [f for f in os.listdir(ruta_fotografo) if os.path.isdir(os.path.join(ruta_fotografo, f))]

        # --- SECCIÓN B: REVISAR FOTOS FAVORITAS ---
        st.subheader("❤️ Fotos Favoritas Elegidas por el Cliente")
        if eventos_existentes:
            evento_fav_sel = st.selectbox("Selecciona un álbum para ver sus favoritas:", eventos_existentes, key="select_fav_album")
            if evento_fav_sel:
                ruta_ev = os.path.join(ruta_fotografo, evento_fav_sel)
                info = obtener_info_evento_por_ruta(ruta_ev)
                favs = info.get("favoritas", [])

                if favs:
                    st.write(f"📌 El cliente eligió **{len(favs)}** foto(s) favorita(s):")
                    cols_fav = st.columns(4)
                    for idx, f in enumerate(favs):
                        ruta_fav = os.path.join(ruta_ev, f)
                        col = cols_fav[idx % 4]
                        if os.path.exists(ruta_fav):
                            img_fav = Image.open(ruta_fav)
                            img_fav = ImageOps.exif_transpose(img_fav)
                            col.image(img_fav, caption=f, use_container_width=True)
                        else:
                            col.write(f"📷 {f}")
                else:
                    st.info("El cliente aún no ha seleccionado fotos favoritas en este álbum.")
        else:
            st.info("Aún no tienes álbumes creados.")

        st.markdown("---")

        # --- SECCIÓN C: TRABAJOS Y GESTIÓN EN 4 COLUMNAS CON OPON DE BORRAR ---
        st.subheader("📁 Todos mis Trabajos")
        if eventos_existentes:
            album_ver = st.selectbox("Selecciona un álbum para explorar sus fotos:", eventos_existentes, key="ver_historial")
            
            if album_ver:
                ruta_album = os.path.join(ruta_fotografo, album_ver)
                fotos_album = [f for f in os.listdir(ruta_album) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]

                st.write(f"📷 Total de fotos en **{album_ver}**: {len(fotos_album)}")

                # Opción para eliminar trabajo
                with st.expander("🗑️ Opciones / Borrar Trabajo"):
                    st.warning(f"¿Deseas eliminar permanentemente la carpeta '{album_ver}' y todas sus fotos?")
                    if st.button("Eliminar Álbum Completo", key=f"del_{album_ver}"):
                        shutil.rmtree(ruta_album)
                        st.success(f"La carpeta '{album_ver}' ha sido eliminada.")
                        st.rerun()

                # Despliegue en 4 columnas con opción para agrandar
                cols_historial = st.columns(4)
                for idx, foto in enumerate(fotos_album):
                    col = cols_historial[idx % 4]
                    ruta_img = os.path.join(ruta_album, foto)
                    
                    with col:
                        img_hist = Image.open(ruta_img)
                        img_hist = ImageOps.exif_transpose(img_hist)
                        st.image(img_hist, caption=foto, use_container_width=True)
                        
                        with st.popover("🔍 Agrandar"):
                            st.image(img_hist, caption=foto, use_container_width=True)
        else:
            st.info("No hay trabajos guardados actualmente.")

# =========================================================
# 2. PORTAL DEL CLIENTE (DISEÑO PIXIESET)
# =========================================================
with tab_cliente:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600&display=swap');
        
        .card-portada {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            padding: 40px 20px;
            text-align: center;
            border-radius: 4px;
            margin-top: 20px;
            margin-bottom: 30px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }
        .marca-fotografo {
            font-family: 'Helvetica Neue', sans-serif;
            font-size: 11px;
            letter-spacing: 3px;
            color: #666666;
            text-transform: uppercase;
            margin-bottom: 15px;
        }
        .titulo-evento {
            font-family: 'Cormorant Garamond', serif;
            font-size: 42px;
            font-weight: 500;
            color: #1a1a1a;
            margin: 10px 0;
            line-height: 1.1;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    mapa_eventos = {}
    if os.path.exists(BASE_DIR):
        for usr in os.listdir(BASE_DIR):
            ruta_usr = os.path.join(BASE_DIR, usr)
            if os.path.isdir(ruta_usr):
                for ev in os.listdir(ruta_usr):
                    ruta_ev = os.path.join(ruta_usr, ev)
                    if os.path.isdir(ruta_ev):
                        mapa_eventos[ev] = {"ruta": ruta_ev, "fotografo": usr}

    if not mapa_eventos:
        st.info("Aún no hay galerías disponibles.")
    else:
        evento_seleccionado = st.selectbox("Selecciona tu galería:", sorted(list(mapa_eventos.keys())))

        if evento_seleccionado:
            datos_galeria = mapa_eventos[evento_seleccionado]
            ruta_galeria = datos_galeria["ruta"]
            nombre_fotografo = datos_galeria["fotografo"]

            marca_fotografa = "CAMY.INSTANTES.PH" if nombre_fotografo.lower() in ["camila", "camy"] else f"{nombre_fotografo.upper()}.PH"

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

            # --- TARJETA DE PORTADA ---
            if not st.session_state[key_acceso]:
                st.markdown(
                    f"""
                    <div class="card-portada">
                        <div class="marca-fotografo">{marca_fotografa}</div>
                        <div class="titulo-evento">{evento_seleccionado.capitalize()}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                clave_ingresada = st.text_input("Ingresa tu clave de acceso:", type="password", key=f"pass_{evento_seleccionado}")

                if st.button("VER GALERÍA", type="primary", use_container_width=True):
                    if clave_ingresada == clave_correcta:
                        st.session_state[key_acceso] = True
                        st.rerun()
                    else:
                        st.error("Contraseña incorrecta. Intenta de nuevo.")

            # --- VISTA DESBLOQUEADA DE FOTOS ---
            else:
                st.markdown(
                    f"""
                    <div style="text-align: left; padding: 20px 0;">
                        <span style="font-family: 'Cormorant Garamond', serif; font-size: 32px; color: #1a1a1a;">{evento_seleccionado.capitalize()}</span><br>
                        <span style="font-family: 'Helvetica Neue', sans-serif; font-size: 10px; letter-spacing: 2px; color: #666; text-transform: uppercase;">{marca_fotografa}</span>
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
                    label="📦 Descargar Galería Completa (.ZIP)",
                    data=buffer,
                    file_name=f"{evento_seleccionado}_alta_resolucion.zip",
                    mime="application/zip",
                    use_container_width=True
                )

                st.markdown("---")

                columnas = st.columns(2)

                for index, foto in enumerate(fotos):
                    ruta_foto = os.path.join(ruta_galeria, foto)
                    col = columnas[index % 2]

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
