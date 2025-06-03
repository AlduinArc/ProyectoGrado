#!/bin/bash

# Crear usuario por defecto
if id "usuario1" &>/dev/null; then
    echo "usuario1 ya existe"
else
    useradd -m usuario1
    echo "usuario1:clave123" | chpasswd
    mkdir -p /home/usuario1/public_html
    chmod 755 /home/usuario1/public_html
    echo "usuario1 creado"
fi

# Ejecuta el comando original (por ejemplo, gunicorn, flask run, etc.)
exec "$@"
