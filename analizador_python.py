import re
from difflib import get_close_matches

# Palabras clave, operadores y símbolos de Python
PALABRAS_CLAVE_PYTHON = {
    'False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await',
    'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except',
    'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is',
    'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return',
    'try', 'while', 'with', 'yield', 'print', 'input', 'range', 'len', 'sum'
}

OPERADORES_PYTHON = {
    '+', '-', '*', '/', '//', '%', '**', '=', '==', '!=', '>', '<',
    '>=', '<=', '+=', '-=', '*=', '/=', '%=', '**=', '//='  
}

SIMBOLOS_PYTHON = {'(', ')', '[', ']', '{', '}', ':', ',', '.', ';'}

# Funciones comunes que no son palabras clave
FUNCIONES_BUILTIN = {'print', 'input', 'len', 'sum', 'range'}

def dividir_bloques_codigo(codigo):
    bloques = []
    bloque_actual = []
    for linea in codigo.splitlines():
        if linea.strip() == '':
            if bloque_actual:
                bloques.append('\n'.join(bloque_actual))
                bloque_actual = []
        else:
            bloque_actual.append(linea)
    if bloque_actual:
        bloques.append('\n'.join(bloque_actual))
    return bloques

def sugerir_palabra_python(token):
    sugerencias = get_close_matches(token, PALABRAS_CLAVE_PYTHON.union(FUNCIONES_BUILTIN), n=1)
    return sugerencias[0] if sugerencias else None

def analizar_python(codigo):
    errores = []
    tokens = []
    bloques = dividir_bloques_codigo(codigo)

    lenguaje_detectado = False

    for idx, bloque in enumerate(bloques, start=1):
        lineas = bloque.split('\n')
        for linea_num, linea in enumerate(lineas, start=1):
            palabras = re.findall(
                r"[A-Za-z_][A-Za-z0-9_]*|==|!=|<=|>=|<|>|\*\*|[-+*/%=(),.:;]|\d+\.?\d*|\".*?\"|\'.*?\'",
                linea
            )
            for palabra in palabras:
                if palabra in PALABRAS_CLAVE_PYTHON:
                    tokens.append(("PALABRA_CLAVE", palabra, idx, linea_num))
                    lenguaje_detectado = True
                elif palabra in FUNCIONES_BUILTIN:
                    tokens.append(("FUNCION_BUILTIN", palabra, idx, linea_num))
                    lenguaje_detectado = True
                elif palabra in OPERADORES_PYTHON:
                    tokens.append(("OPERADOR", palabra, idx, linea_num))
                elif palabra in SIMBOLOS_PYTHON:
                    tokens.append(("SIMBOLO", palabra, idx, linea_num))
                elif re.match(r"^\d+(\.\d+)?$", palabra):
                    tokens.append(("NUMERO", palabra, idx, linea_num))
                elif re.match(r"^\".*\"$|^'.*'$", palabra):
                    tokens.append(("CADENA", palabra, idx, linea_num))
                elif re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", palabra):
                    tokens.append(("IDENTIFICADOR", palabra, idx, linea_num))
                else:
                    sugerencia = sugerir_palabra_python(palabra)
                    if sugerencia:
                        errores.append(f"[Bloque {idx}, Línea {linea_num}] ¿Quisiste decir '{sugerencia}' en vez de '{palabra}'?")
                    else:
                        errores.append(f"[Bloque {idx}, Línea {linea_num}] Token no reconocido: {palabra}")

    # Sencilla verificación sintáctica
    for token in tokens:
        tipo, valor, bloque, linea = token
        if tipo == "PALABRA_CLAVE" and valor == "def":
            if not any(t[0] == "SIMBOLO" and t[1] == ":" for t in tokens if t[2] == bloque):
                errores.append(f"[Bloque {bloque}] Función sin ':' al final")

    if not lenguaje_detectado:
        errores.append("Este código no parece estar escrito en Python. ¿Es posible que sea otro lenguaje como R?")

    return tokens, errores
