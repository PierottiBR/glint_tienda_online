# pages/⚙️_Panel_Admin.py

import streamlit as st
import sqlite3
import pandas as pd
import os
from PIL import Image
import shutil

# --- IMPORTAR CONFIGURACIÓN Y FUNCIONES DESDE EL ARCHIVO PRINCIPAL ---
# Nota: En una aplicación real, las funciones DB irían en un módulo separado, 
# pero por simplicidad de este ejemplo, las definimos aquí nuevamente o las importaríamos.
# Para este setup de Streamlit multi-page simple, es mejor duplicar las funciones 
# de DB y Configuración para asegurar que todo funcione si se accede directamente a la página.

DB_NAME = "bijoutery.db"
IMG_FOLDER = "img"

if not os.path.exists(IMG_FOLDER):
    os.makedirs(IMG_FOLDER)

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

def save_uploaded_file(uploaded_file):
    if uploaded_file is not None:
        file_path = os.path.join(IMG_FOLDER, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return file_path
    return None

# Inicializar DB al inicio de la página de admin también
init_db()


# --- INTERFAZ: PANEL DE ADMIN ---
st.title("🔐 Panel de Administración")
    
# Login simple
password = st.sidebar.text_input("Contraseña de Admin", type="password")
if password != "admin123": # CAMBIAR ESTO EN PRODUCCIÓN
    st.warning("Introduce la contraseña correcta para acceder.")
    # El emoji y el nombre del archivo se mostrarán en la barra lateral.
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/6491/6491546.png", width=100)
    st.stop() # Detiene la ejecución del resto del script si la contraseña es incorrecta

st.sidebar.success("Acceso concedido")
    
tab1, tab2 = st.tabs(["➕ Agregar Producto", "📝 Editar/Eliminar Inventario"])

# Pestaña 1: Agregar
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
                run_query('''
                    INSERT INTO products (name, category, price, stock, image_path, description)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (name, category, price, stock, img_path, desc))
                st.success(f"Producto '{name}' agregado correctamente.")
                st.rerun()
            else:
                st.error("El nombre y el precio son obligatorios.")

# Pestaña 2: Editar
with tab2:
    st.subheader("Gestión de Inventario")
    df = run_query("SELECT * FROM products", return_data=True)
    
    if not df.empty:
        # Edición rápida de Stock y Precio usando Data Editor
        st.info("Edita las celdas y presiona 'Guardar Cambios' abajo.")
        edited_df = st.data_editor(
            df, 
            column_config={
                "image_path": st.column_config.ImageColumn("Foto Preview"),
                "price": st.column_config.NumberColumn("Precio", format="$%.2f"),
            },
            disabled=["id"],
            hide_index=True,
            key="editor"
        )
        
        col_btn1, col_btn2 = st.columns(2)
        
        if col_btn1.button("💾 Guardar Cambios en Stock/Precio"):
            # Iterar sobre el DF editado y actualizar DB
            for index, row in edited_df.iterrows():
                run_query('''
                    UPDATE products SET price = ?, stock = ?, name = ?, description = ?
                    WHERE id = ?
                ''', (row['price'], row['stock'], row['name'], row['description'], row['id']))
            st.success("Base de datos actualizada.")
            st.rerun()

        # Sección de Borrar
        st.divider()
        st.write("Eliminar producto")
        product_to_delete = st.selectbox("Selecciona producto a eliminar", df['name'].values)
        if st.button("🗑️ Eliminar Producto"):
            # Primero recupera la ruta de la imagen para borrarla si existe
            img_to_delete = df[df['name'] == product_to_delete]['image_path'].iloc[0]
            
            # Borrar de la base de datos
            run_query("DELETE FROM products WHERE name = ?", (product_to_delete,))
            
            # Borrar archivo de imagen (si existe y no es None)
            if img_to_delete and os.path.exists(img_to_delete):
                os.remove(img_to_delete)
                
            st.warning(f"{product_to_delete} eliminado.")
            st.rerun()
    else:
        st.info("No hay productos cargados aún.")