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

# --- CÓDIGO PARA CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Glint Accesorios", layout="wide", page_icon="💎")

# --- CORRECCIÓN AQUÍ: CSS ---
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* CORRECCIÓN: 
   Cambiamos 'stSidebar' (que oculta todo) por 'stSidebarNav' (que oculta solo el menú de navegación).
   Esto permite que el sidebar se muestre para el Carrito, pero oculta los links a otras páginas.
*/
div[data-testid="stSidebarNav"] {
    display: none;
}

/* Ajuste para evitar parpadeos en tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
# -----------------------------------------------------

# --- CONFIGURACIÓN DE RUTAS Y API ---
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH") if os.getenv("GITHUB_BRANCH") else "main" 
TIMEOUT_API = 10 

if not GITHUB_TOKEN or not GITHUB_REPO:
    st.error("Error: Las credenciales de GitHub no se han cargado correctamente.")
    st.stop()

IMG_FOLDER = "img"
PRODUCTS_FILE = "products.csv"
PRODUCTS_PATH = f"files_csv/{PRODUCTS_FILE}"

# --- FUNCIONES DE LECTURA DE CSV EN GITHUB ---

@st.cache_data(ttl=600)
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
        
        df = pd.read_csv(StringIO(content_decoded))
        
        df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0)
        df['stock'] = pd.to_numeric(df['stock'], errors='coerce').fillna(0).astype(int)
        
        return df
        
    except Exception as e:
        st.error(f"Error cargando productos: {str(e)}")
        return default_df

# --- INTERFAZ: TIENDA (CLIENTE) ---
def store_page():
    
    # Callback para agregar al carrito sin recargar
    def add_to_cart_callback(product_name, product_price):
        st.session_state.cart.append({"name": product_name, "price": product_price})
        st.toast(f"{product_name} agregado al carrito!", icon="🛍️")

    def get_base64(image_path):
        if not os.path.exists(image_path):
            return ""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()

    # Carga de Logo
    banner_base64 = get_base64("Gemini_Generated_Image_fn2rx0fn2rx0fn2r (1).png")

    # Cargar CSS
    def load_css(file_name): 
        if os.path.exists(file_name):
            with open(file_name, "r") as f:
                css_content = f.read() 
                st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)

    load_css("casino_theme.css") 

    # --- BANNER ---
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
        st.title("Tienda")

    st.markdown("---")
    
    products_df = load_products_github()
    
    if 'cart' not in st.session_state:
        st.session_state.cart = []

    # --- SIDEBAR (Ahora debería ser visible) ---
    with st.sidebar:
        st.header("🛒 Tu Carrito")
        if len(st.session_state.cart) > 0:
            total = 0
            cart_df = pd.DataFrame(st.session_state.cart)
            
            grouped_cart = cart_df.groupby(['name', 'price']).size().reset_index(name='cantidad')
            
            for index, row in grouped_cart.iterrows():
                subtotal = row['price'] * row['cantidad']
                st.write(f"**{row['cantidad']}x** {row['name']} - ${subtotal:,.0f}")
                total += subtotal
            
            st.divider()
            st.subheader(f"Total: ${total:,.0f}")
            
            phone_number = "549407404217" 
            message = "Hola! Quiero encargar lo siguiente:%0A"
            for index, row in grouped_cart.iterrows():
                message += f"- {row['cantidad']}x {row['name']} (${row['price']})%0A"
            message += f"%0ATotal: ${total}"
            
            whatsapp_url = f"https://wa.me/{phone_number}?text={message}"
            st.link_button("📲 Enviar Pedido por WhatsApp", whatsapp_url)
            
            def clear_cart():
                st.session_state.cart = []
            
            st.button("Vaciar Carrito", on_click=clear_cart)
        else:
            st.info("El carrito está vacío.")

    # --- FILTROS Y CATEGORÍAS ---
    available_products = products_df[products_df['stock'] > 0].copy()

    def split_category(val):
        if isinstance(val, str) and " - " in val:
            parts = val.split(" - ", 1)
            return parts[0], parts[1]
        return val, None

    if not available_products.empty:
        available_products[['main_cat', 'sub_cat']] = available_products['category'].apply(
            lambda x: pd.Series(split_category(x))
        )
    else:
        available_products['main_cat'] = []
        available_products['sub_cat'] = []
    
    main_categories = sorted(available_products['main_cat'].dropna().unique().tolist())
    tab_names = ["Todas"] + main_categories 

    product_tabs = st.tabs(tab_names)

    for i, tab_name in enumerate(tab_names):
        with product_tabs[i]:
            if tab_name == "Todas":
                current_filtered_products = available_products
            else:
                current_filtered_products = available_products[available_products['main_cat'] == tab_name]
            
            unique_subcats = current_filtered_products['sub_cat'].dropna().unique().tolist()
            
            if tab_name != "Todas" and len(unique_subcats) > 0:
                sub_options = ["Ver todo"] + sorted(unique_subcats)
                st.write("📂 **Filtrar por tipo:**")
                
                selected_sub = st.radio(
                    label="Selecciona tipo",
                    options=sub_options,
                    horizontal=True,
                    label_visibility="collapsed",
                    key=f"sub_filter_{i}" 
                )
                
                if selected_sub != "Ver todo":
                    current_filtered_products = current_filtered_products[current_filtered_products['sub_cat'] == selected_sub]
            
            st.divider()
            
            if not current_filtered_products.empty:
                current_filtered_products = current_filtered_products.sort_values(by='id', ascending=True)

                cols = st.columns(3) 
                col_index = 0
                
                for index, row in current_filtered_products.iterrows():
                    with cols[col_index % 3]: 
                        with st.container(border=True):
                            relative_path = row['image_path']
                            raw_url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/{GITHUB_BRANCH}/{relative_path}"
                            
                            try:
                                if relative_path:
                                    st.image(raw_url)
                                else:
                                    st.image("https://via.placeholder.com/150?text=Sin+Foto")
                            except:
                                st.image("https://via.placeholder.com/150?text=Error")
                            
                            st.subheader(row['name'])
                            st.caption(row['category'].replace(" - ", " › "))
                            st.write(row['description'])
                            st.write(f"**Precio: ${row['price']:,.0f}**")
                            st.write(f"Stock: {row['stock']} un.")
                            
                            st.button(
                                "Agregar al Carrito", 
                                key=f"btn_{tab_name}_{row['id']}",
                                on_click=add_to_cart_callback,
                                args=(row['name'], row['price'])
                            )
                    col_index += 1
            else:
                st.info("No hay productos disponibles en esta sección.")

if __name__ == "__main__":
    store_page()