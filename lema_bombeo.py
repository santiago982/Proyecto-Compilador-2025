import re

def pertenece_a_lenguaje_regular(cadena, expresion_regular):
    """
    Verifica si la cadena cumple con una expresión regular.
    """
    patron = re.compile(expresion_regular)
    return bool(patron.fullmatch(cadena))

def aplicar_lema_de_bombeo(cadena, constante_n=10):
    """
    Aplica una versión simplificada del lema de bombeo.
    Busca descomposición w = uvz tal que:
      - |uv| <= n
      - v ≠ ε
      - uvⁱz ∈ L (para algunos i)
    """
    longitud = len(cadena)
    resultado = {
        "longitud": longitud,
        "constante_n": constante_n,
        "uvz": None,
        "resultado": "",
        "ejemplos": []
    }

    if longitud < constante_n:
        resultado["resultado"] = "La cadena es demasiado corta para aplicar el lema de bombeo (|w| < n)."
        return resultado

    for i in range(1, constante_n):  # |uv| ≤ n
        u = cadena[:i]
        for j in range(1, constante_n - i + 1):
            v = cadena[i:i + j]
            z = cadena[i + j:]

            if v:  # v ≠ ε
                resultado["uvz"] = (u, v, z)
                ejemplos = [(k, u + v * k + z) for k in range(3)]
                resultado["ejemplos"] = ejemplos
                resultado["resultado"] = "✅ Se encontró una descomposición válida según el lema de bombeo."
                return resultado

    resultado["resultado"] = "⚠️ No se encontró una descomposición válida uvz que cumpla el lema."
    return resultado

def verificar_repeticiones(codigo):
    """
    Heurística para detectar repeticiones y bucles sospechosos en el código.
    """
    repeticiones_sospechosas = []
    
    
    lineas = [line.strip() for line in codigo.strip().split('\n') if line.strip()]
    contador = {}

    for linea in lineas:
        if linea in contador:
            contador[linea] += 1
        else:
            contador[linea] = 1

    for linea, cantidad in contador.items():
        if cantidad >= 3:
            repeticiones_sospechosas.append(f"Línea repetida {cantidad} veces: '{linea}'")


    if re.search(r'while\s*\(.*true.*\)', codigo, re.IGNORECASE):
        repeticiones_sospechosas.append("⚠️ Posible bucle infinito detectado: 'while(true)'")

    if re.findall(r'(for\s*\(.*\))', codigo):
        for_loops = re.findall(r'for\s*\(.*?\)', codigo)
        for loop in for_loops:
            if '1:Inf' in loop or '1:1000000' in loop:
                repeticiones_sospechosas.append(f"⚠️ Posible bucle sospechoso: {loop}")

    return repeticiones_sospechosas
