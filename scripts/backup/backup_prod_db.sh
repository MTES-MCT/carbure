#!/bin/sh

# dump db
mysqldump -h $DJANGO_DB_HOST -u $DJANGO_DB_USER -p"$DJANGO_DB_PASSWORD" $DJANGO_DATABASE > /tmp/backup-$(date +\%F).sql

# upload db
python /app/scripts/backup/s3backup.py -b carbure.database -f /tmp/backup-$(date +\%F).sql

# cleanup s3 bucket
python /app/scripts/backup/s3cleanup.py -b carbure.database

echo "OK"
