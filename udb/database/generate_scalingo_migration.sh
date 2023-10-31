#!/bin/bash

# Run this script from inside the Domibus docker container.
# Download Domibus SQL scripts, apply them to the local dev database and generate a dump compatible with Scalingo.

bash ./database/domibus_migration.sh

MYSQL_OPTIONS="--host=$DOMIBUS_DATABASE_SERVERNAME --port=$DOMIBUS_DATABASE_PORT --user=$MYSQL_USER --password=$MYSQL_PASSWORD"
mysqldump $MYSQL_OPTIONS --databases $DOMIBUS_DATABASE_SCHEMA > ./database/scalingo-migration.sql
