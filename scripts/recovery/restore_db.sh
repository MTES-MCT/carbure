#!/bin/bash

# check environment
if [ "$IMAGE_TAG" != "local" ] && [ "$IMAGE_TAG" != "staging" ]
then
  echo "This script can only be run in local or staging"
  exit 1
fi

# setup scalingo on staging
if [ "$IMAGE_TAG" == "staging" ]
then
  dbclient-fetcher mysql 8
  install-scalingo-cli && scalingo login --api-token $SCALINGO_TOKEN
fi

# clean up any previous local backup
rm -r /tmp/backups
mkdir -p /tmp/backups

# download latest backup
scalingo --app carbure-prod --addon $SCALINGO_MYSQL_UUID backups-download --output /tmp/backups

# decompress backup
echo "Decompressing backup..."
tar -xzf /tmp/backups/*.tar.gz -C /tmp/backups

# remove lines mentionning production database
echo "Cleaning SQL..."
grep -vE "(carbure_pro_)" /tmp/backups/*.sql > /tmp/backups/backup.sql

# extract DATABASE_URL parts
export MYSQL_DATABASE=$(echo $DATABASE_URL | cut -d'/' -f4)
export DB_DETAILS=$(echo $DATABASE_URL | cut -d'/' -f3)
export MYSQL_HOST=$(echo $DB_DETAILS | cut -d'@' -f2 | cut -d':' -f1)
export MYSQL_PORT=$(echo $DB_DETAILS | cut -d'@' -f2 | cut -d':' -f2)
export MYSQL_USER=$(echo $DB_DETAILS | cut -d'@' -f1 | cut -d':' -f1)
export MYSQL_PASSWORD=$(echo $DB_DETAILS | cut -d'@' -f1 | cut -d':' -f2)

alias mysql="mysql --user=$MYSQL_USER --password=$MYSQL_PASSWORD --host=$MYSQL_HOST --port=$MYSQL_PORT --protocol=tcp"

# Clean up old database
echo "Cleaning previous database '$MYSQL_DATABASE'..."
mysql -e "DROP DATABASE \`$MYSQL_DATABASE\`;"
mysql -e "CREATE DATABASE \`$MYSQL_DATABASE\`;"

# Restore the backup
echo "Restoring backup in database..."
mysql $MYSQL_DATABASE < /tmp/backups/backup.sql

# Cleanup
echo "Cleaning up..."
rm -r /tmp/backups

echo "OK"
