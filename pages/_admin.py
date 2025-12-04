# pages/⚙️_Panel_Admin.py

import streamlit as st
import pandas as pd
import os
from PIL import Image
import shutil
import requests
import base64
from io import StringIO
import json # Necesario para manejar la respuesta JSON de la API

# --- CÓDIGO PARA OCULTAR EL SIDEBAR Y EL MAIN MENU ---
st.set_page_config(page_title="Bijoutery Glam - Admin", layout="wide", page_icon="⚙️")
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
div[data-testid="stSidebar"] {
    visibility: hidden;
    display: none;
}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
# -----------------------------------------------------

# --- CONFIGURACIÓN DE RUTAS Y API (AJUSTAR SEGÚN TU ENTORNO) ---
# Usamos st.secrets para las credenciales en Streamlit Cloud
try:
    GITHUB_REPO = st.secrets["github"]["repo"]
    GITHUB_TOKEN = st.secrets["github"]["token"]
    GITHUB_BRANCH = st.secrets.get("github", {}).get("branch", "main")
    TIMEOUT_API = st.secrets.get("github", {}).get("timeout", 10)
except KeyError:
    st.error("Error: Las credenciales de GitHub no están configuradas en `st.secrets`.")
    st.stop()


IMG_FOLDER = "img"
PRODUCTS_FILE = "products.csv"
PRODUCTS_PATH = f"files_csv/{PRODUCTS_FILE}" # Ruta dentro de GitHub

# Asegurar que existe la carpeta de imágenes (para desarrollo local)
if not os.path.exists(IMG_FOLDER):
    os.makedirs(IMG_FOLDER)

# --- FUNCIONES DE MANIPULACIÓN DE CSV EN GITHUB ---

def load_products_github():
    """Carga el DataFrame de productos desde el CSV en GitHub."""
    default_columns = ['id', 'name', 'category', 'price', 'stock', 'image_path', 'description']
    default_df = pd.DataFrame(columns=default_columns)
    
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{PRODUCTS_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    try:
        response = requests.get(url, headers=headers, timeout=TIMEOUT_API)
        response.raise_for_status()
        
        file_info = response.json()
        content_encoded = file_info["content"].replace('\n', '')
        content_decoded = base64.b64decode(content_encoded).decode('utf-8')
        
        # Guardamos el SHA para la posterior actualización
        st.session_state['products_sha'] = file_info.get("sha")
        
        # Leer el contenido como CSV
        return pd.read_csv(StringIO(content_decoded))
        
    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 404:
            st.warning("Archivo products.csv no encontrado en GitHub, creando DataFrame vacío.")
            st.session_state['products_sha'] = None
            return default_df
        st.error(f"Error HTTP al cargar productos: {http_err}. Detalles: {response.text}")
    except Exception as e:
        st.error(f"Error cargando productos: {str(e)}")
    
    st.session_state['products_sha'] = None
    return default_df

def save_products_github(df, commit_message="Actualización de Inventario"):
    """Guarda el DataFrame de productos en el CSV de GitHub."""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{PRODUCTS_PATH}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    try:
        # 1. Obtener SHA del session_state
        sha = st.session_state.get('products_sha')

        # 2. Preparar contenido CSV
        csv_content = df.to_csv(index=False)
        encoded_content = base64.b64encode(csv_content.encode('utf-8')).decode()

        # 3. Crear payload
        data = {
            "message": commit_message,
            "content": encoded_content,
            "branch": GITHUB_BRANCH,
        }
        if sha:
            data["sha"] = sha # Solo se incluye si el archivo ya existe

        # 4. Enviar actualización
        put_response = requests.put(url, headers=headers, json=data, timeout=TIMEOUT_API)
        put_response.raise_for_status()
        
        # Actualizar SHA para futuras operaciones
        st.session_state['products_sha'] = put_response.json().get("content", {}).get("sha")

        return True
    except Exception as e:
        error_details = ""
        if 'put_response' in locals():
             error_details = f"Detalles: {put_response.text}"
        st.error(f"Error guardando productos en GitHub: {str(e)}. {error_details}")
        return False

def save_uploaded_file(uploaded_file):
    # NOTA: En un entorno de producción real, DEBES subir la imagen a un 
    # servicio de almacenamiento en la nube (S3, Cloudinary) y guardar su URL, 
    # ya que la carpeta 'img' también es efímera en Streamlit Cloud.
    # Por ahora, mantenemos la lógica local para el desarrollo:
    if uploaded_file is not None:
        file_path = os.path.join(IMG_FOLDER, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return file_path
    return None

# --- CARGA INICIAL DE DATOS ---
if 'products_df' not in st.session_state:
    st.session_state['products_df'] = load_products_github()

# --- INTERFAZ: PANEL DE ADMIN ---
st.title("🔐 Panel de Administración")
    
# Login simple (Usamos el antiguo st.sidebar para simular un input fuera de la pantalla principal)
# Ocultamos este input usando el CSS anterior, pero el componente st.sidebar.text_input sigue
# siendo una forma útil de manejar inputs de login fuera del flujo de la app.
password = st.sidebar.text_input("Contraseña de Admin", type="password")
if password != "admin123": # CAMBIAR ESTO EN PRODUCCIÓN
    # Solo mostramos el warning en la pantalla principal si el login falla
    if password:
        st.warning("Introduce la contraseña correcta para acceder.")
    st.stop() 

# st.sidebar.success("Acceso concedido") # Ya no se usa el sidebar

# Cargamos el DF de la sesión
df = st.session_state['products_df'].copy()
    
tab1, tab2 = st.tabs(["➕ Agregar Producto", "📝 Editar/Eliminar Inventario"])

# --- Pestaña 1: Agregar Producto ---
with tab1:
    st.subheader("Nuevo Producto")
    with st.form("add_product_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Nombre del producto")
            category = st.selectbox("Categoría", ["Collares", "Pulseras", "Anillos", "Aros", "Conjuntos"])
            price = st.number_input("Precio ($)", min_value=0.0, step=100.0)
        with col2:
            stock = st.number_input("Stock Inicial", min_value=0, step=1)
            desc = st.text_area("Descripción")
            image = st.file_uploader("Foto del producto", type=["jpg", "png", "jpeg"])
            
        submitted = st.form_submit_button("Guardar Producto")
            
        if submitted:
            if name and price > 0:
                img_path = save_uploaded_file(image)
                
                # Calcular el nuevo ID
                next_id = df['id'].max() + 1 if not df.empty and df['id'].max() is not None else 1
                
                new_product = pd.DataFrame([{
                    'id': next_id,
                    'name': name, 
                    'category': category, 
                    'price': price, 
                    'stock': stock, 
                    'image_path': img_path if img_path else "", # Guardar la ruta local o URL de la imagen
                    'description': desc
                }])
                
                # Concatenar y guardar
                updated_df = pd.concat([df, new_product], ignore_index=True)
                
                if save_products_github(updated_df, f"Añadido producto: {name}"):
                    st.session_state['products_df'] = updated_df # Actualizar sesión
                    st.success(f"Producto '{name}' agregado correctamente y guardado en GitHub.")
                    st.rerun()
            else:
                st.error("El nombre y el precio son obligatorios.")

# --- Pestaña 2: Editar/Eliminar Inventario ---
with tab2:
    st.subheader("Gestión de Inventario")
    
    if not df.empty:
        # --- Edición Rápida ---
        st.info("Edita las celdas y presiona 'Guardar Cambios' abajo.")
        # Reconfiguramos las columnas para mayor legibilidad
        column_config = {
            "id": st.column_config.NumberColumn("ID"),
            "name": st.column_config.TextColumn("Nombre"),
            "category": st.column_config.TextColumn("Categoría"),
            "price": st.column_config.NumberColumn("Precio", format="$%.2f"),
            "stock": st.column_config.NumberColumn("Stock", format="%d"),
            "description": st.column_config.TextColumn("Descripción"),
            "image_path": st.column_config.TextColumn("Ruta Imagen")
        }
        
        edited_df = st.data_editor(
            df, 
            column_config=column_config,
            disabled=["id"],
            hide_index=True,
            key="editor_inventory"
        )
        
        # Filtrar si hubo cambios reales (Streamlit data_editor compara automáticamente)
        if edited_df.equals(df):
            st.info("No se han detectado cambios en el editor.")
        
        if st.button("💾 Guardar Cambios en Stock/Precio"):
            if save_products_github(edited_df, "Actualización masiva de inventario"):
                st.session_state['products_df'] = edited_df # Actualizar sesión
                st.success("Inventario actualizado y guardado en GitHub.")
                st.rerun()

        # --- Sección de Borrar ---
        st.divider()
        st.write("Eliminar producto")
        
        product_names = df['name'].tolist()
        product_to_delete_name = st.selectbox("Selecciona producto a eliminar", product_names, key="delete_selector")
        
        if st.button("🗑️ Eliminar Producto"):
            if product_to_delete_name:
                # Obtener la ruta de la imagen antes de eliminar la fila
                img_to_delete = df[df['name'] == product_to_delete_name]['image_path'].iloc[0]
                
                # Filtrar el DataFrame para eliminar el producto
                updated_df = df[df['name'] != product_to_delete_name].reset_index(drop=True)
                
                if save_products_github(updated_df, f"Eliminado producto: {product_to_delete_name}"):
                    st.session_state['products_df'] = updated_df # Actualizar sesión
                    
                    # Borrar archivo de imagen (si existe y es local)
                    if img_to_delete and os.path.exists(img_to_delete):
                        os.remove(img_to_delete)
                        
                    st.warning(f"Producto '{product_to_delete_name}' eliminado y guardado en GitHub.")
                    st.rerun()
            else:
                st.warning("Selecciona un producto para eliminar.")
    else:
        st.info("No hay productos cargados en el inventario.")