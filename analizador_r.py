import re

PALABRAS_CLAVE_R = {
    "function", "if", "else", "for", "while", "repeat", "next", "break", "TRUE", "FALSE", "NULL", "NA"
}

OPERADORES = {
    "<-", "->", "==", "!=", "<", ">", "<=", ">=", "+", "-", "*", "/", "^", "=", "%%", "%/%"
}

SIMBOLOS = {'(', ')', '{', '}', '[', ']', ',', ';'}

def analizar_r(codigo):
    errores = []
    tokens = []

    lineas = codigo.strip().split('\n')
    for num_linea, linea in enumerate(lineas, start=1):
        palabras = re.findall(r"[A-Za-z_][A-Za-z0-9_]*|<-|->|==|!=|<=|>=|[+\-*/^=<>;{},()[\]]|['\"].*?['\"]|\d+(\.\d+)?", linea)

        for palabra in palabras:
            if palabra in PALABRAS_CLAVE_R:
                tokens.append(("PALABRA_CLAVE", palabra, num_linea))
            elif palabra in OPERADORES:
                tokens.append(("OPERADOR", palabra, num_linea))
            elif palabra in SIMBOLOS:
                tokens.append(("SIMBOLO", palabra, num_linea))
            elif re.match(r"^['\"].*['\"]$", palabra):
                tokens.append(("CADENA", palabra, num_linea))
            elif re.match(r"^\d+(\.\d+)?$", palabra):
                tokens.append(("NUMERO", palabra, num_linea))
            elif re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", palabra):
                tokens.append(("IDENTIFICADOR", palabra, num_linea))
            else:
                errores.append(f"[Línea {num_linea}] Token no reconocido: {palabra}")

        # Validaciones sintácticas básicas
        if "<-" in linea and not re.match(r"^\s*[A-Za-z_][A-Za-z0-9_]*\s*<-", linea):
            errores.append(f"[Línea {num_linea}] Posible error de asignación, variable mal definida.")
        if "function" in linea and not re.search(r"function\s*\(", linea):
            errores.append(f"[Línea {num_linea}] Declaración de función incompleta.")

    return errores, tokens
