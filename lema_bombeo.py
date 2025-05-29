import re

def verificar_repeticiones(codigo):
    """
    Aplica una verificación estructural usando una heurística basada en el lema de bombeo.
    No es una demostración formal, pero busca repeticiones sospechosas y bucles redundantes.
    """
    repeticiones_sospechosas = []

    # Conteo de estructuras repetitivas exactas
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

    # Búsqueda de patrones que podrían indicar repeticiones o bucles infinitos
    if re.search(r'while\s*\(.*true.*\)', codigo, re.IGNORECASE):
        repeticiones_sospechosas.append("⚠️ Posible bucle infinito detectado: 'while(true)'")

    if re.findall(r'(for\s*\(.*\))', codigo):
        for_loops = re.findall(r'for\s*\(.*?\)', codigo)
        for loop in for_loops:
            if '1:Inf' in loop or '1:1000000' in loop:
                repeticiones_sospechosas.append(f"⚠️ Posible bucle sospechoso: {loop}")

    return repeticiones_sospechosas
