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
    # --- CSS PARA CENTRAR EL CONTENIDO ---
    def get_base64(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()

    #image_base64 = get_base64("images/background.png")
    banner_base64 = get_base64("GlintAccesoriosLogo.png")
    

    # Cargar CSS y reemplazar la variable dinámica
    def load_css(file_name, image_base64):
        with open(file_name, "r") as f:
            css_content = f.read().replace("{image_base64}", image_base64)
            st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)

    def setup_casino_theme():
        load_css("casino_theme.css")

    setup_casino_theme()

    # Mostrar el banner con HTML para asegurar que el CSS se aplique
    st.markdown(
        f"""
        <div class="contenedor">
            <img src="data:image/png;base64,{banner_base64}" class="imagen-banner" alt="banner">
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # 1. Cargar Productos desde GitHub
    products_df = load_products_github()
    
    # Inicializar carrito
    if 'cart' not in st.session_state:
        st.session_state.cart = []

    # Sidebar - Carrito (aunque el sidebar esté oculto, el contexto 'with st.sidebar:' sigue siendo útil)
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
            phone_number = "549407404217" # TU NUMERO AQUI
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

    # 2. Manejo de Filtros
    
    # Filtrar solo productos con stock > 0
    available_products = products_df[products_df['stock'] > 0]
    
    # Obtener categorías únicas
    categories = ["Todas"] + available_products['category'].dropna().unique().tolist()
    selected_cat = st.selectbox("Filtrar por categoría", categories)

    if selected_cat != "Todas":
        filtered_products = available_products[available_products['category'] == selected_cat]
    else:
        filtered_products = available_products
    
    # 3. Grid de productos
    if not filtered_products.empty:
        cols = st.columns(3) # 3 columnas por fila
        
        for index, row in filtered_products.iterrows():
            with cols[index % 3]:
                with st.container(border=True):
                    # Mostrar imagen (NOTA: Si estás en Streamlit Cloud y las imágenes 
                    # fueron subidas por el admin, las rutas locales NO funcionarán)
                    # La ruta debe ser una URL pública de la imagen.
                    image_source = row['image_path'] if row['image_path'] else "https://via.placeholder.com/150?text=Sin+Foto"
                    
                    try:
                        # Si es una ruta local, necesita Image.open, si es URL, st.image lo maneja
                        if os.path.exists(image_source):
                            image = Image.open(image_source)
                            st.image(image, use_column_width=True)
                        else:
                            # Asumimos que es una URL si no existe localmente
                            st.image(image_source, use_column_width=True)
                    except Exception:
                        st.image("https://via.placeholder.com/150?text=Error+Cargando", use_column_width=True)
                    
                    st.subheader(row['name'])
                    st.caption(row['category'])
                    st.write(row['description'])
                    st.write(f"**Precio: ${row['price']:,.0f}**")
                    st.write(f"Stock: {row['stock']} un.")
                    
                    if st.button(f"Agregar al Carrito", key=f"btn_{row['id']}"):
                        st.session_state.cart.append({"name": row['name'], "price": row['price']})
                        st.toast(f"{row['name']} agregado al carrito!", icon="🛍️")
                        st.rerun()
    else:
        st.info("No hay productos disponibles en esta categoría.")

# --- MAIN APP ---
if __name__ == "__main__":
    # Eliminado init_db() y st.sidebar.image()
    store_page()