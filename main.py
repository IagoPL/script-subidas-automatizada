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

# Función para registrar mensajes (No será necesaria ya que todo será redirigido)
log_message() {
    echo "$1"  # Solo imprime el mensaje
}

# Redirige toda la salida y errores al archivo de log y también a la consola
exec &> >(tee -a "$LOG_FILE")

echo "Iniciando Script"

# Función para subir los archivos al repositorio de GitHub
git_push() {
    local folder_path="$1"
    local repo_url="$2"
    local branch="${3:-}"

    echo "Iniciando subida para $folder_path hacia $repo_url${branch:+ en la rama $branch}."

    cd "$folder_path" || exit

    # Inicializa git si no está inicializado
    if [ ! -d ".git" ]; then
        git init
        git remote add origin "$repo_url"
        echo "Repositorio git inicializado y remoto configurado."
    else
        git remote set-url origin "$repo_url"
        echo "URL del remoto actualizada."
    fi

    # Añade todos los archivos
    git add .
    echo "Archivos añadidos al staging."

    # Commit y push
    if git commit -m "Automated commit"; then
        echo "Commit realizado exitosamente."
        git push --set-upstream origin $(git rev-parse --abbrev-ref HEAD)
        echo "Push realizado exitosamente."
    else
        echo "Error al realizar commit. No hay cambios para commit o hubo un error."
    fi
}

# Leer el archivo de configuración y procesar cada línea
while IFS=, read -r path repo branch
do
    if [[ -n "$path" && -n "$repo" ]]; then
        git_push "$path" "$repo" "$branch"
    fi
done < "$CONFIG_FILE"

echo "Script finalizado."
