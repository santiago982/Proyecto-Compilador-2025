import re
from difflib import get_close_matches

# Palabras clave de R
PALABRAS_CLAVE_R = {
    "if", "else", "for", "while", "repeat", "in", "function", "return",
    "break", "next", "TRUE", "FALSE", "NULL", "NA", "NA_integer_", "NA_real_", "NA_complex_", "NA_character_"
    
}

OPERADORES_R = {"<-", "->", "=", "+", "-", "*", "/", "%%", "%/%", "^", "==", "!=", "<", ">", "<=", ">=", "&", "|", "!", ":"}

SIMBOLOS_R = {"(", ")", "{", "}", "[", "]", ",", ";"}

FUNCIONES_BUILTIN_R = {
    "print", "cat", "mean", "sum", "min", "max", "length", "seq", "rep", "paste",
    "c", "matrix", "data.frame", "list", "as.numeric", "as.character", "as.logical","print", "cat", "summary", "head", "tail", "length", "nrow", "ncol", "class", "typeof", "str",
    "mean", "median", "sd", "var", "cor", "lm", "plot", "hist", "boxplot", "barplot", "table",
    "factor", "as.factor", "levels", "gl", "rep", "seq", "c", "paste", "paste0", "unique",
    "install.packages", "library", "require", "read.csv", "read.table", "write.csv", "colnames", "rownames", "names",
    "data.frame", "matrix", "array", "list", "tibble", "subset", "merge", "rbind", "cbind",
    "mutate", "filter", "select", "group_by", "summarise", "arrange", "separate", "spread", "gather",
    "ggplot", "aes", "geom_point", "geom_line", "geom_bar", "geom_histogram", "theme", "labs", "scale_x", "scale_y",
    "model.matrix", "as.numeric", "as.character", "as.logical", "dummyVars", "sqldf", "gsub"

}

def sugerir_r(token):
    candidatos = PALABRAS_CLAVE_R.union(FUNCIONES_BUILTIN_R)
    sugerencias = get_close_matches(token, candidatos, n=1)
    return sugerencias[0] if sugerencias else None

def detectar_sql_embebido(linea):
    return any(comando in linea.upper() for comando in ["SELECT", "INSERT", "UPDATE", "DELETE", "CREATE"])

def analizar_r(codigo):
    errores = []
    tokens = []

    lineas = codigo.strip().split('\n')

    for idx, linea in enumerate(lineas, start=1):
        linea = linea.strip()

        if not linea:
            continue

        # Detectar posible SQL embebido
        if detectar_sql_embebido(linea):
            errores.append(f"[Línea {idx}] SQL detectado embebido en R. Usa el analizador SQL para esa porción.")
            tokens.append(("SQL_EMBEBIDO", linea, idx))
            continue

        # Tokenización básica en R
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
            elif re.match(r'^".*"$', palabra) or re.match(r"^'.*'$", palabra):
                tokens.append(("CADENA", palabra, idx))
            elif re.match(r"^\d+(\.\d+)?$", palabra):
                tokens.append(("NUMERO", palabra, idx))
            elif re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", palabra):
                tokens.append(("IDENTIFICADOR", palabra, idx))
            else:
                sugerencia = sugerir_r(palabra)
                if sugerencia:
                    errores.append(f"[Línea {idx}] ¿Quisiste decir '{sugerencia}' en vez de '{palabra}'?")
                else:
                    errores.append(f"[Línea {idx}] Token no reconocido: {palabra}")

    return tokens, errores
