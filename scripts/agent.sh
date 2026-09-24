#!/usr/bin/env bash
# Second local environment for a git worktree. Requires the main one (make up).
set -euo pipefail

cd "$(dirname "$0")/.."

agent_project=carbure-agent
agent_database=carbure_agent

compose() {
  set -a
  # shellcheck disable=SC1091
  . ./docker-compose.agent.env
  set +a
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
      mysql -uroot -e "CREATE DATABASE IF NOT EXISTS \`${agent_database}\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
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
