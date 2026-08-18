#!/usr/bin/env bash

# Mirror the user-file S3 prefix into the secure backup S3 bucket.
#
# Usage:
#   ./backup_user_files.sh
#
# User-file source variables:
#   USER_FILES_S3_ENDPOINT_URL
#   USER_FILES_S3_ACCESS_KEY_ID
#   USER_FILES_S3_SECRET_ACCESS_KEY
#   USER_FILES_S3_REGION (optional)
#   USER_FILES_S3_BUCKET
#   USER_FILES_S3_PREFIX (optional)
#
# Secure backup destination variables:
#   SECURE_BACKUP_S3_ENDPOINT_URL
#   SECURE_BACKUP_S3_ACCESS_KEY_ID
#   SECURE_BACKUP_S3_SECRET_ACCESS_KEY
#   SECURE_BACKUP_S3_BUCKET_USER_FILES
#
# rclone sync makes the destination prefix match the source prefix: existing
# objects are overwritten and destination-only objects are deleted.

set -euo pipefail

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
source "$script_dir/rclone_s3.sh"

source_bucket=${USER_FILES_S3_BUCKET:-}
destination_bucket=${SECURE_BACKUP_S3_BUCKET_USER_FILES:-}
source_prefix=${USER_FILES_S3_PREFIX:-}

configure_rclone_s3_remote source \
  "${USER_FILES_S3_ENDPOINT_URL:-}" \
  "${USER_FILES_S3_ACCESS_KEY_ID:-}" \
  "${USER_FILES_S3_SECRET_ACCESS_KEY:-}" \
  "${USER_FILES_S3_REGION:-}"

configure_rclone_s3_remote destination \
  "${SECURE_BACKUP_S3_ENDPOINT_URL:-}" \
  "${SECURE_BACKUP_S3_ACCESS_KEY_ID:-}" \
  "${SECURE_BACKUP_S3_SECRET_ACCESS_KEY:-}"

source_path="source:${source_bucket}"
destination_path="destination:${destination_bucket}"

if [[ -n "$source_prefix" ]]; then
  source_path="${source_path%/}/${source_prefix#/}"
  destination_path="${destination_path%/}/${source_prefix#/}"
fi

echo "> Syncing user files to ${destination_bucket}"
rclone sync \
  --checksum \
  --stats 30s \
  --retries 3 \
  --low-level-retries 10 \
  "$source_path" \
  "$destination_path"

echo "> User-file backup complete"
