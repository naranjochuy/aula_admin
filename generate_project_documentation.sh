#!/bin/bash

# Nombre del archivo de salida
archivo_salida="documentacion_del_proyecto.txt"

# Función para escribir la estructura de directorios de manera recursiva
function escribir_esquema {
    local dir_raiz="$1"
    local indent="$2"
    
    # Encuentra todos los elementos (directorios/archivos) en el directorio actual
    for elemento in $(ls -A "$dir_raiz"); do
        # Omite los directorios y archivos específicos
        if [[ "$elemento" == "venv" || "$elemento" == "node_modules" || "$elemento" == .* ]]; then
            continue
        fi
        
        # Concatenar la ruta completa del elemento
        local ruta_elemento="$dir_raiz/$elemento"
        
        # Si es un directorio, recursivamente llamar a "escribir_esquema"
        if [ -d "$ruta_elemento" ]; then
            echo "${indent}${elemento}/" >> "$archivo_salida"
            escribir_esquema "$ruta_elemento" "${indent}    "
        else
            echo "${indent}${elemento}" >> "$archivo_salida"
        fi
    done
}

# Generar el esquema de carpetas en el archivo de salida
echo "### ESQUEMA DE CARPETAS ###" > "$archivo_salida"
echo "------------" >> "$archivo_salida"
escribir_esquema "." "" # Comienza desde la raíz donde se ejecuta el script
echo "" >> "$archivo_salida" # Espacio en blanco

# Función para escribir el contenido de los archivos
function escribir_contenido_archivos {
    local dir_raiz="$1"
    
    # Encuentra todos los elementos (directorios/archivos) en el directorio actual
    for elemento in $(ls -A "$dir_raiz"); do
        # Omite los directorios específicos
        if [[ "$elemento" == "venv" || "$elemento" == "node_modules" || "$elemento" == .* ]]; then
            continue
        fi
        
        # Concatenar la ruta completa del elemento
        local ruta_elemento="$dir_raiz/$elemento"
        
        # Continuar si es un directorio
        if [ -d "$ruta_elemento" ]; then
            escribir_contenido_archivos "$ruta_elemento"
        else
            # Verifica la extensión del archivo y excluye __init__.py
            if [[ ("$elemento" == *.py || "$elemento" == *.sql || "$elemento" == *.md || "$elemento" == *.yml) && "$elemento" != "__init__.py" ]]; then
                echo "### FILE: $ruta_elemento" >> "$archivo_salida"
                echo "------------" >> "$archivo_salida"
                cat "$ruta_elemento" >> "$archivo_salida"
                echo "" >> "$archivo_salida" # Espacio entre archivos
            fi
        fi
    done
}

# Agregar el contenido de los archivos al archivo de salida
escribir_contenido_archivos "."

echo "Se ha generado el archivo $archivo_salida con el contenido y el esquema de carpetas."