# pages/⚙️_Panel_Admin.py

import streamlit as st
import pandas as pd
import os
from PIL import Image
import requests
import base64
from io import StringIO
import json
from dotenv import load_dotenv
from hashlib import sha256
import time
# Cargar variables de entorno
load_dotenv()

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Bijoutery Glam - Admin", layout="wide", page_icon="⚙️")

# Ocultar elementos de Streamlit
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

# --- VARIABLES Y CREDENCIALES ---
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH") if os.getenv("GITHUB_BRANCH") else "main"
TIMEOUT_API = 10 
IMG_FOLDER = "img"
PRODUCTS_FILE = "products.csv"
PRODUCTS_PATH = f"files_csv/{PRODUCTS_FILE}"
CATEGORIES_FILE = "categories.json" # <--- AGREGAR ESTA VARIABLE
CATEGORIES_PATH = f"files_csv/{CATEGORIES_FILE}"
# Validación de credenciales
if not GITHUB_TOKEN or not GITHUB_REPO:
    st.error("Error: Las credenciales de GitHub (GITHUB_TOKEN y GITHUB_REPO) no se han cargado correctamente.")
    st.stop()

# Asegurar carpeta local temporal
if not os.path.exists(IMG_FOLDER):
    os.makedirs(IMG_FOLDER)

# --- FUNCIONES DE AUTENTICACIÓN ---
def init_session_state():
    """Inicializa las variables de sesión"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'products_df' not in st.session_state:
        st.session_state['products_df'] = load_products_github()
    # --- NUEVO: CARGAR CATEGORÍAS ---
    if 'categories_data' not in st.session_state:
        st.session_state['categories_data'] = load_categories_github()
    if 'username' not in st.session_state:
        st.session_state.username = ""
    if 'attempts' not in st.session_state:
        st.session_state.attempts = 0

def hash_password(password):
    return sha256(password.encode()).hexdigest()

def check_credentials(username, password):
    # Credenciales hardcodeadas (Idealmente mover a secrets)
    valid_credentials = {
        'glintadmin': hash_password('epiglint123')
    }
    return (username in valid_credentials and 
            valid_credentials[username] == hash_password(password))

# --- FUNCIONES DE GITHUB ---

# --- FUNCIONES PARA CATEGORÍAS (JSON) ---
def load_categories_github():
    # Estructura por defecto si no existe el archivo aún
    default_categories = {
        "Acero Blanco": ["Aros", "Pulseras", "Collares", "Dijes", "Anillos"],
        "Acero Dorado": ["Aros", "Pulseras", "Collares", "Dijes", "Anillos"],
        "Acero Quirúrgico": ["Aros", "Pulseras", "Collares", "Dijes"],
        "Plata": ["Aros"],
        "Pañuelos": [],
        "Complementos": []
    }
    
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{CATEGORIES_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    try:
        response = requests.get(url, headers=headers, timeout=TIMEOUT_API)
        response.raise_for_status()
        
        file_info = response.json()
        content_encoded = file_info["content"].replace('\n', '')
        content_decoded = base64.b64decode(content_encoded).decode('utf-8')
        
        st.session_state['categories_sha'] = file_info.get("sha")
        return json.loads(content_decoded) # Convertimos texto a Diccionario Python
        
    except Exception:
        # Si falla (404 no existe), devolvemos el default y el SHA nulo
        st.session_state['categories_sha'] = None
        return default_categories

def save_categories_github(categories_dict, commit_message="Actualización de Categorías"):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{CATEGORIES_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    try:
        sha = st.session_state.get('categories_sha')
        # Convertir diccionario a JSON texto
        json_content = json.dumps(categories_dict, indent=4, ensure_ascii=False)
        encoded_content = base64.b64encode(json_content.encode('utf-8')).decode()

        data = {
            "message": commit_message,
            "content": encoded_content,
            "branch": GITHUB_BRANCH,
        }
        if sha:
            data["sha"] = sha

        response = requests.put(url, headers=headers, json=data, timeout=TIMEOUT_API)
        response.raise_for_status()
        
        # Actualizar SHA
        response_json = response.json()
        st.session_state['categories_sha'] = response_json.get("content", {}).get("sha")
        return True
    except Exception as e:
        st.error(f"Error guardando categorías: {e}")
        return False
    
    
def load_products_github():
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
        
        st.session_state['products_sha'] = file_info.get("sha")
        
        return pd.read_csv(StringIO(content_decoded))
        
    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 404:
            st.warning("Archivo products.csv no encontrado, creando uno nuevo.")
            st.session_state['products_sha'] = None
            return default_df
        st.error(f"Error HTTP al cargar productos: {http_err}")
    except Exception as e:
        st.error(f"Error cargando productos: {str(e)}")
    
    st.session_state['products_sha'] = None
    return default_df

def save_products_github(df, commit_message="Actualización de Inventario"):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{PRODUCTS_PATH}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    try:
        sha = st.session_state.get('products_sha')
        csv_content = df.to_csv(index=False)
        encoded_content = base64.b64encode(csv_content.encode('utf-8')).decode()

        data = {
            "message": commit_message,
            "content": encoded_content,
            "branch": GITHUB_BRANCH,
        }
        if sha:
            data["sha"] = sha

        put_response = requests.put(url, headers=headers, json=data, timeout=TIMEOUT_API)
        put_response.raise_for_status()
        
        response_json = put_response.json()
        # Actualizar SHA inmediatamente para evitar conflictos en guardados consecutivos
        st.session_state['products_sha'] = response_json.get("content", {}).get("sha")

        return response_json
    except Exception as e:
        st.error(f"Error al guardar en GitHub: {e}")
        return False

def upload_image_to_github(repo, token, branch, local_path, github_path, commit_message="Admin panel: Upload image"):
    try:
        with open(local_path, "rb") as image_file:
            content = image_file.read()
    except FileNotFoundError:
        return False
        
    content_encoded = base64.b64encode(content).decode('utf-8')
    url = f"https://api.github.com/repos/{repo}/contents/{github_path}"
    headers = {"Authorization": f"token {token}"}
    data = {
        "message": commit_message,
        "content": content_encoded,
        "branch": branch
    }

    try:
        response = requests.put(url, headers=headers, json=data)
        response.raise_for_status()
        return True
    except Exception as e:
        st.error(f"Error subiendo imagen: {e}")
        return False

def handle_image_upload(uploaded_file, GITHUB_REPO, GITHUB_TOKEN, GITHUB_BRANCH, IMG_FOLDER):
    if uploaded_file is None:
        return None

    file_name = uploaded_file.name
    # Usar IMG_FOLDER local temporalmente
    local_path = os.path.join(IMG_FOLDER, file_name)
    
    try:
        with open(local_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
    except Exception as e:
        st.error(f"Error al guardar localmente: {e}")
        return None

    # Ruta relativa para el CSV y GitHub
    github_path = f"img/{file_name}" # Asegurar estructura 'img/archivo.jpg'
    
    upload_success = upload_image_to_github(
        repo=GITHUB_REPO,
        token=GITHUB_TOKEN,
        branch=GITHUB_BRANCH,
        local_path=local_path,
        github_path=github_path,
        commit_message=f"Admin: Upload image {file_name}"
    )

    if os.path.exists(local_path):
        os.remove(local_path)
        
    if upload_success:
        return github_path
    else:
        return False

# --- PÁGINAS ---
def login_page():
    st.title("Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")
        
        if submit_button:
            if check_credentials(username, password):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.attempts = 0
                st.success("Login successful!")
                st.rerun()
            else:
                st.session_state.attempts += 1
                st.error(f"Credenciales inválidas. Intento {st.session_state.attempts} de 3")
                if st.session_state.attempts >= 3:
                    st.error("Máximos intentos alcanzados.")

def main():
    init_session_state()
    
    if not st.session_state.authenticated:
        login_page()
    else:
        st.title("Panel de Administración", anchor=False)    

        # Cargar DF de sesión
        df = st.session_state['products_df'].copy()
            
        tab1, tab2 = st.tabs(["➕ Agregar Producto", "📝 Editar/Eliminar Inventario"])

        # --- Pestaña 1: Agregar Producto ---
        with tab1:
            st.subheader("Nuevo Producto")
            # ---------------------------------------------------------
            # SECCIÓN 1: GESTOR DE CATEGORÍAS (NUEVO)
            # ---------------------------------------------------------
            with st.expander("📂 ¿Necesitas una categoría nueva? Créala aquí"):
                st.write("Agrega una nueva línea (ej: Oro) o un nuevo tipo (ej: Tobillera en Acero Blanco).")
                c_cat1, c_cat2, c_cat3 = st.columns([2, 2, 1])
                
                # Obtener diccionario actual
                current_cats = st.session_state['categories_data']
                
                with c_cat1:
                    # Opción para crear nueva Categoría Principal o seleccionar existente
                    opcion_creacion = st.radio("¿Qué quieres agregar?", ["Nuevo Tipo en categoría existente", "Nueva Línea/Material completa"])
                
                with c_cat2:
                    if opcion_creacion == "Nueva Línea/Material completa":
                        new_main_cat = st.text_input("Nombre de la nueva Línea (ej: Oro 18k)")
                        new_sub_cat_optional = st.text_input("Primer tipo (Opcional, ej: Anillos)")
                    else:
                        # Seleccionar existente
                        cat_parent = st.selectbox("Selecciona la Línea existente", list(current_cats.keys()))
                        new_sub_type = st.text_input("Nombre del nuevo tipo (ej: Tobilleras)")

                with c_cat3:
                    st.write("") # Espacio vertical
                    st.write("")
                    if st.button("➕ Crear Categoría"):
                        updated = False
                        if opcion_creacion == "Nueva Línea/Material completa":
                            if new_main_cat and new_main_cat not in current_cats:
                                # Crear nueva lista
                                current_cats[new_main_cat] = [new_sub_cat_optional] if new_sub_cat_optional else []
                                updated = True
                            elif new_main_cat in current_cats:
                                st.warning("Esa categoría ya existe.")
                        else:
                            if new_sub_type and new_sub_type not in current_cats[cat_parent]:
                                current_cats[cat_parent].append(new_sub_type)
                                updated = True
                            elif new_sub_type in current_cats[cat_parent]:
                                st.warning("Ese tipo ya existe en esta categoría.")

                        if updated:
                            if save_categories_github(current_cats, "Nueva categoría añadida"):
                                st.session_state['categories_data'] = current_cats
                                st.success("Categoría actualizada!")
                                time.sleep(1)
                                st.rerun()

            st.divider()

            with st.form("add_product_form", clear_on_submit=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    name = st.text_input("Nombre del producto")
                    
                    # --- USAMOS LOS DATOS DINÁMICOS AQUÍ ---
                    cats_data = st.session_state['categories_data']
                    main_keys = list(cats_data.keys())
                    
                    main_category = st.selectbox("Material / Línea", options=main_keys)
                    
                    # Obtener subtipos según selección
                    sub_options = cats_data.get(main_category, [])
                    
                    if sub_options:
                        sub_category = st.selectbox("Tipo de producto", options=sub_options)
                        category_final = f"{main_category} - {sub_category}"
                    else:
                        # Caso: Categoría sin hijos (ej: Pañuelos)
                        st.write(f"Categoría: {main_category}") 
                        category_final = main_category
                    # ---------------------------------------

                    price = st.number_input("Precio ($)", min_value=0.0, step=100.0)
                    
                with col2:
                    stock = st.number_input("Stock Inicial", min_value=0, step=1)
                    desc = st.text_area("Descripción")
                    image = st.file_uploader("Foto del producto", type=["jpg", "png", "jpeg"])
                    
                submitted = st.form_submit_button("Guardar Producto")
                    
                if submitted:
                    if name and price > 0:
                        
                        # Subir imagen
                        img_path = handle_image_upload(image, GITHUB_REPO, GITHUB_TOKEN, GITHUB_BRANCH, IMG_FOLDER)
                        if img_path is False:
                            st.warning(f"Error al subir la imagen. Intenta de nuevo.")
                            st.stop()
                        
                        next_id = df['id'].max() + 1 if not df.empty and pd.notna(df['id'].max()) else 1
                        
                        new_product = pd.DataFrame([{
                            'id': next_id,
                            'name': name, 
                            'category': category_final, 
                            'price': price, 
                            'stock': stock, 
                            'image_path': img_path if img_path else "", 
                            'description': desc
                        }])
                        
                        updated_df = pd.concat([df, new_product], ignore_index=True)
                        
                        github_response = save_products_github(updated_df, f"Añadido producto: {name} ({category_final})")
                        
                        if github_response:
                            st.session_state['products_df'] = updated_df 
                            st.success(f"🎉 **Producto '{name}' agregado con éxito!**")
                            st.rerun()
                        else:
                            st.error("El producto no pudo guardarse en el CSV de GitHub.")
                    else:
                        st.error("El nombre y el precio son obligatorios.")

        # --- Pestaña 2: Editar/Eliminar Inventario ---
        with tab2:
            st.subheader("Gestión de Inventario")
            
            if not df.empty:
                st.info("Edita las celdas y presiona 'Guardar Cambios' abajo.")
                
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
                
                if st.button("💾 Guardar Cambios en Stock/Precio"):
                    if not edited_df.equals(df):
                        if save_products_github(edited_df, "Actualización masiva de inventario"):
                            st.session_state['products_df'] = edited_df
                            st.success("Inventario actualizado en GitHub.")
                            st.rerun()
                    else:
                        st.info("No hay cambios para guardar.")

                st.divider()
                st.write("### Eliminar producto")
                
                product_names = df['name'].tolist()
                product_to_delete_name = st.selectbox("Selecciona producto a eliminar", product_names, key="delete_selector")
                
                if st.button("🗑️ Eliminar Producto"):
                    if product_to_delete_name:
                        # Filtrar para eliminar
                        updated_df = df[df['name'] != product_to_delete_name].reset_index(drop=True)
                        
                        if save_products_github(updated_df, f"Eliminado producto: {product_to_delete_name}"):
                            st.session_state['products_df'] = updated_df
                            st.success(f"Producto '{product_to_delete_name}' eliminado del listado.")
                            st.rerun()
                    else:
                        st.warning("Selecciona un producto.")
            else:
                st.info("No hay productos cargados en el inventario.")

if __name__ == "__main__":
    main()