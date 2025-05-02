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
        elif re.search(r"\bfunction\b|\b<-", linea_stripped):
            lenguaje = "R"
        elif re.search(r"\bdef\b|\bprint\b|:\s*$|\bimport\b", linea_stripped):
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



