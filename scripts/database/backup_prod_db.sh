#!/bin/sh

if [ "$IMAGE_TAG" != "prod" ]
then
  echo "This script can only be run in production"
  exit 1
fi

# setup scalingo
install-scalingo-cli
scalingo login --api-token $SCALINGO_TOKEN

# download latest backup
mkdir -p /tmp/backups
scalingo --region osc-secnum-fr1 --app carbure-prod --addon $SCALINGO_MYSQL_UUID backups-download --output /tmp/backups

# upload backup to backblaze
echo "Uploading backup to backblaze..."
python3 /app/scripts/database/s3backblaze.py -f /tmp/backups/*.tar.gz

# cleanup
echo "Cleaning up..."
rm -r /tmp/backups

echo "OK"
