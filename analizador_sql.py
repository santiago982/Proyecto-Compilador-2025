import re

PALABRAS_CLAVE_SQL = {
    "SELECT", "FROM", "WHERE", "INSERT", "INTO", "VALUES", "UPDATE", "SET",
    "DELETE", "CREATE", "TABLE", "DROP", "ALTER", "JOIN", "INNER", "LEFT", "RIGHT"
}

SIMBOLOS = {';', ',', '(', ')', '=', '<', '>', '*', '.'}

def analizar_sql(codigo):
    errores = []
    tokens = []

    lineas = codigo.strip().split('\n')
    for num_linea, linea in enumerate(lineas, start=1):
        palabras = re.findall(r"[A-Za-z_][A-Za-z_0-9]*|==|<=|>=|!=|[<>]=?|['\"].*?['\"]|[(),=*;]", linea)

        for palabra in palabras:
            if palabra.upper() in PALABRAS_CLAVE_SQL:
                tokens.append(("PALABRA_CLAVE", palabra.upper(), num_linea))
            elif palabra in SIMBOLOS:
                tokens.append(("SIMBOLO", palabra, num_linea))
            elif re.match(r"^['\"].*?['\"]$", palabra):
                tokens.append(("CADENA", palabra, num_linea))
            elif re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", palabra):
                tokens.append(("IDENTIFICADOR", palabra, num_linea))
            elif re.match(r"^\d+$", palabra):
                tokens.append(("NUMERO", palabra, num_linea))
            else:
                errores.append(f"[Línea {num_linea}] Token no reconocido: {palabra}")

        # Validación sintáctica simple
        if re.match(r"(?i)^\s*SELECT\b", linea):
            if "FROM" not in linea.upper():
                errores.append(f"[Línea {num_linea}] Falta cláusula FROM en la sentencia SELECT.")
        elif re.match(r"(?i)^\s*INSERT\b", linea):
            if "INTO" not in linea.upper() or "VALUES" not in linea.upper():
                errores.append(f"[Línea {num_linea}] Falta INTO o VALUES en sentencia INSERT.")
        elif re.match(r"(?i)^\s*UPDATE\b", linea):
            if "SET" not in linea.upper():
                errores.append(f"[Línea {num_linea}] Falta SET en sentencia UPDATE.")
        elif re.match(r"(?i)^\s*DELETE\b", linea):
            if "FROM" not in linea.upper():
                errores.append(f"[Línea {num_linea}] DELETE sin FROM.")

    return errores, tokens
