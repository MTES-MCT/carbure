#!/usr/bin/env bash

# Turn DATABASE_URL into a mysql client command.
#
# The backup app has no Python, so scripts cannot go through Django's dbshell.
# Source this file, then call parse_mysql_url.
#
# Sets MYSQL_DATABASE, MYSQL_USER, MYSQL_HOST, MYSQL_PORT, MYSQL_PASSWORD
# and MYSQL, an array ready to execute. If the URL has no password, one is
# requested interactively.

parse_mysql_url() {
  if [[ -z "${DATABASE_URL:-}" ]]; then
    echo "DATABASE_URL is not defined" >&2
    return 1
  fi

  local url=${DATABASE_URL#*://}
  local auth=${url%%/*}
  local user_info=${auth%@*}
  local host_port=${auth##*@}

  MYSQL_DATABASE=${url#*/}
  MYSQL_DATABASE=${MYSQL_DATABASE%%\?*}
  MYSQL_USER=${user_info%%:*}
  MYSQL_HOST=${host_port%%:*}
  MYSQL_PORT=${host_port#*:}

  if [[ "$user_info" == *:* ]]; then
    MYSQL_PASSWORD=${user_info#*:}
  else
    read -r -s -p "MySQL password: " MYSQL_PASSWORD
    echo
  fi

  MYSQL=(mysql --user="$MYSQL_USER" --password="$MYSQL_PASSWORD" --host="$MYSQL_HOST" --port="$MYSQL_PORT" --protocol=tcp)
}
