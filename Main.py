import streamlit as st
from lenguaje_detector import detectar_lenguajes_embebidos
from analizador_sql import analizar_sql
from analizador_r import analizar_r
from analizador_python import analizar_python
from lema_bombeo import verificar_repeticiones
from explicador import explicar_codigo

# ------------------------------------
# INTERFAZ STREAMLIT PRINCIPAL
# ------------------------------------
st.title("Simulador de Compilador Multilenguaje Embebido")

# CSS para imagen fija al lado derecho
st.markdown("""
    <style>
    .right-bg {
        position: fixed;
        top: 0;
        right: 0;
        width: 40vw;
        height: 100vh;
        background-image: url('https://codebr.net/images/compilador.webp');
        background-size: contain;
        background-repeat: no-repeat;
        background-position: left;
        
        opacity: 0.85;
        z-index: -1;
    }

    .stApp {
        background-color: transparent;
    }

    /* Opcional: limitar el ancho del contenido principal para evitar superposición */
    .main {
        max-width: 60vw;
        padding-left: 2rem;
    }
    </style>

    <div class="right-bg"></div>
    """, unsafe_allow_html=True)



st.markdown("""
Este simulador permite analizar código con sentencias embebidas en **Python**, **SQL**, **R** y más.
Puedes escribir directamente el código o subir un archivo `.txt`.
""")

codigo = ""
archivo = st.file_uploader("Sube tu archivo de código (.txt)", type=["txt"])
if archivo:
    codigo = archivo.read().decode("utf-8")
    st.text_area("Vista previa del archivo cargado:", value=codigo, height=200)
else:
    codigo = st.text_area("Escribe o pega tu código aquí:", height=200)

if st.button("Compilar") and codigo:
    bloques = detectar_lenguajes_embebidos(codigo)

    for idx, (lenguaje, bloque) in enumerate(bloques):
        st.subheader(f"Bloque {idx+1}: Lenguaje detectado - {lenguaje}")
        st.code(bloque)

        if lenguaje == "Python":
            tokens, errores = analizar_python(bloque)
        elif lenguaje == "SQL":
            tokens, errores = analizar_sql(bloque)
        elif lenguaje == "R":
            tokens, errores = analizar_r(bloque)
        else:
            tokens, errores = [], ["Lenguaje no soportado"]

        repeticiones = verificar_repeticiones(bloque)
        explicacion = explicar_codigo(bloque, lenguaje)

        st.markdown("**Tokens reconocidos:**")
        st.code(tokens)

        if errores:
            st.markdown("**Errores detectados:**")
            for err in errores:
                st.error(err)
        else:
            st.success("No se encontraron errores de sintaxis o semántica.")

        if repeticiones:
            st.warning("Repeticiones estructurales detectadas (Lema de Bombeo):")
            for r in repeticiones:
                st.text(r)

        st.markdown("**Explicación del código:**")
        st.info(explicacion)
else:
    st.info("Escribe o carga un archivo para comenzar el análisis.")
