import re

def detectar_lenguajes_embebidos(codigo):
    """
    Detecta bloques de código en diferentes lenguajes (Python, SQL, R) embebidos en un mismo texto.
    Devuelve una lista de tuplas: (lenguaje, bloque de código)
    """
    bloques = []
    actual = []
    lenguaje_actual = None

    lineas = codigo.strip().split('\n')

    for linea in lineas:
        linea_stripped = linea.strip()

        # Detectores simples por línea
        if re.search(r"\b(SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER|JOIN|FROM|WHERE)\b", linea_stripped, re.IGNORECASE):
            lenguaje = "SQL"
        elif re.search(r"\b(function|if|else|for|while|repeat|TRUE|FALSE|NULL|NA|view|library|return)\b", linea_stripped) \
            or "<-" in linea_stripped or "->" in linea_stripped or re.search(r"\bdbGetQuery\b|\bsqldf\b", linea_stripped):
            lenguaje = "R"
        elif re.search(r"\bdef\s+\w+\s*\(.*\)\s*:\b|\bprint\s*\(.*\)|f\".*?\"|f\'.*?\'|\bclass\s+\w+\s*:\b", linea_stripped):
            lenguaje = "Python"

        else:
            lenguaje = lenguaje_actual  # Continuación del mismo lenguaje

        if lenguaje != lenguaje_actual and actual:
            bloques.append((lenguaje_actual, "\n".join(actual)))
            actual = []

        lenguaje_actual = lenguaje
        actual.append(linea)

    if actual:
        bloques.append((lenguaje_actual, "\n".join(actual)))

    return bloques



