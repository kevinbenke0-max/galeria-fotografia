import os
import base64
import json
import zipfile
import io
import shutil
import streamlit as st
from PIL import Image

st.set_page_config(page_title="Galería Fotográfica", layout="wide")
# Función para fondo de pantalla personalizado
def set_bg_hack(main_bg):
    if os.path.exists(main_bg):
        with open(main_bg, "rb") as f:
            encoded_string = base64.b64encode(f.read()).decode()
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("data:image/png;base64,{encoded_string}");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                background-attachment: fixed;
            }}
            [data-testid="stHeader"], [data-testid="stAppViewContainer"] {{
                background-color: transparent !important;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

# Aplicar la imagen de fondo
set_bg_hack("fondo.jpeg")

BASE_DIR = "galerias_clientes"
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)
USUARIOS_FILE = "usuarios.json"

def cargar_usuarios():
    if not os.path.exists(USUARIOS_FILE):
        usuarios_iniciales = {"camila": "151124"}
        with open(USUARIOS_FILE, "w") as f:
            json.dump(usuarios_iniciales, f)
        return usuarios_iniciales
    with open(USUARIOS_FILE, "r") as f:
        return json.load(f)

def registrar_usuario(usuario, password):
    usuarios = cargar_usuarios()
    usuarios[usuario.lower()] = password
    with open(USUARIOS_FILE, "w") as f:
        json.dump(usuarios, f)

def obtener_ruta_usuario(usuario):
    ruta_usr = os.path.join(BASE_DIR, usuario.lower())
    os.makedirs(ruta_usr, exist_ok=True)
    return ruta_usr

def guardar_info_evento(usuario, nombre_evento, datos):
    ruta_usr = obtener_ruta_usuario(usuario)
    ruta_info = os.path.join(ruta_usr, nombre_evento, "info.json")
    with open(ruta_info, "w") as f:
        json.dump(datos, f)

def obtener_info_evento_por_ruta(ruta_evento):
    ruta_info = os.path.join(ruta_evento, "info.json")
    if os.path.exists(ruta_info):
        with open(ruta_info, "r") as f:
            return json.load(f)
    return {}

st.title("📸 Sistema de Gestión y Entrega Fotográfica")

modo = st.sidebar.radio("Navegación", ["Panel Fotógrafa (Cargar Fotos)", "Portal Cliente (Ver y Descargar)"])
# ==========================================
# 1. PANEL DE FOTÓGRAFOS (SOLO ESTA PARTE)
# ==========================================
if modo == "Panel Fotógrafa (Cargar Fotos)":
    st.sidebar.markdown("---")
    
    opcion_cuenta = st.sidebar.radio("Acceso Fotógrafos:", ["Iniciar Sesión", "Crear Nuevo Perfil"])
    usuarios_db = cargar_usuarios()
    
    usuario_autenticado = False
    usuario_actual = ""

    if opcion_cuenta == "Iniciar Sesión":
        st.sidebar.subheader("🔑 Iniciar Sesión")
        u_input = st.sidebar.text_input("Usuario:", key="login_user").strip()
        p_input = st.sidebar.text_input("Contraseña:", type="password", key="login_pass").strip()
        
        if u_input and p_input:
            if u_input.lower() in usuarios_db and usuarios_db[u_input.lower()] == p_input:
                st.sidebar.success(f"¡Bienvenido/a, {u_input}!")
                usuario_autenticado = True
                usuario_actual = u_input
            else:
                st.sidebar.error("Usuario o contraseña incorrectos")

    elif opcion_cuenta == "Crear Nuevo Perfil":
        st.sidebar.subheader("📝 Registrar Fotógrafo/a")
        nuevo_u = st.sidebar.text_input("Nuevo Usuario:", key="reg_user").strip()
        nuevo_p = st.sidebar.text_input("Nueva Contraseña:", type="password", key="reg_pass").strip()
        
        if st.sidebar.button("Registrar Perfil"):
            if nuevo_u and nuevo_p:
                if nuevo_u.lower() in usuarios_db:
                    st.sidebar.warning("El usuario ya existe. Intenta con otro nombre.")
                else:
                    registrar_usuario(nuevo_u, nuevo_p)
                    st.sidebar.success("¡Perfil creado con éxito! Ahora ve a 'Iniciar Sesión'.")
            else:
                st.sidebar.error("Completa todos los campos.")
        if usuario_autenticado:
        st.header(f"📸 Panel de Control — {usuario_actual.capitalize()}") 
        
        ruta_fotografo = obtener_ruta_usuario(usuario_actual)
        
        st.subheader("Crear Nueva Galería de Cliente")
        nombre_evento = st.text_input("Nombre del Cliente o Evento (Ej: Boda_Sofia_y_Lucas):").strip()
        clave_evento = st.text_input("Contraseña de acceso para el cliente:", type="password").strip()
        
        archivos_subidos = st.file_uploader(
            "Selecciona las fotos en alta resolución:",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True
        )
        
        if st.button("Guardar y Crear Galería"):
            if nombre_evento and clave_evento and archivos_subidos:
                ruta_evento = os.path.join(ruta_fotografo, nombre_evento)
                os.makedirs(ruta_evento, exist_ok=True)
                
                for archivo in archivos_subidos:
                    ruta_guardado = os.path.join(ruta_evento, archivo.name)
                    with open(ruta_guardado, "wb") as f:
                        f.write(archivo.getbuffer())
                
                guardar_info_evento(usuario_actual, nombre_evento, {"password": clave_evento, "favoritas": []})
                st.success(f"¡Éxito! Galería '{nombre_evento}' creada correctamente.")
            else:
                st.error("Por favor completa el nombre, la contraseña y sube al menos una foto.")
                
        st.markdown("---")
        
        st.subheader("📋 Ver Selección de Clientes")
        eventos_existentes = [f for f in os.listdir(ruta_fotografo) if os.path.isdir(os.path.join(ruta_fotografo, f))]
        if eventos_existentes:
            evento_revisar = st.selectbox("Selecciona un evento para ver las fotos elegidas por el cliente:", eventos_existentes)
            if evento_revisar:
                ruta_ev = os.path.join(ruta_fotografo, evento_revisar)
                info = obtener_info_evento_por_ruta(ruta_ev)
                favo = info.get("favoritas", [])
                if favo:
                    st.write(f"📌 El cliente seleccionó **{len(favo)}** foto(s) favorita(s):")
                    for f in favo:
                        st.write(f"- {f}")
                else:
                    st.info("El cliente aún no ha guardado su selección de favoritas.")
        else:
            st.info("Aún no tienes galerías creadas.")

        st.markdown("---")
        st.subheader("📁 Historial de Trabajos Entregados")
        
        if eventos_existentes:
            album_ver = st.selectbox("Selecciona un álbum para revisar sus fotos:", eventos_existentes, key="ver_historial")
            if album_ver:
                ruta_album = os.path.join(ruta_fotografo, album_ver)
                fotos_album = [f for f in os.listdir(ruta_album) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
                
                st.write(f"📷 Total de fotos en **{album_ver}**: {len(fotos_album)}")
                
                cols_historial = st.columns(3)
                for idx, foto in enumerate(fotos_album):
                    col = cols_historial[idx % 3]
                    ruta_img = os.path.join(ruta_album, foto)
                    col.image(Image.open(ruta_img), caption=foto, use_container_width=True)
        else:
            st.info("Aún no has creado ninguna galería.")

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
