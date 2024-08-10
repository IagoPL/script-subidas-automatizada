#!/bin/bash

# Configuración
MAX_FILE_SIZE=104857600  # Máximo tamaño de archivo en bytes (100 MB)
LOG_DIR="logs"
DATE=$(date +"%Y-%m-%d_%H-%M-%S")
LOG_FILE="$LOG_DIR/git_upload_$DATE.log"
CONFIG_FILE="rutas.txt"

# Crear carpeta de logs y archivo si no existen
mkdir -p "$LOG_DIR"
touch "$LOG_FILE"

# Redirige toda la salida y errores al archivo de log y también a la consola
exec &> >(tee -a "$LOG_FILE")

echo "Iniciando Script"

# Función para manejar la subida de archivos al repositorio de GitHub
process_directory() {
    local folder_path="$1"
    local repo_url="$2"
    local branch="${3:-}"

    echo "Revisando $folder_path para cambios..."
    cd "$folder_path" || { echo "Error al cambiar al directorio $folder_path"; return 1; }

    # Verifica si hay cambios en el directorio
    if ! git diff-index --quiet HEAD --; then
        echo "Cambios detectados en $folder_path. Iniciando subida..."

        # Inicializa git si no está inicializado
        if [ ! -d ".git" ]; then
            git init
            git remote add origin "$repo_url"
            echo "Repositorio git inicializado y remoto configurado."
        else
            git remote set-url origin "$repo_url"
            echo "URL del remoto actualizada."
        fi

        git add .
        echo "Archivos añadidos al staging."

        # Commit y push
        if git commit -m "Automated commit"; then
            echo "Commit realizado exitosamente."
            git push --set-upstream origin $(git rev-parse --abbrev-ref HEAD)
            echo "Push realizado exitosamente."
        else
            echo "Error al realizar commit."
        fi
    else
        echo "No se detectaron cambios en $folder_path. No se realiza subida."
    fi
}

# Leer el archivo de configuración y procesar cada línea
while IFS=, read -r path repo branch || [[ -n "$path" ]]
do
    echo "Procesando: $path, $repo, $branch"
    if [[ -n "$path" && -n "$repo" ]]; then
        process_directory "$path" "$repo" "$branch"
    else
        echo "Línea de configuración inválida: $path, $repo, $branch"
    fi
done < "$CONFIG_FILE"

echo "Script finalizado."
