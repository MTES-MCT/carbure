#!/bin/bash

function loaddotenv() {
    set -o allexport; source .env; set +o allexport
}

loaddotenv
export MYSQL_HOST="$(docker inspect --format '{{ .NetworkSettings.Networks.carbure_default.IPAddress }}' carbure_mariadb)"
export MYSQL_PORT=3306
export PYTHONPATH="$CARBURE_HOME/web:$CARBURE_HOME"
export ALLOWED_HOSTS="carbure.local"
source venv/bin/activate
