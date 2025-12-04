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
from dotenv import load_dotenv
load_dotenv()
from hashlib import sha256

def init_session_state():
    """Inicializa las variables de sesión"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

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
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")
# Usamos el valor por defecto 'main' si no está en las variables de entorno
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH") if os.getenv("GITHUB_BRANCH") else "main" 
TIMEOUT_API = 10 

# **VERIFICACIÓN CORREGIDA**
# Si alguna de las variables críticas es None o una cadena vacía, detenemos la app.
if not GITHUB_TOKEN or not GITHUB_REPO:
    st.error("Error: Las credenciales de GitHub (GITHUB_TOKEN y GITHUB_REPO) no se han cargado correctamente.")
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
        response_json = put_response.json() # Capturamos la respuesta JSON
        st.session_state['products_sha'] = response_json.get("content", {}).get("sha")

        # CAMBIAR: Devolver la respuesta JSON
        return response_json 
    except Exception as e:
        # ... (código de manejo de error existente) ...
        return False

def upload_image_to_github(repo, token, branch, local_path, github_path, commit_message="Admin panel: Upload image"):
    """Sube un archivo de imagen codificado en Base64 a GitHub usando la API de Contents."""
    
    try:
        # 1. Leer el contenido binario del archivo local
        with open(local_path, "rb") as image_file:
            content = image_file.read()
    except FileNotFoundError:
        st.error(f"Error: Archivo de imagen local no encontrado en {local_path}.")
        return False
        
    # 2. Codificar el contenido a Base64
    content_encoded = base64.b64encode(content).decode('utf-8')

    # 3. Preparar la solicitud
    url = f"https://api.github.com/repos/{repo}/contents/{github_path}"
    headers = {"Authorization": f"token {token}"}

    data = {
        "message": commit_message,
        "content": content_encoded,
        "branch": branch
    }

    # 4. Enviar la solicitud PUT (Crear/Actualizar)
    try:
        response = requests.put(url, headers=headers, json=data)
        response.raise_for_status() 
        return True
    except requests.exceptions.HTTPError as http_err:
        st.error(f"Error HTTP al subir imagen a GitHub: {http_err}. Detalles: {response.text}")
        return False
    except Exception as e:
        st.error(f"Error al subir imagen a GitHub: {str(e)}")
        return False
def handle_image_upload(uploaded_file, GITHUB_REPO, GITHUB_TOKEN, GITHUB_BRANCH, IMG_FOLDER):
    if uploaded_file is None:
        return None # No hay archivo para subir

    # 1. GUARDA EL ARCHIVO TEMPORALMENTE EN LA CARPETA LOCAL (Necesario para leer el binario)
    file_name = uploaded_file.name
    local_path = os.path.join(IMG_FOLDER, file_name)
    
    try:
        with open(local_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
    except Exception as e:
        st.error(f"Error al guardar el archivo local: {e}")
        return None

    # 2. SUBIR LA IMAGEN A GITHUB
    github_path = local_path # La ruta en GitHub será 'img/nombre.png'
    
    upload_success = upload_image_to_github(
        repo=GITHUB_REPO,
        token=GITHUB_TOKEN,
        branch=GITHUB_BRANCH,
        local_path=local_path,
        github_path=github_path,
        commit_message=f"Admin: Upload image {file_name}"
    )

    # 3. LIMPIAR EL ARCHIVO LOCAL (Si la subida fue exitosa, ya no lo necesitamos)
    if upload_success and os.path.exists(local_path):
        os.remove(local_path) 
        
    if upload_success:
        # Devolver la ruta relativa (ej: img/producto.png) que se guardará en el CSV
        return github_path 
    else:
        st.error("La imagen falló al subir a GitHub. Producto NO guardado.")
        return False # Devolvemos False para señalar un fallo
# --- CARGA INICIAL DE DATOS ---
if 'products_df' not in st.session_state:
    st.session_state['products_df'] = load_products_github()
def hash_password(password):
    """Crea un hash SHA-256 de la contraseña"""
    return sha256(password.encode()).hexdigest()

def check_credentials(username, password):
    """Verifica las credenciales del usuario"""
    valid_credentials = {
        'glintadmin': hash_password('epiglint123')
    }
    return (username in valid_credentials and 
            valid_credentials[username] == hash_password(password))
# --- INTERFAZ: PANEL DE ADMIN ---
st.title("🔐 Panel de Administración")
def login_page():
    """Página de inicio de sesión"""
    st.title("Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")
        
        if submit_button:
            if check_credentials(username, password):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.success("Login successful!")
                st.rerun()
            else:
                st.session_state.attempts += 1
                st.error(f"Invalid credentials! Attempt {st.session_state.attempts} of 3")
                if st.session_state.attempts >= 3:
                    st.error("Maximum login attempts reached. Please try again later.")
                    st.session_state.attempts = 0
def main():
    init_session_state()
    
    if not st.session_state.authenticated:
        login_page()
    else:
        st.title("Panel de Administración", anchor=False)    
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
    
    # 1. DEFINIMOS LA ESTRUCTURA DE CATEGORÍAS
    # Esto organiza qué subcategorías pertenecen a qué material
    CATEGORIAS_ESTRUCTURA = {
        "Acero Blanco": ["Aros", "Pulseras", "Collares", "Dijes", "Anillos"],
        "Acero Dorado": ["Aros", "Pulseras", "Collares", "Dijes", "Anillos"],
        "Acero Quirúrgico": ["Aros", "Pulseras", "Collares", "Dijes"],
        "Plata": ["Aros"],
        "Pañuelos": [],       # Sin subcategorías
        "Complementos": []    # Sin subcategorías
    }

    with st.form("add_product_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Nombre del producto")
            
            # --- NUEVA LÓGICA DE CATEGORÍAS ---
            # Selector 1: Material o Línea principal
            main_category = st.selectbox("Material / Línea", options=list(CATEGORIAS_ESTRUCTURA.keys()))
            
            # Buscamos las opciones correspondientes a la selección
            sub_options = CATEGORIAS_ESTRUCTURA[main_category]
            
            # Selector 2: Solo aparece si hay subcategorías (ej. Pañuelos no tiene)
            if sub_options:
                sub_category = st.selectbox("Tipo de producto", options=sub_options)
                # Combinamos para guardar en el CSV: "Acero Blanco - Aros"
                category_final = f"{main_category} - {sub_category}"
            else:
                # Si no hay subcategoría, se guarda solo el nombre principal
                category_final = main_category
            # ----------------------------------

            price = st.number_input("Precio ($)", min_value=0.0, step=100.0)
            
        with col2:
            stock = st.number_input("Stock Inicial", min_value=0, step=1)
            desc = st.text_area("Descripción")
            image = st.file_uploader("Foto del producto", type=["jpg", "png", "jpeg"])
            
        submitted = st.form_submit_button("Guardar Producto")
            
        if submitted:
            if name and price > 0:
                
                # LLAMADA A LA FUNCIÓN UNIFICADA
                img_path = handle_image_upload(image, GITHUB_REPO, GITHUB_TOKEN, GITHUB_BRANCH, IMG_FOLDER)
                
                # Verificar si el manejo de la imagen falló
                if img_path is False:
                    st.warning(f"Producto '{name}' no guardado debido a un error de subida de imagen.")
                    st.stop()
                
                # Calcular el nuevo ID
                next_id = df['id'].max() + 1 if not df.empty and df['id'].max() is not None else 1
                
                new_product = pd.DataFrame([{
                    'id': next_id,
                    'name': name, 
                    # AQUÍ USAMOS LA CATEGORÍA COMBINADA
                    'category': category_final, 
                    'price': price, 
                    'stock': stock, 
                    'image_path': img_path if img_path else "", 
                    'description': desc
                }])
                
                # Concatenar y guardar
                updated_df = pd.concat([df, new_product], ignore_index=True)
                
                # Guardamos y capturamos la respuesta de GitHub
                github_response = save_products_github(updated_df, f"Añadido producto: {name} ({category_final})")
                
                if github_response is not False:
                    commit_sha = github_response.get("commit", {}).get("sha", "N/A")
                    commit_url = github_response.get("commit", {}).get("html_url", "#")
                    commit_message = github_response.get("commit", {}).get("message", "Actualización.")
                    
                    st.session_state['products_df'] = updated_df 
                    
                    st.success(f"🎉 **Producto '{name}' agregado con éxito!**")
                    st.markdown(f"""
                        **Detalles:**
                        * **Categoría:** {category_final}
                        * **Commit:** `{commit_sha[:7]}`
                        * [Ver Commit en GitHub]({commit_url})
                    """)
                    
                    st.rerun()
                else:
                    st.error("El producto no pudo guardarse en el CSV de GitHub.")
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