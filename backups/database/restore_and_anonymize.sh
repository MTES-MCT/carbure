#!/usr/bin/env bash

# Restore a production dump, apply Django migrations, then anonymize personal
# identifiers (user emails/names and entity contact fields).
#
# Usage:
#   ./restore_and_anonymize.sh local <backup-dir|backup-file> [database-url]
#   ./restore_and_anonymize.sh scalingo <scalingo-app> [database-url]
#
# Example:
#   ./restore_and_anonymize.sh scalingo carbure-prod "$READ_REPLICA_DATABASE_URL"
#
# The database URL must be passed as an argument or set in $DATABASE_URL.

set -euo pipefail

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)

"$script_dir/restore.sh" "$@"
"$script_dir/anonymize.sh" "${3:-${DATABASE_URL:-}}"
