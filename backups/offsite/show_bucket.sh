#!/usr/bin/env bash

# List the content of a given bucket on B3
#
# Usage:
#   ./show_bucket.sh <bucket>
#
# The content will be shown as a file tree, with file and folder sizes specified.

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
source "$script_dir/rclone_s3.sh"

configure_rclone_s3_remote destination \
  "$SECURE_BACKUP_S3_ENDPOINT_URL" \
  "$SECURE_BACKUP_S3_ACCESS_KEY_ID" \
  "$SECURE_BACKUP_S3_SECRET_ACCESS_KEY"

rclone tree "destination:$1" --max-depth 5 --size --human-readable
