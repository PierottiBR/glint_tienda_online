# 🛍️_Tienda.py

import streamlit as st
import pandas as pd
import os
from PIL import Image
import requests
import base64
from io import StringIO
from dotenv import load_dotenv
load_dotenv()

# --- CÓDIGO PARA OCULTAR EL SIDEBAR Y EL MAIN MENU ---
st.set_page_config(page_title="Glint Accesorios", layout="wide", page_icon="💎")

hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
/* Esta parte oculta explícitamente el sidebar */
div[data-testid="stSidebar"] {
    visibility: hidden;
    display: none;
}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
# -----------------------------------------------------

# --- CONFIGURACIÓN DE RUTAS Y API ---
# Usamos st.secrets para cargar las credenciales de forma segura
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


# --- FUNCIONES DE LECTURA DE CSV EN GITHUB ---

@st.cache_data(ttl=30) # Caching: Los datos se refrescan cada 10 minutos
def load_products_github():
    """Carga el DataFrame de productos desde el CSV en GitHub (solo lectura)."""
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
        
        # Leer el contenido como CSV
        df = pd.read_csv(StringIO(content_decoded))
        
        # Asegurarse de que las columnas numéricas sean números (importante para price y stock)
        df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0)
        df['stock'] = pd.to_numeric(df['stock'], errors='coerce').fillna(0).astype(int)
        
        return df
        
    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 404:
            st.warning("Archivo products.csv no encontrado en GitHub. Tienda vacía.")
            return default_df
        st.error(f"Error HTTP al cargar productos: {http_err}. Detalles: {response.text}")
    except Exception as e:
        st.error(f"Error cargando productos: {str(e)}")
    
    return default_df


# --- INTERFAZ: TIENDA (CLIENTE) ---
def store_page():
    
    # FUNCIONES LOCALES DENTRO DE store_page()
    def get_base64(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()

    # Obtén el base64 del logo
    # Asegúrate de que esta imagen exista en tu carpeta o usa un try/except
    try:
        banner_base64 = get_base64("Gemini_Generated_Image_fn2rx0fn2rx0fn2r (1).png")
    except FileNotFoundError:
        banner_base64 = "" # O manejar el error si la imagen no está

    # Cargar CSS
    def load_css(file_name): 
        with open(file_name, "r") as f:
            css_content = f.read() 
            st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)

    def setup_casino_theme():
        # Asegúrate de que 'casino_theme.css' exista
        try:
            load_css("casino_theme.css") 
        except FileNotFoundError:
            pass

    setup_casino_theme()

    # --- CENTRADO Y VISUALIZACIÓN DEL LOGO ---
    if banner_base64:
        st.markdown(
            f"""
            <div class="contenedor">
                <img src="data:image/png;base64,{banner_base64}" class="imagen-banner" alt="banner">
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.title("Tienda") # Fallback si no hay imagen

    st.markdown("---")
    
    # 1. Cargar Productos desde GitHub
    products_df = load_products_github()
    
    # Inicializar carrito
    if 'cart' not in st.session_state:
        st.session_state.cart = []

    # Sidebar - Carrito
    with st.sidebar:
        st.header("🛒 Tu Carrito")
        if len(st.session_state.cart) > 0:
            total = 0
            cart_df = pd.DataFrame(st.session_state.cart)
            
            # Agrupar por producto para mostrar cantidad
            grouped_cart = cart_df.groupby(['name', 'price']).size().reset_index(name='cantidad')
            
            for index, row in grouped_cart.iterrows():
                subtotal = row['price'] * row['cantidad']
                st.write(f"**{row['cantidad']}x** {row['name']} - ${subtotal:,.0f}")
                total += subtotal
            
            st.divider()
            st.subheader(f"Total: ${total:,.0f}")
            
            # Botón de Checkout (WhatsApp)
            phone_number = "549407404217" 
            message = "Hola! Quiero encargar lo siguiente:%0A"
            for index, row in grouped_cart.iterrows():
                message += f"- {row['cantidad']}x {row['name']} (${row['price']})%0A"
            message += f"%0ATotal: ${total}"
            
            whatsapp_url = f"https://wa.me/{phone_number}?text={message}"
            st.link_button("📲 Enviar Pedido por WhatsApp", whatsapp_url)
            
            if st.button("Vaciar Carrito"):
                st.session_state.cart = []
                st.rerun()
        else:
            st.info("El carrito está vacío.")

    # ============================================================
    # 2. MANEJO DE FILTROS Y CATEGORÍAS JERÁRQUICAS (ACTUALIZADO)
    # ============================================================
    
    # Filtrar solo productos con stock > 0
    available_products = products_df[products_df['stock'] > 0].copy()

    # --- LÓGICA DE SEPARACIÓN (Parsing) ---
    def split_category(val):
        if isinstance(val, str) and " - " in val:
            parts = val.split(" - ", 1)
            return parts[0], parts[1] # Retorna (Material, Tipo)
        return val, None # Retorna (Material, None) si no hay guión

    # Aplicamos la función para generar columnas temporales
    if not available_products.empty:
        available_products[['main_cat', 'sub_cat']] = available_products['category'].apply(
            lambda x: pd.Series(split_category(x))
        )
    else:
        available_products['main_cat'] = []
        available_products['sub_cat'] = []
    
    # Obtener categorías principales únicas para las PESTAÑAS (Tabs)
    main_categories = sorted(available_products['main_cat'].dropna().unique().tolist())
    tab_names = ["Todas"] + main_categories 

    # Crear las pestañas de Streamlit
    product_tabs = st.tabs(tab_names)

    # Iterar sobre las pestañas
    for i, tab_name in enumerate(tab_names):
        
        with product_tabs[i]:
            
            # --- A. Filtrado por Pestaña (Nivel 1: Material) ---
            if tab_name == "Todas":
                current_filtered_products = available_products
            else:
                current_filtered_products = available_products[available_products['main_cat'] == tab_name]
            
            # --- B. Filtrado por Subcategoría (Nivel 2: Tipo) ---
            # Solo mostramos esto si NO estamos en "Todas" y si hay subcategorías disponibles
            unique_subcats = current_filtered_products['sub_cat'].dropna().unique().tolist()
            
            if tab_name != "Todas" and len(unique_subcats) > 0:
                sub_options = ["Ver todo"] + sorted(unique_subcats)
                
                st.write("📂 **Filtrar por tipo:**")
                selected_sub = st.radio(
                    label="Selecciona tipo",
                    options=sub_options,
                    horizontal=True,
                    label_visibility="collapsed",
                    key=f"sub_filter_{i}" # Key única para cada pestaña
                )
                
                if selected_sub != "Ver todo":
                    current_filtered_products = current_filtered_products[current_filtered_products['sub_cat'] == selected_sub]
            
            st.divider() # Separador visual
            
            # --- C. Ordenamiento ---
            if not current_filtered_products.empty:
                current_filtered_products = current_filtered_products.sort_values(by='id', ascending=True)
            
            # ============================================================
            # 3. GRID DE PRODUCTOS (TU DISEÑO ORIGINAL)
            # ============================================================
            if not current_filtered_products.empty:

                cols = st.columns(3) 
                col_index = 0 # Inicializar contador manual
                
                for index, row in current_filtered_products.iterrows():
                    
                    with cols[col_index % 3]: 
                        with st.container(border=True):
                            
                            relative_path = row['image_path']
                            
                            # Construir URL Raw
                            raw_url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/{GITHUB_BRANCH}/{relative_path}"
                            
                            try:
                                if relative_path:
                                    st.image(raw_url, use_column_width=True)
                                else:
                                    st.image("https://via.placeholder.com/150?text=Sin+Foto", use_column_width=True)
                            except Exception:
                                st.image("https://via.placeholder.com/150?text=Error+Cargando", use_column_width=True)
                            
                            st.subheader(row['name'])
                            
                            # Mostrar categoría limpia (opcional: quitar el guión visualmente)
                            display_cat = row['category'].replace(" - ", " › ")
                            st.caption(display_cat)
                            
                            st.write(row['description'])
                            st.write(f"**Precio: ${row['price']:,.0f}**")
                            st.write(f"Stock: {row['stock']} un.")
                            
                            # Key única combinando Tab e ID del producto
                            if st.button(f"Agregar al Carrito", key=f"btn_{tab_name}_{row['id']}"): 
                                st.session_state.cart.append({"name": row['name'], "price": row['price']})
                                st.toast(f"{row['name']} agregado al carrito!", icon="🛍️")
                                st.rerun()

                    # Incrementar contador
                    col_index += 1
            else:
                st.info(f"No hay productos disponibles en esta sección.")

# --- MAIN APP ---
if __name__ == "__main__":
    # Eliminado init_db() y st.sidebar.image()
    store_page()