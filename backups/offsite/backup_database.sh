#!/usr/bin/env bash

# Download the latest successful Scalingo database backup and upload it to
# the secure backup S3 bucket.
#
# Usage:
#   ./backup_database.sh <scalingo-app>
#
# Scalingo variables:
#   SCALINGO_TOKEN
#
# Secure backup destination variables:
#   SECURE_BACKUP_S3_ENDPOINT_URL
#   SECURE_BACKUP_S3_ACCESS_KEY_ID
#   SECURE_BACKUP_S3_SECRET_ACCESS_KEY
#   SECURE_BACKUP_S3_BUCKET_DATABASE

set -euo pipefail

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
source "$script_dir/rclone_s3.sh"

scalingo_app=$1
destination_bucket=${SECURE_BACKUP_S3_BUCKET_DATABASE:-}

if [[ -z "$scalingo_app" ]]; then
  echo "scalingo_app must be provided as the first argument" >&2
  exit 1
fi

if [[ -z "$destination_bucket" ]]; then
  echo "SECURE_BACKUP_S3_BUCKET_DATABASE must be provided" >&2
  exit 1
fi

configure_rclone_s3_remote destination \
  "${SECURE_BACKUP_S3_ENDPOINT_URL:-}" \
  "${SECURE_BACKUP_S3_ACCESS_KEY_ID:-}" \
  "${SECURE_BACKUP_S3_SECRET_ACCESS_KEY:-}"

backup_dir=$(mktemp -d "/tmp/scalingo-backup.XXXXXX")
trap 'rm -rf -- "$backup_dir"' EXIT

"$script_dir/../database/download_scalingo_backup.sh" "$scalingo_app" "$backup_dir"

shopt -s nullglob
backup_files=("$backup_dir"/*.tar.gz)
shopt -u nullglob

if [[ ${#backup_files[@]} -ne 1 ]]; then
  echo "Expected exactly one tar.gz backup in ${backup_dir}, found ${#backup_files[@]}" >&2
  exit 1
fi

backup_file=${backup_files[0]}
backup_path=$(date -u +%Y/%m/%d.tar.gz)

echo "> Uploading database backup to ${destination_bucket}/${scalingo_app}/${backup_path}"
rclone copyto \
  --checksum \
  --stats 30s \
  --retries 3 \
  --low-level-retries 10 \
  "$backup_file" \
  "destination:${destination_bucket%/}/${scalingo_app%/}/${backup_path}"

echo "> Database backup upload complete"
