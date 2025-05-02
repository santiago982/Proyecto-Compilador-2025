import re

PALABRAS_CLAVE_SQL = {
    "SELECT", "FROM", "WHERE", "INSERT", "INTO", "VALUES", "UPDATE", "SET",
    "DELETE", "CREATE", "TABLE", "DROP", "ALTER", "ADD", "JOIN", "ON",
    "GROUP", "BY", "ORDER", "HAVING", "AS", "DISTINCT", "AND", "OR", "NOT",
    "NULL", "IS", "IN", "EXISTS", "BETWEEN", "LIKE", "LIMIT"
}

OPERADORES_SQL = {
    "=", ">", "<", ">=", "<=", "<>", "!=", "AND", "OR", "NOT"
}

SIMBOLOS_SQL = {"(", ")", ",", ";", "*"}


def dividir_sentencias_sql(codigo):
    bloques = []
    sentencia_actual = ""

    for linea in codigo.strip().split("\n"):
        linea = linea.strip()
        if not linea:
            continue
        sentencia_actual += linea + " "
        if ";" in linea:
            bloques.append(sentencia_actual.strip())
            sentencia_actual = ""

    if sentencia_actual.strip():  # Si queda algo sin punto y coma al final
        bloques.append(sentencia_actual.strip())
    
    return bloques


def analizar_sql(codigo):
    errores = []
    tokens = []

    sentencias = dividir_sentencias_sql(codigo)

    for idx, sentencia in enumerate(sentencias, start=1):
        palabras = re.findall(r"[A-Za-z_][A-Za-z0-9_]*|[<>]=?|==|!=|[*(),;=]|'.*?'|\d+", sentencia)
        
        for palabra in palabras:
            if palabra.upper() in PALABRAS_CLAVE_SQL:
                tokens.append(("PALABRA_CLAVE", palabra.upper(), idx))
            elif palabra in OPERADORES_SQL:
                tokens.append(("OPERADOR", palabra, idx))
            elif palabra in SIMBOLOS_SQL:
                tokens.append(("SIMBOLO", palabra, idx))
            elif re.match(r"^'.*'$", palabra):
                tokens.append(("CADENA", palabra, idx))
            elif re.match(r"^\d+$", palabra):
                tokens.append(("NUMERO", palabra, idx))
            elif re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", palabra):
                tokens.append(("IDENTIFICADOR", palabra, idx))
            else:
                errores.append(f"[Sentencia {idx}] Token no reconocido: {palabra}")

        if not sentencia.endswith(";"):
            errores.append(f"[Sentencia {idx}] Falta punto y coma al final.")

    return tokens, errores
