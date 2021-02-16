#!/bin/bash

if [ "$IMAGE_TAG" = "local" ]
then
    # dump database
    ssh tortilla "docker exec carbure_mariadb mysqldump -u root -p"rootpassword" yourdbname --result-file=/tmp/carbure_dev_db.sql && docker cp carbure_mariadb:/tmp/carbure_dev_db.sql /tmp/carbure_dev_db.sql"
    echo "DEV Database dump successful, waiting 30 seconds for TOTP reset before download"
    sleep 30
    # download db
    scp tortilla:/tmp/carbure_dev_db.sql /tmp
    # load it   
    mysql -u $DJANGO_DB_USER -p$DJANGO_DB_PASSWORD $DJANGO_DATABASE --host $DJANGO_DB_HOST < /tmp/carbure_dev_db.sql
else
    echo "This script can only run locally"
fi
