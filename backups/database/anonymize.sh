#!/usr/bin/env bash

# Anonymize personal identifiers in a restored database (users and entity contacts).
#
# Usage:
#   ./anonymize.sh [database-url]
#
# Example:
#   ./anonymize.sh mysql://user:password@host:3306/database
#
# The database URL defaults to $DATABASE_URL.

set -euo pipefail

DATABASE_URL=${1:-${DATABASE_URL:-}}

if [[ -z "$DATABASE_URL" ]]; then
  echo "DATABASE_URL is not defined" >&2
  exit 1
fi

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
project_root=$(cd -- "$script_dir/../.." && pwd)

echo "> Anonymizing personal data..."
(
  cd -- "$project_root"
  DATABASE_URL="$DATABASE_URL" python web/manage.py dbshell -- --batch < "$script_dir/anonymize.sql"
)
echo "> Anonymization complete"
