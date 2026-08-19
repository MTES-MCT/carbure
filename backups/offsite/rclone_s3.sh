#!/usr/bin/env bash

# Configure an S3-compatible rclone remote without writing credentials to a
# config file. The caller supplies the values explicitly.
#
# Usage:
#   configure_rclone_s3_remote \
#     <remote-name> <endpoint> <access-key-id> <secret-access-key> \
#     [region]

configure_rclone_s3_remote() {
  local remote_name=$1
  local endpoint=$2
  local access_key_id=$3
  local secret_access_key=$4
  local region=${5:-}
  local remote_key

  remote_key=$(printf '%s' "$remote_name" | tr '[:lower:]' '[:upper:]')

  [[ -n "$endpoint" ]] || {
    echo "Missing S3 endpoint for ${remote_name}" >&2
    return 1
  }
  [[ -n "$access_key_id" ]] || {
    echo "Missing S3 access key for ${remote_name}" >&2
    return 1
  }
  [[ -n "$secret_access_key" ]] || {
    echo "Missing S3 secret key for ${remote_name}" >&2
    return 1
  }

  export "RCLONE_CONFIG_${remote_key}_TYPE=s3"
  export "RCLONE_CONFIG_${remote_key}_PROVIDER=Other"
  export "RCLONE_CONFIG_${remote_key}_ENV_AUTH=false"
  export "RCLONE_CONFIG_${remote_key}_ACCESS_KEY_ID=${access_key_id}"
  export "RCLONE_CONFIG_${remote_key}_SECRET_ACCESS_KEY=${secret_access_key}"
  export "RCLONE_CONFIG_${remote_key}_ENDPOINT=${endpoint}"

  if [[ -n "$region" ]]; then
    export "RCLONE_CONFIG_${remote_key}_REGION=${region}"
  fi
}
