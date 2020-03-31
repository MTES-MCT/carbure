#!/bin/bash

if [ "$ENV" = "dev" ] || [ "$ENV" = "staging" ]
then
    mysql -u $MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE < /tmp/backup.sql
else
    echo "This script can only run in dev or staging environments"
fi


