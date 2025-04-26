import re

def detectar_lenguajes_embebidos(codigo):
    """
    Detecta bloques de código en diferentes lenguajes (Python, SQL, R) embebidos en un mismo texto.
    Devuelve una lista de tuplas: (lenguaje, bloque de código)
    """
    bloques = []

    # Patrones básicos por lenguaje
    patron_python = r"(?:^|\n)(def |import |for |if |print\().*?(?=\n\S|$)"
    patron_sql = r"(?:^|\n)(SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER|JOIN).*?(?=;|\n\S|$)"
    patron_r = r"(?:^|\n)([a-zA-Z_]\w*\s*<-\s*|library\(|function\(|plot\().*?(?=\n\S|$)"

    # Buscar coincidencias
    for match in re.finditer(patron_python, codigo, re.DOTALL | re.IGNORECASE):
        bloques.append(("Python", match.group().strip()))

    for match in re.finditer(patron_sql, codigo, re.DOTALL | re.IGNORECASE):
        bloques.append(("SQL", match.group().strip()))

    for match in re.finditer(patron_r, codigo, re.DOTALL | re.IGNORECASE):
        bloques.append(("R", match.group().strip()))

    # Ordenar por aparición original (posición en el texto)
    bloques_ordenados = sorted(bloques, key=lambda x: codigo.find(x[1]))
    return bloques_ordenados



