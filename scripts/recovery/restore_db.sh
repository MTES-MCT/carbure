#!/bin/bash

# crontab to run on the server (dev and staging ONLY)
# 45 1 * * * docker cp carbure_app:/app/scripts/recovery/restore_db.sh /tmp/ && bash /tmp/restore_db.sh

set -x
if [ -z "$1" ]
  then
      DATE=$(date -d yesterday +"%Y/%m/%d")
else
    DATE=$1
fi

echo "Loading $DATE database backup"

# delete staging and dev database
echo "Deleting database from staging/dev"
docker cp carbure_app:/app/scripts/recovery/delete_db.sh /tmp
docker cp /tmp/delete_db.sh carbure_mariadb:/tmp
docker exec carbure_mariadb bash /tmp/delete_db.sh

# download yesterday's database
echo "Download database backup"
docker exec carbure_app python3 /app/scripts/recovery/s3recovery.py -b carbure.database -d $DATE

# copy downloaded backup into database container
echo "Copy backup to database container"
docker cp carbure_app:/tmp/backup.sql /tmp
docker cp /tmp/backup.sql carbure_mariadb:/tmp/backup.sql

# load backup
echo "Loading database backup"
docker cp carbure_app:/app/scripts/recovery/load_backup.sh /tmp
docker cp /tmp/load_backup.sh carbure_mariadb:/tmp
docker exec carbure_mariadb bash /tmp/load_backup.sh

# cleanup
rm /tmp/backup.sql
docker exec carbure_app rm /tmp/backup.sql
