def explicar_codigo(codigo, lenguaje):
    """
    Explica el código proporcionado, dependiendo del lenguaje.
    Puede usarse incluso si está embebido.
    """
    if lenguaje == "Python":
        return explicar_python(codigo)
    elif lenguaje == "SQL":
        return explicar_sql(codigo)
    elif lenguaje == "R":
        return explicar_r(codigo)
    else:
        return "Lenguaje no reconocido para explicación."


def explicar_python(codigo):
    explicaciones = []

    if "import" in codigo:
        explicaciones.append("📦 Se están importando librerías externas en Python.")
    if "def " in codigo:
        explicaciones.append("🧩 Se está definiendo una función.")
    if "for " in codigo:
        explicaciones.append("🔁 Se utiliza un bucle for para iterar sobre una secuencia.")
    if "if " in codigo:
        explicaciones.append("🔀 Se utiliza una estructura condicional (if).")
    if "print(" in codigo:
        explicaciones.append("🖨️ Se imprime un valor en consola con print().")

    if not explicaciones:
        explicaciones.append("📘 Código Python detectado. No se encontraron estructuras destacables.")

    return "\n".join(explicaciones)


def explicar_sql(codigo):
    explicaciones = []

    if "SELECT" in codigo.upper():
        explicaciones.append("🔍 Se realiza una consulta para seleccionar datos de una tabla.")
    if "FROM" in codigo.upper():
        explicaciones.append("📂 Se especifica la tabla de origen para la consulta.")
    if "WHERE" in codigo.upper():
        explicaciones.append("🔎 Se aplica una condición de filtrado (WHERE).")
    if "JOIN" in codigo.upper():
        explicaciones.append("🔗 Se está uniendo información de varias tablas (JOIN).")
    if "INSERT" in codigo.upper():
        explicaciones.append("📝 Se insertan datos en una tabla.")
    if "UPDATE" in codigo.upper():
        explicaciones.append("🔧 Se actualizan registros existentes en una tabla.")
    if "DELETE" in codigo.upper():
        explicaciones.append("🗑️ Se eliminan registros de una tabla.")

    if not explicaciones:
        explicaciones.append("📘 Código SQL detectado. No se encontraron estructuras destacables.")

    return "\n".join(explicaciones)


def explicar_r(codigo):
    explicaciones = []

    if "<-" in codigo:
        explicaciones.append("📥 Se asigna un valor a una variable usando '<-'.")
    if "plot(" in codigo:
        explicaciones.append("📊 Se genera una gráfica con plot().")
    if "library(" in codigo:
        explicaciones.append("📚 Se carga una librería de funciones con library().")
    if "function(" in codigo:
        explicaciones.append("🧩 Se define una función personalizada.")
    if "for(" in codigo or "for (" in codigo:
        explicaciones.append("🔁 Se está utilizando un bucle for en R.")
    if "if(" in codigo or "if (" in codigo:
        explicaciones.append("🔀 Se utiliza una estructura condicional (if).")

    if not explicaciones:
        explicaciones.append("📘 Código R detectado. No se encontraron estructuras destacables.")

    return "\n".join(explicaciones)
