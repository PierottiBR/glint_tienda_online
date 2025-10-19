import streamlit as st
import base64

st.set_option("client.showErrorDetails", True)

# === Cargar imagen PNG y convertir a base64 ===
logo_path = "GlintAccesoriosLogo.png"  # tu imagen
with open(logo_path, "rb") as f:
    logo_base64 = base64.b64encode(f.read()).decode()

st.set_page_config(page_title="Glint Accesorios", page_icon=logo_path, layout="wide")

# === Mostrar título sin clamp ni ícono ===
import streamlit as st

st.markdown(
    """
    <style>
    @keyframes star-glow {
        0% { text-shadow: 0 0 5px #d4af37, 0 0 10px #d4af37; }
        50% { text-shadow: 0 0 20px #ffd700, 0 0 30px #ffd700; }
        100% { text-shadow: 0 0 5px #d4af37, 0 0 10px #d4af37; }
    }

    .titulo-wrapper {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            max-width: 100%;        /* no salga del contenedor */
            word-break: break-word;  /* corta si es muy largo */
        }

    .titulo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 0;
    }

    .titulo-glint {
        color: #d4af37;
        font-weight: 900;
        font-size: 80px;
        margin: 0 10px 0 0;
        line-height: 1;
    }

    .estrella {
        font-size: 120px;
        animation: star-glow 2s infinite;
        line-height: 1;
    }

    .subtitulo {
        font-size: 24px;
        margin: 2px 0;
        line-height: 1;
        letter-spacing: 3px;
    }

    * { margin: 0; padding: 0; } /* elimina márgenes y paddings globales */
    </style>

    <div class="titulo-wrapper">
        <div class="subtitulo">Bienvenid@ a</div>
        <div class="titulo-container">
            <div class="titulo-glint">Glint</div>
            <div class="estrella">★</div>
        </div>
        <div class="subtitulo">ACCESORIOS</div>
    </div>
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

#TABS CON CATEGORIAS
tab1, tab2, tab3, tab4 = st.tabs(["Aros", "Collares", "Pulseras", "Anillos"])

with tab1:
    col1, col2, col3, col4 = st.columns(4)
    columnas = [col1, col2, col3, col4]

    for i, producto in enumerate(productos):
        col = columnas[i % 4]  # distribuye en 4 columnas
        with col:
            st.image(ajustar_imagen(producto["imagen"]), use_container_width=True)
            st.markdown(f"**{producto['nombre']}**")
            st.write("Detalles:")
            for detalle in producto["detalles"]:
                st.write(detalle)
            st.link_button("Comprar", producto["url"], use_container_width=True)

with tab2:
    st.write("Collares")

with tab3:
    st.write("Pulseras")

with tab4:
    st.write("Anillos")