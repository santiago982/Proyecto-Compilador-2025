import re
from difflib import get_close_matches

# Palabras clave SQL válidas
PALABRAS_CLAVE_SQL = {
    "SELECT", "FROM", "WHERE", "INSERT", "INTO", "VALUES", "UPDATE", "SET",
    "DELETE", "CREATE", "TABLE", "DROP", "ALTER", "ADD", "JOIN", "ON",
    "GROUP", "BY", "ORDER", "HAVING", "AS", "DISTINCT", "AND", "OR", "NOT",
    "NULL", "IS", "IN", "EXISTS", "BETWEEN", "LIKE", "LIMIT", "PRIMARY", "KEY",
    "AUTO_INCREMENT", "UNIQUE", "DEFAULT"
}

# Operadores y símbolos SQL válidos
OPERADORES_SQL = {"=", ">", "<", ">=", "<=", "<>", "!=", "AND", "OR", "NOT"}
SIMBOLOS_SQL = {"(", ")", ",", ";", "*"}

# Tipos y modificadores de datos válidos en SQL
TIPOS_SQL_VALIDOS = {
    "INT", "INTEGER", "VARCHAR", "CHAR", "DECIMAL", "FLOAT", "DOUBLE",
    "DATE", "TEXT", "BOOLEAN", "SMALLINT", "BIGINT", "NUMERIC", "REAL", "TIME"
}
MODIFICADORES_SQL_VALIDOS = {
    "PRIMARY", "KEY", "AUTO_INCREMENT", "NOT", "NULL", "UNIQUE", "DEFAULT"
}

# Separa código SQL en sentencias
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
    if sentencia_actual.strip():
        bloques.append(sentencia_actual.strip())
    return bloques

# Sugiere una palabra clave cercana
def sugerir_palabra(token):
    sugerencias = get_close_matches(token.upper(), PALABRAS_CLAVE_SQL, n=1)
    return sugerencias[0] if sugerencias else None

# Valida columnas de CREATE TABLE
def validar_columnas_create_table(sentencia, idx):
    errores = []
    columnas_raw = re.findall(r"\((.*?)\)", sentencia, re.DOTALL)
    if not columnas_raw:
        errores.append(f"[Sentencia {idx}] No se encontraron columnas en CREATE TABLE.")
        return errores
    
    columnas = columnas_raw[0].split(",")
    for i, col in enumerate(columnas, 1):
        partes = col.strip().split()
        if len(partes) < 2:
            errores.append(f"[Sentencia {idx}] Columna {i} incompleta: '{col.strip()}'")
            continue
        nombre = partes[0]
        tipo = partes[1].upper()
        if "(" in tipo:
            tipo = tipo.split("(")[0]
        if tipo not in TIPOS_SQL_VALIDOS:
            errores.append(f"[Sentencia {idx}] Tipo de dato inválido en columna '{nombre}': '{partes[1]}'")
        
        modificadores = [p.upper() for p in partes[2:]]
        for mod in modificadores:
            if mod not in MODIFICADORES_SQL_VALIDOS:
                errores.append(f"[Sentencia {idx}] Modificador inválido en columna '{nombre}': '{mod}'")
    
    return errores

# Analiza código SQL
def analizar_sql(codigo):
    errores = []
    tokens = []
    
    sentencias = dividir_sentencias_sql(codigo)

    for idx, sentencia in enumerate(sentencias, start=1):
        palabras = re.findall(r"[A-Za-z_][A-Za-z0-9_]*|[<>]=?|==|!=|[*(),;=]|'.*?'|\d+\.?\d*|\d+", sentencia)
        palabras_mayus = [p.upper() for p in palabras]
        tipo_sentencia = palabras_mayus[0] if palabras_mayus else ""

        # Validaciones generales de estructura
        if tipo_sentencia == "SELECT":
            if "FROM" not in palabras_mayus:
                errores.append(f"[Sentencia {idx}] SELECT sin cláusula FROM.")
        elif tipo_sentencia == "INSERT":
            if "INTO" not in palabras_mayus or "VALUES" not in palabras_mayus:
                errores.append(f"[Sentencia {idx}] INSERT debe contener INTO y VALUES.")
        elif tipo_sentencia == "UPDATE":
            if "SET" not in palabras_mayus:
                errores.append(f"[Sentencia {idx}] UPDATE sin cláusula SET.")
        elif tipo_sentencia == "DELETE":
            if "FROM" not in palabras_mayus:
                errores.append(f"[Sentencia {idx}] DELETE sin cláusula FROM.")
        elif tipo_sentencia == "CREATE":
            if "TABLE" not in palabras_mayus:
                errores.append(f"[Sentencia {idx}] CREATE debe ir acompañado de TABLE.")
            if "(" not in sentencia or ")" not in sentencia:
                errores.append(f"[Sentencia {idx}] Falta paréntesis en definición de CREATE TABLE.")
            else:
                errores.extend(validar_columnas_create_table(sentencia, idx))
        else:
            if not any(clave in palabras_mayus for clave in ["SELECT", "INSERT", "UPDATE", "DELETE", "CREATE"]):
                errores.append(f"[Sentencia {idx}] No parece una sentencia SQL válida.")

        # Tokenización y verificación
        for palabra in palabras:
            palabra_mayus = palabra.upper()

            if palabra_mayus in PALABRAS_CLAVE_SQL:
                tokens.append(("PALABRA_CLAVE", palabra_mayus, idx))
            elif palabra in OPERADORES_SQL:
                tokens.append(("OPERADOR", palabra, idx))
            elif palabra in SIMBOLOS_SQL:
                tokens.append(("SIMBOLO", palabra, idx))
            elif re.match(r"^'.*'$", palabra):
                tokens.append(("CADENA", palabra, idx))
            elif re.match(r"^\d+(\.\d+)?$", palabra):
                tokens.append(("NUMERO", palabra, idx))
            elif palabra_mayus in TIPOS_SQL_VALIDOS or palabra_mayus in MODIFICADORES_SQL_VALIDOS:
                tokens.append(("TIPO_O_MODIFICADOR", palabra_mayus, idx))
            elif re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", palabra):
                tokens.append(("IDENTIFICADOR", palabra, idx))
                # Solo sugerir si no es palabra clave, tipo ni modificador
                if (
                    palabra_mayus not in PALABRAS_CLAVE_SQL and
                    palabra_mayus not in TIPOS_SQL_VALIDOS and
                    palabra_mayus not in MODIFICADORES_SQL_VALIDOS
                ):
                    sugerencia = sugerir_palabra(palabra)
                    if sugerencia and sugerencia != palabra_mayus:
                        errores.append(f"[Sentencia {idx}] ¿Quisiste decir '{sugerencia}' en vez de '{palabra}'?")
            else:
                errores.append(f"[Sentencia {idx}] Token no reconocido: {palabra}")

        # Validar punto y coma final
        if not sentencia.strip().endswith(";"):
            errores.append(f"[Sentencia {idx}] Falta punto y coma al final.")

    return tokens, errores
