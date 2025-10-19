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
    # === AROS ===
    {
        "id": "aros_salas",
        "imagen": "accesorios/aros/arosalas.png",
        "nombre": "Aros Alas",
        "detalles": ["• 1,5 Cm", "• Acero dorado"],
        "url": "https://wa.me/5493407404217?text=Hola,%20estoy%20interesado%20en%20los%20Aros%20Alas",
        "categoria": "Aros"
    },
    {
        "id": "aros_cereza",
        "imagen": "accesorios/aros/aroscereza.png",
        "nombre": "Aros Cereza",
        "detalles": ["• 1,5 Cm", "• Acero dorado"],
        "url": "https://wa.me/5493407404217?text=Hola,%20estoy%20interesado%20en%20los%20Aros%20Cereza",
        "categoria": "Aros"
    },
    {
        "id": "aros_corazon",
        "imagen": "accesorios/aros/aroscorazon.png",
        "nombre": "Aros Corazón",
        "detalles": ["• 1,5 Cm", "• Acero dorado"],
        "url": "https://wa.me/5493407404217?text=Hola,%20estoy%20interesado%20en%20los%20Aros%20Corazón",
        "categoria": "Aros"
    },
    {
        "id": "aros_cubanos",
        "imagen": "accesorios/aros/aroscubanos.png",
        "nombre": "Aros Cubanos",
        "detalles": ["• 1,5 Cm", "• Acero dorado"],
        "url": "https://wa.me/5493407404217?text=Hola,%20estoy%20interesado%20en%20los%20Aros%20Cubanos",
        "categoria": "Aros"
    },
    {
        "id": "aros_flor",
        "imagen": "accesorios/aros/arosflor.png",
        "nombre": "Aros Flor",
        "detalles": ["• 1,5 Cm", "• Acero dorado"],
        "url": "https://wa.me/5493407404217?text=Hola,%20estoy%20interesado%20en%20los%20Aros%20Flor",
        "categoria": "Aros"
    },
    {
        "id": "aros_herradura",
        "imagen": "accesorios/aros/arosherradura.png",
        "nombre": "Aros Herradura",
        "detalles": ["• 1,5 Cm", "• Acero dorado"],
        "url": "https://wa.me/5493407404217?text=Hola,%20estoy%20interesado%20en%20los%20Aros%20Herradura",
        "categoria": "Aros"
    },
    {
        "id": "aros_herradura2",
        "imagen": "accesorios/aros/arosherradura2.png",
        "nombre": "Aros Herradura 2",
        "detalles": ["• 1,5 Cm", "• Acero dorado"],
        "url": "https://wa.me/5493407404217?text=Hola,%20estoy%20interesado%20en%20los%20Aros%20Herradura%202",
        "categoria": "Aros"
    },
    {
        "id": "aros_mariposa",
        "imagen": "accesorios/aros/arosmariposa.png",
        "nombre": "Aros Mariposa",
        "detalles": ["• 1,5 Cm", "• Acero dorado"],
        "url": "https://wa.me/5493407404217?text=Hola,%20estoy%20interesado%20en%20los%20Aros%20Mariposa",
        "categoria": "Aros"
    },
    {
        "id": "aros_nose",
        "imagen": "accesorios/aros/arosnose.png",
        "nombre": "Aros Nose",
        "detalles": ["• 1,5 Cm", "• Acero dorado"],
        "url": "https://wa.me/5493407404217?text=Hola,%20estoy%20interesado%20en%20los%20Aros%20Nose",
        "categoria": "Aros"
    },

    # === COLLARES ===
    {
        "id": "collar_cadena_girasol",
        "imagen": "accesorios/collares/cadenagirasol.png",
        "nombre": "Cadena Girasol",
        "detalles": ["• Acero inoxidable", "• Dije Girasol"],
        "url": "https://wa.me/5493407404217?text=Hola,%20quiero%20más%20info%20sobre%20la%20Cadena%20Girasol",
        "categoria": "Collares"
    },
    {
        "id": "collar_cadena_plateada",
        "imagen": "accesorios/collares/cadenaplateada.png",
        "nombre": "Cadena Plateada",
        "detalles": ["• Acero plateado", "• Diseño clásico"],
        "url": "https://wa.me/5493407404217?text=Hola,%20quiero%20más%20info%20sobre%20la%20Cadena%20Plateada",
        "categoria": "Collares"
    },
    {
        "id": "collar_dije_mariposa",
        "imagen": "accesorios/collares/dijemariposa.png",
        "nombre": "Dije Mariposa",
        "detalles": ["• Acero dorado", "• Dije Mariposa"],
        "url": "https://wa.me/5493407404217?text=Hola,%20quiero%20más%20info%20sobre%20el%20Dije%20Mariposa",
        "categoria": "Collares"
    },
    {
        "id": "collar_dije_osito",
        "imagen": "accesorios/collares/dijeosito.png",
        "nombre": "Dije Osito",
        "detalles": ["• Acero dorado", "• Dije Osito"],
        "url": "https://wa.me/5493407404217?text=Hola,%20quiero%20más%20info%20sobre%20el%20Dije%20Osito",
        "categoria": "Collares"
    },
    {
        "id": "collar_gargantilla",
        "imagen": "accesorios/collares/gargantilla1.png",
        "nombre": "Gargantilla",
        "detalles": ["• Acero dorado", "• Estilo moderno"],
        "url": "https://wa.me/5493407404217?text=Hola,%20quiero%20más%20info%20sobre%20la%20Gargantilla",
        "categoria": "Collares"
    },

    # === PULSERAS ===
    {
        "id": "pulsera_1",
        "imagen": "accesorios/pulseras/pulsera1.png",
        "nombre": "Pulsera Dorada",
        "detalles": ["• Acero dorado", "• Diseño ajustable"],
        "url": "https://wa.me/5493407404217?text=Hola,%20quiero%20más%20info%20sobre%20la%20Pulsera%20Dorada",
        "categoria": "Pulseras"
    },
]

tab1, tab2, tab3, tab4 = st.tabs(["Aros", "Collares", "Pulseras", "Anillos"])

def mostrar_productos(categoria):
    col1, col2, col3, col4 = st.columns(4)
    columnas = [col1, col2, col3, col4]
    productos_filtrados = [p for p in productos if p["categoria"] == categoria]

    for i, producto in enumerate(productos_filtrados):
        col = columnas[i % 4]
        with col:
            st.image(ajustar_imagen(producto["imagen"]), use_container_width=True)
            st.markdown(f"**{producto['nombre']}**")
            for detalle in producto["detalles"]:
                st.write(detalle)
            st.link_button("Comprar", producto["url"], use_container_width=True)

with tab1:
    mostrar_productos("Aros")

with tab2:
    mostrar_productos("Collares")

with tab3:
    mostrar_productos("Pulseras")

with tab4:
    st.info("Próximamente Anillos 💍")