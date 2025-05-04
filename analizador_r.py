import re
from difflib import get_close_matches

# Palabras clave y funciones comunes de R
PALABRAS_CLAVE_R = {
    "if", "else", "for", "while", "repeat", "in", "function", "return",
    "break", "next", "TRUE", "FALSE", "NULL", "NA", "NA_integer_", "NA_real_", "NA_complex_", "NA_character_"
    
}


OPERADORES_R = {"<-", "->", "=", "+", "-", "*", "/", "%%", "%/%", "^", "==", "!=", "<", ">", "<=", ">=", "&", "|", "!", ":"}

SIMBOLOS_R = {"(", ")", "{", "}", "[", "]", ",", ";"}

FUNCIONES_BUILTIN_R = {
    # Básicas
    "print", "cat", "mean", "sum", "min", "max", "length", "seq", "rep", "paste",
    "c", "matrix", "data.frame", "list", "as.numeric", "as.character", "as.logical", "summary", "str", "class",
    # Manipulación
    "subset", "merge", "rbind", "cbind", "filter", "mutate", "select", "group_by", "arrange", "summarise",
    # Visualización
    "plot", "hist", "boxplot", "barplot", "ggplot", "aes", "geom_point", "geom_line", "geom_bar",
    # Librerías y datos
    "install.packages", "library", "require", "read.csv", "read.table", "write.csv", "data", "head", "tail",
    # SQL y limpieza
    "sqldf", "tidyr", "dplyr", "tibble", "separate", "spread", "gather"
}

LIBRERIAS_RECONOCIDAS = {
    "sqldf", "dplyr", "tidyr", "ggplot2", "readr", "stringr", "lubridate", "data.table", "tibble", "caret", "shiny"
}

def sugerir_r(token):
    candidatos = PALABRAS_CLAVE_R.union(FUNCIONES_BUILTIN_R)
    sugerencias = get_close_matches(token, candidatos, n=1)
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

def analizar_r(codigo):
    errores = []
    tokens = []
    lineas = codigo.strip().split('\n')

    for idx, linea in enumerate(lineas, start=1):
        linea = linea.strip()
        if not linea:
            continue

        # Ignorar comentarios
        linea = linea.split("#")[0].strip()
        if not linea:
            continue

        # Detectar SQL embebido
        if detectar_sql_embebido(linea):
            errores.append(f"[Línea {idx}] SQL embebido detectado. Usa el analizador SQL para esta sección.")
            tokens.append(("SQL_EMBEBIDO", linea, idx))
            continue

        # Verificar paréntesis
        verificar_balance_parentesis(linea, idx, errores)

        # Verificar comillas balanceadas
        if linea.count('"') % 2 != 0 or linea.count("'") % 2 != 0:
            errores.append(f"[Línea {idx}] Comillas desbalanceadas.")

        # Verificar asignaciones tipo if( sin cierre )
        if re.match(r"if\s*\([^)]*$", linea):
            errores.append(f"[Línea {idx}] Condición 'if' incompleta o sin cierre de paréntesis.")

        # Verificar elementos tipo c(1 2 3)
        if re.search(r"c\(\s*\d+\s+\d+", linea):
            errores.append(f"[Línea {idx}] Puede faltar una coma entre los elementos de 'c()'.")

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

