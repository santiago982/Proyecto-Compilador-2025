import re

def analizar_python(codigo):
    errores = []
    tokens = []

    # Análisis léxico (tokens simples)
    patron_tokens = r"\b(def|return|if|else|for|while|import|print|in|range)\b|\w+|\d+|[+\-*/=<>():.,]"
    tokens_encontrados = re.findall(patron_tokens, codigo)

    if not tokens_encontrados:
        errores.append("No se encontraron tokens en el código.")

    tokens.extend(tokens_encontrados)

    # Reglas sintácticas mínimas
    if "def" in tokens and "(" not in tokens:
        errores.append("Falta paréntesis en la definición de función.")

    if "print" in tokens and "(" not in tokens:
        errores.append("Falta paréntesis en la función print.")

    # Validación semántica simple
    if "return" in tokens and "def" not in tokens:
        errores.append("Uso de 'return' fuera de una función.")

    return errores, tokens
