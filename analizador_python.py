import re
from difflib import get_close_matches

# Palabras clave de Python más comunes
PALABRAS_CLAVE_PYTHON = {
    'False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await',
    'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except',
    'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is',
    'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return',
    'try', 'while', 'with', 'yield'
}

OPERADORES_PYTHON = {
    '+', '-', '*', '/', '//', '%', '**', '=', '==', '!=', '>', '<',
    '>=', '<=', '+=', '-=', '*=', '/=', '%=', '**=', '//='  
}

SIMBOLOS_PYTHON = {'(', ')', '[', ']', '{', '}', ':', ',', '.', ';'}

# Detectar bloques de código Python

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

# Detectar fragmentos embebidos de SQL
SQL_INICIO = re.compile(r"('''|\"\"\"|\"|')(SELECT|INSERT|UPDATE|DELETE|CREATE).*?(\1)", re.IGNORECASE | re.DOTALL)

def extraer_sql_embebido(codigo):
    return re.findall(SQL_INICIO, codigo)

def sugerir_palabra_python(token):
    sugerencias = get_close_matches(token, PALABRAS_CLAVE_PYTHON, n=1)
    return sugerencias[0] if sugerencias else None

def analizar_python(codigo):
    errores = []
    tokens = []
    bloques = dividir_bloques_codigo(codigo)

    for idx, bloque in enumerate(bloques, start=1):
        lineas = bloque.split('\n')
        for linea_num, linea in enumerate(lineas, start=1):
            palabras = re.findall(r"[A-Za-z_][A-Za-z0-9_]*|[<>]=?|==|!=|\*\*|[-+*/%=(),.:;]|\d+\.?\d*|\".*?\"|\'.*?\'", linea)
            for palabra in palabras:
                if palabra in PALABRAS_CLAVE_PYTHON:
                    tokens.append(("PALABRA_CLAVE", palabra, idx, linea_num))
                elif palabra in OPERADORES_PYTHON:
                    tokens.append(("OPERADOR", palabra, idx, linea_num))
                elif palabra in SIMBOLOS_PYTHON:
                    tokens.append(("SIMBOLO", palabra, idx, linea_num))
                elif re.match(r"^\d+(\.\d+)?$", palabra):
                    tokens.append(("NUMERO", palabra, idx, linea_num))
                elif re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", palabra):
                    tokens.append(("IDENTIFICADOR", palabra, idx, linea_num))
                elif re.match(r"^\".*\"$|^'.*'$", palabra):
                    tokens.append(("CADENA", palabra, idx, linea_num))
                else:
                    sugerencia = sugerir_palabra_python(palabra)
                    if sugerencia:
                        errores.append(f"[Bloque {idx}, Línea {linea_num}] ¿Quisiste decir '{sugerencia}' en vez de '{palabra}'?")
                    else:
                        errores.append(f"[Bloque {idx}, Línea {linea_num}] Token no reconocido: {palabra}")

    # Análisis de SQL embebido
    sql_embebido = extraer_sql_embebido(codigo)
    if sql_embebido:
        from analizador_sql import analizar_sql  
        for sql_texto in sql_embebido:
            _, errores_sql = analizar_sql(sql_texto[1])
            errores.extend(["[SQL Embebido] " + e for e in errores_sql])

    return tokens, errores

