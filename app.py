import os
import zipfile
import io
import json
import streamlit as st
from PIL import Image

# Configuración de la página
st.set_page_config(
    page_title="Galería Fotográfica",
    page_icon="📸",
    layout="wide"
)

# Muestra el logo arriba de todo
st.image("logo.jpeg", width=250)

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
    return None