#!/usr/bin/env bash

# Restore a local Scalingo backup or download and restore the latest successful
# backup for a Scalingo MySQL addon, then apply the project's latest Django migrations.
#
# Usage:
#   ./restore.sh local <backup-dir|backup-file> [database-url]
#   ./restore.sh scalingo <scalingo-app> [database-url]
#
# Example:
#   ./restore.sh local /tmp/backups
#   ./restore.sh local /tmp/backups/backup.tar.gz
#   ./restore.sh scalingo carbure-prod
#
# The database URL must be passed as an argument or set in $DATABASE_URL. If it has no password,
# the restore script asks for one interactively. Avoid putting the password in a command-line URL.

set -euo pipefail

backup_source=$1
backup_location=$2
database_url=${3:-${DATABASE_URL:-}}

if [[ -z "$backup_source" ]]; then
  echo "backup_source must be provided as the first argument" >&2
  exit 1
fi

if [[ -z "$backup_location" ]]; then
  echo "backup_location must be provided as the second argument" >&2
  exit 1
fi

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
project_root=$(cd -- "$script_dir/../.." && pwd)

if [[ "$backup_source" == "local" ]]; then
  backup_path=$backup_location
elif [[ "$backup_source" == "scalingo" ]]; then
  backup_dir=$(mktemp -d "/tmp/scalingo-backup.XXXXXX")

  # Clean up the downloaded backup once the script exits, after success or failure.
  trap 'rm -rf -- "$backup_dir"' EXIT

  "$script_dir/download_scalingo_backup.sh" "$backup_location" "$backup_dir"
  backup_path=$backup_dir
fi

"$script_dir/restore_local_backup.sh" "$backup_path" "$database_url"

(
  cd -- "$project_root"
  DATABASE_URL="$database_url" python web/manage.py migrate
)

echo "> Database is ready"
