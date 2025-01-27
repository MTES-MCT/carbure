#!/bin/bash

set -e

if [ -z "$1" ]; then
  SOURCE_ENV="carbure-prod"
else
  SOURCE_ENV=$1
fi

if [ "$2" ]; then
  DATABASE_URL=$2
fi

if [ "$SOURCE_ENV" = "carbure-prod" ]; then
  SCALINGO_MYSQL_UUID="ad-5fac8322-ec5b-4fe3-89ed-468e9895f180"
  SCALINGO_MYSQL_DB="carbure_pro_"
elif [ "$SOURCE_ENV" = "carbure-dev" ]; then
  SCALINGO_MYSQL_UUID="ad-60b35da0-a857-4ca0-a779-9419088dc724"
  SCALINGO_MYSQL_DB="carbure_dev_"
fi

# setup scalingo on servers
if [ "$IMAGE_TAG" = "dev" ] || [ "$IMAGE_TAG" = "staging" ] || [ "$IMAGE_TAG" = "prod" ]; then
  dbclient-fetcher mysql 8
  install-scalingo-cli && scalingo login --api-token $SCALINGO_TOKEN
fi

# This condition is useful when you want to use a local database dump,
# for example, to debug a particular version.
if [ "$1" != "local" ]; then
  # clean up any previous local backup
  rm -rf /tmp/backups
  mkdir -p /tmp/backups

  # download latest backup
  scalingo --region osc-secnum-fr1 --app $SOURCE_ENV --addon $SCALINGO_MYSQL_UUID backups-download --output /tmp/backups
fi

# decompress backup
echo "> Decompressing backup..."
tar -xzf /tmp/backups/*.tar.gz -C /tmp/backups

# remove lines mentionning production database
echo "> Cleaning SQL..."
grep -vE "(${SCALINGO_MYSQL_DB})" /tmp/backups/*.sql > /tmp/backups/backup.sql

# extract DATABASE_URL parts
export MYSQL_DATABASE=$(echo $DATABASE_URL | cut -d'/' -f4 | cut -d'?' -f1)
export DB_DETAILS=$(echo $DATABASE_URL | cut -d'/' -f3)
export MYSQL_HOST=$(echo $DB_DETAILS | cut -d'@' -f2 | cut -d':' -f1)
export MYSQL_PORT=$(echo $DB_DETAILS | cut -d'@' -f2 | cut -d':' -f2)
export MYSQL_USER=$(echo $DB_DETAILS | cut -d'@' -f1 | cut -d':' -f1)
export MYSQL_PASSWORD=$(echo $DB_DETAILS | cut -d'@' -f1 | cut -d':' -f2)

shopt -s expand_aliases # allow aliases inside script
alias carbure-mysql="mysql --user=$MYSQL_USER --password=$MYSQL_PASSWORD --host=$MYSQL_HOST --port=$MYSQL_PORT --protocol=tcp"

# Clean up old database
echo "> Cleaning previous database '$MYSQL_DATABASE'..."
carbure-mysql -e "DROP DATABASE \`$MYSQL_DATABASE\`;"
carbure-mysql -e "CREATE DATABASE \`$MYSQL_DATABASE\`;"

# Restore the backup
echo "> Restoring backup in database..."
carbure-mysql $MYSQL_DATABASE < /tmp/backups/backup.sql

echo "> Applying latest migrations..."
python web/manage.py migrate

# Cleanup
echo "> Cleaning up..."
rm -r /tmp/backups

echo "> DONE"
