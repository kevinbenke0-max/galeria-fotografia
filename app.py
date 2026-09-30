import os
import json
import zipfile
import io
import base64
import shutil
import streamlit as st
from PIL import Image

# 1. Configuración de la página
st.set_page_config(
    page_title="Galería Fotográfica Studio",
    page_icon="📸",
    layout="wide"
)

# 2. Fondo de pantalla personalizado
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
            .stButton>button {{
                border-radius: 8px;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

set_bg_hack("fondo.jpeg")

# 3. Carpeta Base y Funciones Auxiliares
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
    return {}

def generar_zip(ruta_galeria, lista_fotos):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zip_file:
        for foto in lista_fotos:
            path_foto = os.path.join(ruta_galeria, foto)
            if os.path.exists(path_foto):
                zip_file.write(path_foto, arcname=foto)
    buffer.seek(0)
    return buffer
    # 4. Menú Lateral
st.sidebar.title("📌 Menú Principal")
modo = st.sidebar.radio("Modo de acceso:", ["👤 Cliente (Ver Galería)", "📸 Fotógrafo (Administración)"])

# CREDENCIALES DEL FOTÓGRAFO
USUARIO_CORRECTO = "Camila"
PASSWORD_CORRECTO = "151124"

# ---------------------------------------------------------
# MODO FOTÓGRAFO (ADMINISTRACIÓN)
# ---------------------------------------------------------
if modo == "📸 Fotógrafo (Administración)":
    st.title("⚙️️ Panel de Administración")
    
    st.sidebar.subheader("Inicio de Sesión")
    usuario_input = st.sidebar.text_input("Usuario:")
    password_input = st.sidebar.text_input("Contraseña:", type="password")
    
    if usuario_input.strip().lower() == USUARIO_CORRECTO.lower() and password_input == PASSWORD_CORRECTO:
        st.success(f"Bienvenida, {USUARIO_CORRECTO}.")
        
        tab_crear, tab_subir, tab_eliminar = st.tabs([
            "➕ Crear Galería", 
            "📤 Cargar Fotos", 
            "🗑️ Eliminar Galería"
        ])
        
        with tab_crear:
            st.subheader("1. Crear Nueva Galería")
            nuevo_evento = st.text_input("Nombre del evento / galería (ej: 15_Anos_Sofia):")
            clave_galeria = st.text_input("Contraseña para el cliente (opcional):", type="password")
            
            if st.button("Crear Galería"):
                if nuevo_evento.strip() != "":
                    ruta_nueva = os.path.join(BASE_DIR, nuevo_evento.strip())
                    if not os.path.exists(ruta_nueva):
                        os.makedirs(ruta_nueva)
                        guardar_info_evento(nuevo_evento.strip(), {"password": clave_galeria.strip(), "favoritas": []})
                        st.success(f"Galería '{nuevo_evento}' creada con éxito.")
                        st.rerun()
                    else:
                        st.warning("Esa galería ya existe.")
                else:
                    st.error("Ingresa un nombre válido.")
        
        with tab_subir:
            st.subheader("2. Cargar Fotografías")
            eventos_existentes = [d for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d))]
            
            if eventos_existentes:
                evento_destino = st.selectbox("Selecciona la galería:", eventos_existentes)
                archivos_subidos = st.file_uploader("Selecciona imágenes:", type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=True)
                
                if st.button("Guardar Fotos"):
                    if archivos_subidos:
                        ruta_destino = os.path.join(BASE_DIR, evento_destino)
                        for foto in archivos_subidos:
                            with open(os.path.join(ruta_destino, foto.name), "wb") as f:
                                f.write(foto.getbuffer())
                        st.success(f"Se subieron {len(archivos_subidos)} fotos a '{evento_destino}'.")
                    else:
                        st.error("Selecciona al menos una foto.")
            else:
                st.info("Crea una galería primero.")

        with tab_eliminar:
            st.subheader("3. Eliminar Galería Completa")
            eventos_existentes = [d for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d))]
            
            if eventos_existentes:
                evento_a_borrar = st.selectbox("Selecciona la galería a eliminar:", eventos_existentes, key="borrar_select")
                confirmacion = st.checkbox(f"Confirmo eliminar '{evento_a_borrar}'")
                
                if st.button("🗑️ Eliminar Definitivamente"):
                    if confirmacion:
                        shutil.rmtree(os.path.join(BASE_DIR, evento_a_borrar))
                        st.success(f"Galería '{evento_a_borrar}' eliminada.")
                        st.rerun()
                    else:
                        st.error("Marca la casilla para confirmar.")
            else:
                st.info("No hay galerías para eliminar.")
                else:
        if usuario_input != "" or password_input != "":
            st.error("Usuario o contraseña incorrectos.")
        else:
            st.info("Ingresa con tu usuario y contraseña en la barra lateral.")
# ---------------------------------------------------------
# MODO CLIENTE (VER GALERÍA Y DAR ME GUSTA)
# ---------------------------------------------------------
else:
    eventos = [d for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d))]
    
    if not eventos:
        st.title("Bienvenido a la Galería Studio 📸")
        st.info("No hay galerías disponibles en este momento.")
    else:
        evento_seleccionado = st.sidebar.selectbox("Selecciona tu galería:", eventos)
        
        if evento_seleccionado:
            ruta_galeria = os.path.join(BASE_DIR, evento_seleccionado)
            info_evento = obtener_info_evento(evento_seleccionado)
            clave_requerida = info_evento.get("password", "")
            
            # Verificación de clave del álbum
            acceso_concedido = True
            if clave_requerida:
                clave_ingresada = st.sidebar.text_input(f"Contraseña de '{evento_seleccionado}':", type="password", key=f"pass_{evento_seleccionado}")
                if clave_ingresada != clave_requerida:
                    acceso_concedido = False
                    st.title(f"🖼️ Galería: {evento_seleccionado}")
                    st.warning("Por favor, ingresa la contraseña de la galería en el menú lateral para ver las fotos.")

            if acceso_concedido:
                st.title(f"🖼️ Galería: {evento_seleccionado}")
                
                extensiones_validas = (".jpg", ".jpeg", ".png", ".webp")
                fotos = [f for f in os.listdir(ruta_galeria) if f.lower().endswith(extensiones_validas)]
                
                if not fotos:
                    st.warning("Esta galería aún no contiene fotografías.")
                else:
                    # Cargar lista de "me gusta" guardadas
                    favoritas = info_evento.get("favoritas", [])
                    
                    st.subheader(f"❤️ Fotos seleccionadas: {len(favoritas)} de {len(fotos)}")
                    
                    # Botón para descargar selección en ZIP
                    col_top1, col_top2 = st.columns([2, 1])
                    with col_top2:
                        if favoritas:
                            zip_buffer = generar_zip(ruta_galeria, favoritas)
                            st.download_button(
                                label="📦 Descargar 'Me gusta' (.ZIP)",
                                data=zip_buffer,
                                file_name=f"{evento_seleccionado}_mis_favoritas.zip",
                                mime="application/zip",
                                use_container_width=True
                            )
                    
                    st.markdown("---")
                    
                    # Grilla sencilla de fotografías con botón Me Gusta / Descargar
                    cols = st.columns(3)
                    for index, foto in enumerate(fotos):
                        col = cols[index % 3]
                        ruta_foto = os.path.join(ruta_galeria, foto)
                        es_favorita = foto in favoritas
                        
                        with col:
                            imagen = Image.open(ruta_foto)
                            st.image(imagen, use_container_width=True)
                            
                            c1, c2 = st.columns(2)
                            with c1:
                                label_btn = "❤️ Me gusta" if es_favorita else "🤍 Me gusta"
                                if st.button(label_btn, key=f"like_{foto}"):
                                    if es_favorita:
                                        favoritas.remove(foto)
                                    else:
                                        favoritas.append(foto)
                                    info_evento["favoritas"] = favoritas
                                    guardar_info_evento(evento_seleccionado, info_evento)
                                    st.rerun()
                                    with c2:
                                with open(ruta_foto, "rb") as file_foto:
                                    st.download_button(
                                        label="⬇️ Descargar",
                                        data=file_foto,
                                        file_name=foto,
                                        mime="image/jpeg",
                                        key=f"dl_{foto}"
                                    )
