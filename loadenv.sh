#!/bin/bash

function loaddotenv() {
    set -o allexport; source .env; set +o allexport
}

loaddotenv
export DJANGO_DB_HOST="$(docker inspect --format '{{ .NetworkSettings.Networks.carbure_default.IPAddress }}' carbure_mariadb)"
export DJANGO_DB_PORT=3306
export DJANGO_NGINX_HOST="$(docker inspect --format '{{ .NetworkSettings.Networks.carbure_default.IPAddress }}' carbure_web)"
export PYTHONPATH="$CARBURE_HOME/web:$CARBURE_HOME"
source venv/bin/activate
