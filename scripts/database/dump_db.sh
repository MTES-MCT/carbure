#!/bin/bash

# clean up any previous local backup
rm -rf /tmp/backups
mkdir -p /tmp/backups

# extract DATABASE_URL parts
export MYSQL_DATABASE=$(echo $DATABASE_URL | cut -d'/' -f4)
export DB_DETAILS=$(echo $DATABASE_URL | cut -d'/' -f3)
export MYSQL_HOST=$(echo $DB_DETAILS | cut -d'@' -f2 | cut -d':' -f1)
export MYSQL_PORT=$(echo $DB_DETAILS | cut -d'@' -f2 | cut -d':' -f2)
export MYSQL_USER=$(echo $DB_DETAILS | cut -d'@' -f1 | cut -d':' -f1)
export MYSQL_PASSWORD=$(echo $DB_DETAILS | cut -d'@' -f1 | cut -d':' -f2)

shopt -s expand_aliases # allow aliases inside script
alias carbure-mysqldump="mysqldump --user=$MYSQL_USER --password=$MYSQL_PASSWORD --host=$MYSQL_HOST --port=$MYSQL_PORT --protocol=tcp"

carbure-mysqldump $MYSQL_DATABASE > /tmp/backups/backup-$(date +\%F).sql

tar -czf /tmp/backups/backup-$(date +\%F).tar.gz -C /tmp/backups backup-$(date +\%F).sql

echo "OK"
