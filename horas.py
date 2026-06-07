import re

def estandarizar_archivo_horarios(ruta_fichero):
    """
    Lee un archivo de texto con expresiones temporales coloquiales y las
    reemplaza por su representación digital en formato militar (HH:MM).
    Los cambios se guardan directamente sobrescribiendo el archivo original.
    """
    
    def procesar_patron_estandar(coincidencia):
        # Extraer componentes capturados usando grupos posicionales en lugar de nombres
        hora_int = int(coincidencia.group(1))
        minutos_str = coincidencia.group(3)
        periodo_dia = coincidencia.group(5)

        minutos_int = int(minutos_str) if minutos_str else 0

        # Validación estricta de rangos horarios válidos
        if minutos_int >= 60 or hora_int >= 24:
            return coincidencia.group(0)

        # Ajuste de franja horaria (conversión a formato 24h)
        if periodo_dia:
            periodo_dia = periodo_dia.lower()
            if periodo_dia in ['tarde', 'noche'] and hora_int < 12:
                hora_int += 12
            elif periodo_dia in ['mañana', 'noche'] and hora_int == 12:
                hora_int = 0

        return f"{hora_int:02d}:{minutos_int:02d}"

    def limpiar_expresiones_coloquiales(contenido_texto):
        # Caso A: Expresiones tipo "X y media de la ..."
        contenido_texto = re.sub(
            r'(?<!\d)(\d{1,2})\s+y\s+media\s+de\s+la\s+(mañana|tarde|noche)',
            lambda m: f"{int(m.group(1)) + (12 if m.group(2).lower() in ['tarde', 'noche'] and int(m.group(1)) < 12 else 0):02d}:30",
            contenido_texto, flags=re.IGNORECASE
        )

        # Caso B: Expresiones tipo "X menos cuarto"
        contenido_texto = re.sub(
            r'(?<!\d)(\d{1,2})\s+menos\s+cuarto',
            lambda m: f"{(int(m.group(1)) - 1) % 24:02d}:45",
            contenido_texto, flags=re.IGNORECASE
        )

        # Caso C: Expresiones fijas "X en punto"
        contenido_texto = re.sub(
            r'(?<!\d)(\d{1,2})\s+en\s+punto',
            lambda m: f"{int(m.group(1)):02d}:00",
            contenido_texto, flags=re.IGNORECASE
        )

        # Caso D: Medianoche explícita
        contenido_texto = re.sub(
            r'12\s+de\s+la\s+noche',
            '00:00',
            contenido_texto, flags=re.IGNORECASE
        )

        return contenido_texto

    # Expresión regular principal modificada utilizando grupos por posición en vez de (?P<name>)
    regex_horas = re.compile(
        r'(?<!\d)(\d{1,2})\s*(h|:)?\s*(\d{1,2})?\s*(m|min)?(?:\s+de\s+la\s+(mañana|tarde|noche))?',
        flags=re.IGNORECASE
    )

    # Lectura del archivo original
    with open(ruta_fichero, mode='r', encoding='utf-8') as archivo_lectura:
        lineas_originales = archivo_lectura.readlines()

    lineas_procesadas = []
    for renglon in lineas_originales:
        # Aplicar primero el filtro de frases hechas y luego el formato numérico
        renglon_modificado = limpiar_expresiones_coloquiales(renglon)
        renglon_modificado = regex_horas.sub(procesar_patron_estandar, renglon_modificado)

        # Asegurar el salto de línea al final del registro
        if not renglon_modificado.endswith('\n'):
            renglon_modificado += '\n'
        lineas_procesadas.append(renglon_modificado)

    # Volcado de datos final sobre el mismo fichero
    with open(ruta_fichero, mode='w', encoding='utf-8') as archivo_escritura:
        archivo_escritura.writelines(lineas_procesadas)