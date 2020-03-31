#!/bin/bash

# crontab to run on the server (dev and staging ONLY)
# 45 1 * * * docker cp carbure_app:/app/scripts/recovery/restore_db.sh /tmp/ && bash /tmp/restore_db.sh

set -x
DATE=$(date -d yesterday +"%Y/%m/%d")

# delete staging and dev database
echo "Deleting database from staging/dev"
docker cp carbure_app:/app/scripts/recovery/delete_db.sh carbure_mariadb:/tmp
docker exec carbure_mariadb bash /tmp/delete_db.sh

# download yesterday's database
echo "Download database backup"
docker exec carbure_app python3 /app/scripts/recovery/s3recovery.py -b carbure.database -d $DATE

# copy downloaded backup into database container
echo "Copy backup to database container"
docker cp carbure_app:/tmp/backup-$DATE.sql carbure_mariadb:/tmp/backup.sql

# load backup
echo "Loading database backup"
docker cp carbure_app:/app/scripts/recovery/load_backup.sh carbure_mariadb:/tmp
docker exec carbure_mariadb bash /tmp/load_backup.sh
