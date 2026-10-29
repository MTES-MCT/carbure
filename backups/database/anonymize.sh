#!/usr/bin/env bash

# Anonymize personal identifiers in a restored database (users and entity contacts).
#
# Usage:
#   ./anonymize.sh [database-url]
#
# Example:
#   ./anonymize.sh mysql://user:password@host:3306/database
#
# The database URL defaults to $DATABASE_URL. If it has no password, one is requested interactively.

set -euo pipefail

DATABASE_URL=${1:-${DATABASE_URL:-}}

if [[ -z "$DATABASE_URL" ]]; then
  echo "DATABASE_URL is not defined" >&2
  exit 1
fi

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)

# shellcheck source=mysql_url.sh
source "$script_dir/mysql_url.sh"
parse_mysql_url

echo "> Anonymizing personal data..."
"${MYSQL[@]}" "$MYSQL_DATABASE" --batch < "$script_dir/anonymize.sql"
echo "> Anonymization complete"
