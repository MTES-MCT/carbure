#!/usr/bin/env bash

set -x
if [ -z "$1" ]
  then
      DATE=$(date -d yesterday +"%Y/%m/%d")
else
    DATE=$1
fi

echo "Loading $DATE database backup"

echo "Download mysql tools"
dbclient-fetcher mysql 8

echo "Download database backup"
python3 /app/scripts/recovery/s3recovery.py -b carbure.database -d $DATE

echo "Decompress backup"
tar -xzf /tmp/backup.tgz -C /tmp
mv /tmp/tmp/backup*.sql /tmp/backup.sql

# echo "Reset current database"

echo "Restore database backup"
cat /tmp/backup.sql | python3 /app/web/manage.py dbshell