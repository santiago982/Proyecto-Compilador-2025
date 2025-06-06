import re
from difflib import get_close_matches

# Diccionarios que NO deben cambiar
PALABRAS_CLAVE_R = {
    "if", "else", "for", "while", "repeat", "in", "function", "return",
    "break", "next", "TRUE", "FALSE", "NULL", "NA", "NA_integer_", "NA_real_", "NA_complex_", "NA_character_"
}

OPERADORES_R = {"<-", "->", "=", "+", "-", "*", "/", "%%", "%/%", "^", "==", "!=", "<", ">", "<=", ">=", "&", "|", "!", ":"}

SIMBOLOS_R = {"(", ")", "{", "}", "[", "]", ",", ";"}

FUNCIONES_BUILTIN_R = {
    "view", "cat", "mean", "sum", "min", "max", "length", "seq", "rep", "paste",
    "c", "matrix", "data.frame", "list", "as.numeric", "as.character", "as.logical", "summary", "str", "class",
    "subset", "merge", "rbind", "cbind", "filter", "mutate", "select", "group_by", "arrange", "summarise",
    "plot", "hist", "boxplot", "barplot", "ggplot", "aes", "geom_point", "geom_line", "geom_bar",
    "install.packages", "library", "require", "read.csv", "read.table", "write.csv", "data", "head", "tail",
    "sqldf", "tidyr", "dplyr", "tibble", "separate", "spread", "gather", "readr"
}

LIBRERIAS_RECONOCIDAS = {
    "sqldf", "dplyr", "tidyr", "ggplot2", "readr", "stringr", "lubridate", "data.table", "tibble", "caret", "shiny"
}

def sugerir_r(token):
    candidatos = PALABRAS_CLAVE_R.union(FUNCIONES_BUILTIN_R)
    sugerencias = get_close_matches(token, candidatos, n=1, cutoff=0.75)
    return sugerencias[0] if sugerencias else None

def detectar_sql_embebido(linea):
    return any(sql in linea.upper() for sql in ["SELECT", "INSERT", "UPDATE", "DELETE", "CREATE"])

def verificar_balance_parentesis(linea, idx, errores):
    stack = []
    pares = {')': '(', ']': '[', '}': '{'}
    for char in linea:
        if char in "([{":
            stack.append(char)
        elif char in ")]}":
            if not stack or stack[-1] != pares[char]:
                errores.append(f"[Línea {idx}] Símbolo de cierre '{char}' no coincide o está desbalanceado.")
            else:
                stack.pop()
    if stack:
        errores.append(f"[Línea {idx}] Faltan símbolos de cierre para: {''.join(stack)}")

def unir_bloques_multilinea(lineas):
    bloques = []
    bloque_actual = ''
    par_balance = 0
    for linea in lineas:
        linea_sin_comentario = linea.split("#")[0]
        par_balance += linea_sin_comentario.count('(') - linea_sin_comentario.count(')')
        bloque_actual += linea + '\n'
        if par_balance <= 0:
            bloques.append(bloque_actual.strip())
            bloque_actual = ''
            par_balance = 0
    if bloque_actual:
        bloques.append(bloque_actual.strip())
    return bloques

def analizar_r(codigo):
    errores = []
    tokens = []
    lineas = codigo.strip().split('\n')
    lineas = unir_bloques_multilinea(lineas)

    for idx, linea in enumerate(lineas, start=1):
        original_line = linea
        linea = linea.strip()
        if not linea:
            continue

        # Ignorar comentarios
        linea = linea.split("#")[0].strip()
        if not linea:
            continue

        # SQL embebido
        if detectar_sql_embebido(linea):
            errores.append(f"[Línea {idx}] SQL embebido detectado. Usa el analizador SQL para esta sección.")
            tokens.append(("SQL_EMBEBIDO", linea, idx))
            continue

        verificar_balance_parentesis(linea, idx, errores)

        if linea.count('"') % 2 != 0 or linea.count("'") % 2 != 0:
            errores.append(f"[Línea {idx}] Comillas desbalanceadas.")

        if re.match(r"if\s*\([^)]*$", linea):
            errores.append(f"[Línea {idx}] Condición 'if' incompleta o sin cierre de paréntesis.")

        if re.search(r"c\(\s*\d+\s+\d+", linea):
            errores.append(f"[Línea {idx}] Puede faltar una coma entre los elementos de 'c()'.")

        if re.search(r'=\s*\(\s*"[^"]+"\s+"[^"]+"', linea):
            errores.append(f"[Línea {idx}] Falta la función 'c()' o hay elementos de texto sin comas.")

        if re.search(r'\(\s*(\d+\s+\d+|".+?"\s+".+?")', linea):
            errores.append(f"[Línea {idx}] Puede faltar una coma entre los elementos dentro del paréntesis (verifica uso de 'c()').")

        # ERRORES NUEVOS agregados para reconocer

        # 1. Asignación mal formada con '<' en vez de '<-'
        if re.search(r'\w+\s*<\s*\w+', linea) and '<-' not in linea:
            errores.append(f"[Línea {idx}] Posible error de asignación: usa '<-' en lugar de '<'.")

        # 2. Detección y sugerencia para funciones mal escritas
        funciones_posibles = re.findall(r'\b[A-Za-z_]+\b(?=\()', linea)
        for funcion in funciones_posibles:
            if funcion not in FUNCIONES_BUILTIN_R:
                sugerencia = sugerir_r(funcion)
                if sugerencia:
                    errores.append(f"[Línea {idx}] Función '{funcion}()' no reconocida. ¿Quisiste decir '{sugerencia}()'?")
                else:
                    errores.append(f"[Línea {idx}] Función '{funcion}()' no reconocida.")

        # Tokenización básica
        palabras = re.findall(r"[A-Za-z_][A-Za-z0-9_]*|[<>]=?|==|!=|%%|%/%|[*+^/\\(),;:{}[\]]|[-]+|<-|->|\d+\.?\d*|\".*?\"|'.*?'", linea)

        for palabra in palabras:
            if palabra in PALABRAS_CLAVE_R:
                tokens.append(("PALABRA_CLAVE", palabra, idx))
            elif palabra in FUNCIONES_BUILTIN_R:
                tokens.append(("FUNCION", palabra, idx))
            elif palabra in OPERADORES_R:
                tokens.append(("OPERADOR", palabra, idx))
            elif palabra in SIMBOLOS_R:
                tokens.append(("SIMBOLO", palabra, idx))
            elif palabra in LIBRERIAS_RECONOCIDAS:
                tokens.append(("LIBRERIA", palabra, idx))
            elif re.match(r'^".*"$', palabra) or re.match(r"^'.*'$", palabra):
                tokens.append(("CADENA", palabra, idx))
            elif re.match(r"^\d+(\.\d+)?$", palabra):
                tokens.append(("NUMERO", palabra, idx))
            elif re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", palabra):
                tokens.append(("IDENTIFICADOR", palabra, idx))
            else:
                sugerencia = sugerir_r(palabra)
                if sugerencia:
                    errores.append(f"[Línea {idx}] Token '{palabra}' no reconocido. ¿Quisiste decir '{sugerencia}'?")
                else:
                    errores.append(f"[Línea {idx}] Token no reconocido: '{palabra}'")

    return tokens, errores



