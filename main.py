import streamlit as st
import base64

st.set_page_config(page_title="Glint Accesorios", page_icon=":stars:", layout="wide")

# === Cargar imagen PNG y convertir a base64 ===
logo_path = "GlintAccesoriosLogo.png"  # tu imagen
with open(logo_path, "rb") as f:
    logo_base64 = base64.b64encode(f.read()).decode()

# === Mostrar logo centrado ===
st.markdown(
    f"""
    <style>
        .contenedor {{
            display: flex;
            justify-content: center;
            align-items: center;
            background-color: transparent !important;
        }}
        .imagen-banner {{
            width: 30%;
            height: auto;
            background-color: transparent !important;
        }}
        /* Quitar fondo oscuro general */
        [data-testid="stAppViewContainer"] {{
            background-color: Black !important;
        }}
    </style>
    <div class="contenedor">
        <img src="data:image/png;base64,{logo_base64}" class="imagen-banner" alt="banner">
    </div>
    """,
    unsafe_allow_html=True
)

# === Mostrar título sin clamp ni ícono ===
st.markdown(
    """
    <p style='text-align: center; color: #d4af37; font-weight: 800; font-size: 2rem; margin-top: 15px;'>
        Glint Accesorios
    </p>
    """,
    unsafe_allow_html=True
)


from PIL import Image

# Función para ajustar imágenes al mismo tamaño y centrar
def ajustar_imagen(path, size=(300, 300)):
    img = Image.open(path)
    img.thumbnail(size)  # mantiene proporción
    fondo = Image.new("RGBA", size, (255, 255, 255, 0))  # fondo transparente
    x = (size[0] - img.width) // 2
    y = (size[1] - img.height) // 2
    fondo.paste(img, (x, y), img if img.mode == 'RGBA' else None)
    return fondo

# Lista de productos con id
productos = [
    {
        "id": "aros_cubanos",
        "imagen": "accesorios/aros/aroscubanos.png",
        "nombre": "Aros Cubanos",
        "detalles": ["• 1,5 Cm", "• Acero dorado"],
        "url": "https://wa.me/5493407404217?text=Hola,%20estoy%20interesado%20en%20el%20aros%20cubanos"
    },
    {
        "id": "aros_flor",
        "imagen": "accesorios/aros/arosflor.png",
        "nombre": "Aros Flor",
        "detalles": ["• 1,5 Cm", "• Acero dorado"],
        "url": "https://wa.me/5493407404217?text=Hola,%20estoy%20interesado%20en%20el%20aros%20flor"
    },
    {
        "id": "aros_cereza",
        "imagen": "accesorios/aros/aroscereza.png",
        "nombre": "Aros Cereza",
        "detalles": ["• 1,5 Cm", "• Acero dorado"],
        "url": "https://wa.me/5493407404217?text=Hola,%20estoy%20interesado%20en%20el%20aros%20cereza"
    }
]

# Crear columnas
col1, col2, col3 = st.columns(3)

# Columna 1
with col1:
    contenedor = st.container(border=True)
    with contenedor:
        prod = next(p for p in productos if p["id"] == "aros_cubanos")
        img = ajustar_imagen(prod["imagen"])
        st.image(img, caption=prod["nombre"], width='stretch')
        st.write(f"**{prod['nombre']}**")
        for detalle in prod["detalles"]:
            st.write(detalle)
        st.link_button(label="Comprar", url=prod["url"],width='stretch')

# Columna 2
with col2:
    contenedor = st.container(border=True)
    with contenedor:
        prod = next(p for p in productos if p["id"] == "aros_flor")
        img = ajustar_imagen(prod["imagen"])
        st.image(img, caption=prod["nombre"],width='stretch')
        st.write(f"**{prod['nombre']}**")
        for detalle in prod["detalles"]:
            st.write(detalle)
        st.link_button(label="Comprar", url=prod["url"],width='stretch')

# Columna 3
with col3:
    contenedor = st.container(border=True)
    with contenedor:
        prod = next(p for p in productos if p["id"] == "aros_cereza")
        img = ajustar_imagen(prod["imagen"])
        st.image(img, caption=prod["nombre"],width='stretch')
        st.write(f"**{prod['nombre']}**")
        for detalle in prod["detalles"]:
            st.write(detalle)
        st.link_button(label="Comprar", url=prod["url"],width='stretch')