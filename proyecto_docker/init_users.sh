#!/bin/bash

CONTAINER_NAME=proyecto_docker_api_1

echo "==> Esperando a que el contenedor $CONTAINER_NAME inicie..."
while ! docker ps | grep -q "$CONTAINER_NAME"; do
    sleep 1
done

echo "==> Obteniendo usuarios locales del host..."

# Lista solo usuarios con UID >= 1000 (usuarios reales, no del sistema)
USERNAMES=$(awk -F: '$3 >= 1000 && $3 < 65534 {print $1}' /etc/passwd)

for USER in $USERNAMES; do
    echo "==> Creando usuario $USER en el contenedor..."

    docker exec "$CONTAINER_NAME" bash -c "
        if ! id \"$USER\" &>/dev/null; then
            useradd -m \"$USER\"
            echo \"$USER:default123\" | chpasswd
            mkdir -p \"/home/$USER/public_html\"
            chmod 755 \"/home/$USER/public_html\"
        else
            echo \"Usuario $USER ya existe en el contenedor\"
        fi
    "
done

echo "==> Todos los usuarios han sido creados con la contraseña: default123"
