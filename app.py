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

# 2. Función para fondo de pantalla
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

# Aplicar fondo
set_bg_hack("fondo.jpeg")

# 3. Carpeta Base y Funciones
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
    # 4. Menú Lateral (Navegación)
st.sidebar.title("📌 Menú Principal")
modo = st.sidebar.radio("Modo de acceso:", ["👤 Cliente (Ver Galería)", "📸 Fotógrafo (Administración)"])

# CREDENCIALES DEL FOTÓGRAFO
USUARIO_CORRECTO = "Camila"
PASSWORD_CORRECTO = "151124"

# MODO FOTÓGRAFO
if modo == "📸 Fotógrafo (Administración)":
    st.title("⚙️ Panel de Administración")
    
    st.sidebar.subheader("Inicio de Sesión")
    usuario_input = st.sidebar.text_input("Usuario:")
    password_input = st.sidebar.text_input("Contraseña:", type="password")
    
    if usuario_input == USUARIO_CORRECTO and password_input == PASSWORD_CORRECTO:
        st.success(f"Bienvenida, {USUARIO_CORRECTO}.")
        
        tab_crear, tab_subir, tab_eliminar = st.tabs([
            "➕ Crear Galería", 
            "📤 Cargar Fotos", 
            "🗑️ Eliminar Galería"
        ])
        
        with tab_crear:
            st.subheader("1. Crear Nueva Galería")
            nuevo_evento = st.text_input("Nombre de la nueva galería (ej: 15_Anos_Sofia):")
            if st.button("Crear Galería"):
                if nuevo_evento.strip() != "":
                    ruta_nueva = os.path.join(BASE_DIR, nuevo_evento.strip())
                    if not os.path.exists(ruta_nueva):
                        os.makedirs(ruta_nueva)
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
                evento_destino = st.selectbox("Selecciona la galería para subir fotos:", eventos_existentes)
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
                evento_a_borrar = st.selectbox("Selecciona la galería que deseas eliminar:", eventos_existentes, key="borrar_select")
                st.warning(f"⚠️ Atención: Esta acción eliminará permanentemente la carpeta '{evento_a_borrar}' y todas las fotos contenidas en ella.")
                
                confirmacion = st.checkbox(f"Confirmo que deseo eliminar definitivamente '{evento_a_borrar}'")
                
                if st.button("🗑️ Eliminar Galería definitivamente"):
                    if confirmacion:
                        ruta_borrar = os.path.join(BASE_DIR, evento_a_borrar)
                        try:
                            shutil.rmtree(ruta_borrar)
                            st.success(f"La galería '{evento_a_borrar}' ha sido eliminada.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al eliminar la galería: {e}")
                    else:
                        st.error("Por favor, marca la casilla de confirmación para proceder.")
            else:
                st.info("No hay galerías para eliminar.")

    else:
        if usuario_input != "" or password_input != "":
            st.error("Usuario o contraseña incorrectos.")
        else:
            st.info("Ingresa el usuario y la contraseña en la barra lateral para acceder.")
            # MODO CLIENTE
else:
    eventos = [d for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d))]
    
    if not eventos:
        st.title("Bienvenido a la Galería Studio 📸")
        st.info("No hay galerías activas en este momento.")
    else:
        evento_seleccionado = st.sidebar.selectbox("Selecciona tu galería:", eventos)
        
        if evento_seleccionado:
            st.title(f"🖼️ Galería: {evento_seleccionado}")
            ruta_galeria = os.path.join(BASE_DIR, evento_seleccionado)
            
            extensiones_validas = (".jpg", ".jpeg", ".png", ".webp")
            fotos = [f for f in os.listdir(ruta_galeria) if f.lower().endswith(extensiones_validas)]
            
            if not fotos:
                st.warning("Esta galería aún no contiene fotografías.")
            else:
                datos_previos = obtener_info_evento(evento_seleccionado) or {}
                favoritas_previas = datos_previos.get("seleccionadas", [])
                
                tab_galeria, tab_resumen, tab_descarga = st.tabs([
                    "📸 Selección de Fotos", 
                    "📋 Resumen de Selección", 
                    "📦 Zona de Descargas"
                ])
                
                with tab_galeria:
                    st.write("Marca la casilla de cada fotografía para añadirla a tu lista:")
                    
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
                                    seleccionadas.append(foto)
                        
                        st.markdown("---")
                        guardar_btn = st.form_submit_button("💾 Guardar Selección de Fotos")
                        
                        if guardar_btn:
                            guardar_info_evento(evento_seleccionado, {"seleccionadas": seleccionadas})
                            st.success(f"¡Selección guardada! Elegiste {len(seleccionadas)} foto(s).")
                
                with tab_resumen:
                    st.subheader("Fotos Seleccionadas Hasta el Momento")
                    datos_actuales = obtener_info_evento(evento_seleccionado) or {}
                    lista_sel = datos_actuales.get("seleccionadas", [])
                    
                    if not lista_sel:
                        st.info("Aún no se ha guardado ninguna foto en esta galería.")
                    else:
                        st.write(f"**Total elegidas:** {len(lista_sel)} de {len(fotos)}")
                        st.json(lista_sel)
                
                with tab_descarga:
                    st.subheader("Opciones de Descarga")
                    datos_actuales = obtener_info_evento(evento_seleccionado) or {}
                    lista_sel = datos_actuales.get("seleccionadas", [])
                    
                    col_d1, col_d2 = st.columns(2)
                    
                    with col_d1:
                        st.markdown("##### 📄 Exportar lista (JSON)")
                        str_json = json.dumps({"evento": evento_seleccionado, "seleccionadas": lista_sel}, indent=4)
                        st.download_button(
                            label="Descargar info.json",
                            data=str_json,
                            file_name=f"{evento_seleccionado}_seleccion.json",
                        mime="application/json"
                        )
                    
                    with col_d2:
                        st.markdown("##### 📦 Descargar fotos seleccionadas (.ZIP)")
                        if lista_sel:
                            zip_buffer = generar_zip(ruta_galeria, lista_sel)
                            st.download_button(
                                label="Descargar Fotos (.ZIP)",
                                data=zip_buffer,
                                file_name=f"{evento_seleccionado}_fotos_seleccionadas.zip",
                                mime="application/zip"
                            )
                        else:
                            st.caption("Selecciona al menos una foto para descargar en ZIP.")
