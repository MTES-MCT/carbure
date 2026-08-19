#!/usr/bin/env bash

# Restore a MySQL database from a Scalingo tar.gz backup.
#
# Usage:
#   ./restore_local_backup.sh <dir|file> [database-url]
#
# Example:
#   ./restore_local_backup.sh /tmp/backups
#   ./restore_local_backup.sh /tmp/backups/backup.tar.gz mysql://user@host:port/database
#
# The database URL defaults to $DATABASE_URL. If it has no password, one is requested interactively.
# When specifying the database-url parameter in your cli, avoid letting the password inside.

set -euo pipefail

backup_path=$1
DATABASE_URL=${2:-${DATABASE_URL:-}}

if [[ -z "$backup_path" ]]; then
  echo "backup_path must be provided as the first argument" >&2
  exit 1
fi

if [[ -z "$DATABASE_URL" ]]; then
  echo "DATABASE_URL is not defined" >&2
  exit 1
fi

if [[ -d "$backup_path" ]]; then
  backup_files=("$backup_path"/*.tar.gz)
  backup_file=${backup_files[0]}
else
  backup_file=$backup_path
fi

URL=${DATABASE_URL#*://}
AUTH=${URL%%/*}
USER_INFO=${AUTH%@*}
HOST_PORT=${AUTH##*@}

MYSQL_DATABASE=${URL#*/}
MYSQL_DATABASE=${MYSQL_DATABASE%%\?*}
MYSQL_USER=${USER_INFO%%:*}
MYSQL_HOST=${HOST_PORT%%:*}
MYSQL_PORT=${HOST_PORT#*:}

# Extract password from DATABASE_URL if present, otherwise prompt the user
if [[ "$USER_INFO" == *:* ]]; then
  MYSQL_PASSWORD=${USER_INFO#*:}
else
  read -r -s -p "MySQL password: " MYSQL_PASSWORD
  echo
fi

MYSQL=(mysql --user="$MYSQL_USER" --password="$MYSQL_PASSWORD" --host="$MYSQL_HOST" --port="$MYSQL_PORT" --protocol=tcp)

echo "> Recreating database '$MYSQL_DATABASE'..."
"${MYSQL[@]}" -e "DROP DATABASE IF EXISTS \`$MYSQL_DATABASE\`;"
"${MYSQL[@]}" -e "CREATE DATABASE \`$MYSQL_DATABASE\`;"

echo "> Restoring '$MYSQL_DATABASE' from '$backup_file'..."

# Remove CREATE DATABASE and USE statements near the top of the Scalingo dumps,
# then stream the resulting SQL directly into MySQL.
tar -xOzf "$backup_file" "*.sql" |
  sed -E '1,50 {
    /^[[:space:]]*CREATE[[:space:]]+DATABASE([[:space:]]|$)/d
    /^[[:space:]]*USE([[:space:]]|$)/d
  }' |
  "${MYSQL[@]}" "$MYSQL_DATABASE"

echo "> Restoration complete"
