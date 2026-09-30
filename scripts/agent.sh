#!/usr/bin/env bash
# Second local environment for a git worktree. Requires the main one (make up).
set -euo pipefail

cd "$(dirname "$0")/.."

agent_project=carbure-agent

set -a
# shellcheck disable=SC1091
# The Makefile has already exported .env. Reload the agent file so interpolation
# uses its values (MYSQL_DATABASE, AWS_ENV_FOLDER_NAME, WEB_PORT, ...) instead of the main ones.
. ./docker-compose.agent.env
set +a

compose() {
  docker compose -p "$agent_project" \
    --env-file .env \
    --env-file docker-compose.agent.env \
    -f docker-compose.yml \
    -f docker-compose.agent.yml \
    "$@"
}

case "${1:-}" in
  up)
    docker exec -e MYSQL_PWD="$MYSQL_ROOT_PASSWORD" carbure_mysql \
      mysql -uroot -e "CREATE DATABASE IF NOT EXISTS \`${MYSQL_DATABASE}\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    compose up -d carbure-frontend carbure-django carbure-web-proxy
    ;;
  down)
    compose down
    ;;
  logs)
    compose logs -f carbure-django carbure-frontend
    ;;
  *)
    echo "usage: $0 up|down|logs" >&2
    exit 1
    ;;
esac
