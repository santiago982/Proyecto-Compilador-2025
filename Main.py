import streamlit as st
from lenguaje_detector import detectar_lenguajes_embebidos
from analizador_sql import analizar_sql
from analizador_r import analizar_r
from analizador_python import analizar_python
from lema_bombeo import verificar_repeticiones,pertenece_a_lenguaje_regular,aplicar_lema_de_bombeo
from explicador import explicar_codigo

# ------------------------------------
# INTERFAZ STREAMLIT PRINCIPAL ggg
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

    # Constante del lema de bombeo
N_CONSTANTE_BOMPEO = 10

# Expresiones regulares para cada lenguaje (puedes ajustar según tu diseño)
expresion_regular = {
    "Python": r"^[\s\S]*$",  # Puedes poner una más específica si quieres
    "SQL": r"(?i)^\s*(SELECT|INSERT|UPDATE|DELETE)\s+.*",
    "R": r"^[\s\S]*<-\s*.*"  # Ejemplo muy simple
}

st.title("🔍 Analizador Multilenguaje con Lema de Bombeo")

# Suponiendo que ya tienes tu lista de bloques y lenguajes detectados
for idx, (lenguaje, bloque) in enumerate(bloques):
    st.subheader(f"🧩 Bloque {idx + 1} - Lenguaje detectado: {lenguaje}")
    st.code(bloque)

    # --- Análisis léxico/sintáctico por lenguaje ---
    if lenguaje == "Python":
        tokens, errores = analizar_python(bloque)
    elif lenguaje == "SQL":
        tokens, errores = analizar_sql(bloque)
    elif lenguaje == "R":
        tokens, errores = analizar_r(bloque)
    else:
        tokens, errores = [], ["Lenguaje no soportado"]

    # --- Pertenece a lenguaje regular ---
    pertenece = pertenece_a_lenguaje_regular(bloque.strip(), expresion_regular.get(lenguaje, r".*"))

    # --- Lema de Bombeo formal ---
    resultado_bombeo = aplicar_lema_de_bombeo(bloque.strip(), N_CONSTANTE_BOMPEO)

    # --- Heurística de repeticiones estructurales ---
    repeticiones = verificar_repeticiones(bloque)
    
    
    explicacion = explicar_codigo(bloque, lenguaje)
    

    # --- Mostrar resultados ---
    st.markdown("### 📌 Tokens reconocidos:")
    st.code(tokens)

    if errores:
        st.markdown("### ❌ Errores detectados:")
        for err in errores:
            st.error(err)
    else:
        st.success("✅ No se encontraron errores de sintaxis o semántica.")

    st.markdown("### 📐 Pertenencia a lenguaje regular:")
    if pertenece:
        st.success("✅ La cadena cumple con la expresión regular esperada.")
    else:
        st.warning("⚠️ La cadena NO pertenece al lenguaje definido por la expresión regular.")

    st.markdown("### 🌀 Verificación estructural (heurística):")
    if repeticiones:
        for r in repeticiones:
            st.warning(r)
    else:
        st.info("✅ No se detectaron repeticiones estructurales sospechosas.")

    st.markdown("### 🔁 Análisis con el lema de bombeo:")
    st.info(f"Longitud de cadena: {resultado_bombeo['longitud']} | Constante n: {resultado_bombeo['constante_n']}")
    st.info(resultado_bombeo["resultado"])

    if resultado_bombeo["uvz"]:
        u, v, z = resultado_bombeo["uvz"]
        st.markdown(f"**Descomposición encontrada** `w = uvz`")
        st.code(f"u = '{u}'\nv = '{v}'\nz = '{z}'")

        st.markdown("**🔄 Ejemplos con uvⁱz para i = 0, 1, 2:**")
        for i, ejemplo in resultado_bombeo["ejemplos"]:
            st.text(f"i = {i}: {ejemplo}")
            
            
        st.markdown("**Explicación del código:**")
        st.info(explicacion)

st.info("Carga un archivo o escribe código para comenzar el análisis.")
