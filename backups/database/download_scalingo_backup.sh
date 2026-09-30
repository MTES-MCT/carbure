#!/usr/bin/env bash

# Download the latest successful backup for a Scalingo addon.
#
# Usage:
#   ./download_scalingo_backup.sh <scalingo-app> [output-directory]
#
# Example:
#   ./download_scalingo_backup.sh carbure-prod /tmp/backups/
#   SCALINGO_TOKEN=my-token ./download_scalingo_backup.sh carbure-prod /tmp/backups/
#
# The backup is downloaded from the osc-secnum-fr1 region. 
# Set SCALINGO_TOKEN to log in automatically, otherwise an existing Scalingo CLI session is reused. 
# The output directory defaults to the current directory.

set -euo pipefail

if (( $# < 1 )) || [[ -z "$1" ]]; then
  echo "Usage: $0 <scalingo-app> [output-directory]" >&2
  exit 1
fi

app="$1"
output_dir="${2:-.}"

mkdir -p "$output_dir"

if ! command -v scalingo >/dev/null 2>&1; then
  if command -v install-scalingo-cli >/dev/null 2>&1; then
    install-scalingo-cli
  else
    echo "Error: scalingo-cli is not installed" >&2
    exit 1
  fi
fi

if ! command -v mysql >/dev/null 2>&1; then
  if command -v dbclient-fetcher >/dev/null 2>&1; then
    dbclient-fetcher mysql 8
  else
    echo "Error: mysql cli is not installed" >&2
    exit 1
  fi
fi

if [ -n "${SCALINGO_TOKEN:-}" ]; then
  scalingo login --api-token "$SCALINGO_TOKEN"
fi

scalingo \
  --region osc-secnum-fr1 \
  --app "$app" \
  --addon mysql \
  backups-download \
  --output "$output_dir"

echo "> Downloaded backup archive to $output_dir"
