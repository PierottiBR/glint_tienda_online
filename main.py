# 🛍️_Tienda.py

import streamlit as st
import sqlite3
import pandas as pd
import os
from PIL import Image
# import shutil # shutil ya no es necesario si no borras archivos

# --- CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="Bijoutery Glam", layout="wide", page_icon="💎")
DB_NAME = "bijoutery.db"
IMG_FOLDER = "img"

# Asegurar que existe la carpeta de imágenes (para desarrollo local)
if not os.path.exists(IMG_FOLDER):
    os.makedirs(IMG_FOLDER)

# --- FUNCIONES DE BASE DE DATOS (Mantenidas por ahora) ---
# ... (deja todas tus funciones init_db y run_query aquí, son compartidas) ...
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            price REAL,
            stock INTEGER,
            image_path TEXT,
            description TEXT
        )
    ''')
    conn.commit()
    conn.close()

def run_query(query, params=(), return_data=False):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(query, params)
    if return_data:
        data = c.fetchall()
        columns = [desc[0] for desc in c.description]
        conn.close()
        return pd.DataFrame(data, columns=columns)
    conn.commit()
    conn.close()

# --- FUNCIONES AUXILIARES ---
# ... (deja tu función save_uploaded_file aquí) ...
def save_uploaded_file(uploaded_file):
    if uploaded_file is not None:
        file_path = os.path.join(IMG_FOLDER, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return file_path
    return None


# --- INTERFAZ: TIENDA (CLIENTE) ---
def store_page():
    st.title("💎 Tienda de Bijoutery & Accesorios")
    
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

    # Filtros
    # Asegúrate de que init_db se ejecute si es la primera vez
    init_db() 
    categories = ["Todas"] + [r[0] for r in run_query("SELECT DISTINCT category FROM products", return_data=True).values.tolist()]
    selected_cat = st.selectbox("Filtrar por categoría", categories)

    query = "SELECT * FROM products WHERE stock > 0"
    params = ()
    if selected_cat != "Todas":
        query += " AND category = ?"
        params = (selected_cat,)
    
    products = run_query(query, params, return_data=True)

    # Grid de productos
    if not products.empty:
        cols = st.columns(3) # 3 columnas por fila
        for index, row in products.iterrows():
            with cols[index % 3]:
                with st.container(border=True):
                    # Mostrar imagen si existe
                    if row['image_path'] and os.path.exists(row['image_path']):
                        try:
                            image = Image.open(row['image_path'])
                            st.image(image, use_column_width=True)
                        except:
                            st.error("Error cargando imagen")
                    else:
                        st.image("https://via.placeholder.com/150?text=Sin+Foto", use_column_width=True)
                    
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

# --- MAIN APP (MODIFICADO) ---
if __name__ == "__main__":
    init_db() # Asegura que la DB exista al inicio de la app
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/6491/6491546.png", width=100)
    # Ya no necesitas el radio button de navegación, Streamlit lo hace automáticamente
    store_page()