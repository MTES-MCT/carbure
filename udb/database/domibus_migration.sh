#!/bin/bash

# Run the migration scripts provided by Domibus.
# This should be the normal way to initialize the database, though it does not work with Scalingo for now.

# Download SQL scripts from Domibus CDN

DOMIBUS_SQL_SCRIPTS_FILE=domibus-msh-distribution-5.1.1-sql-scripts.zip
DOMIBUS_SQL_SCRIPTS_URL="https://ec.europa.eu/digital-building-blocks/artifact/repository/eDelivery/eu/domibus/domibus-msh-distribution/5.1.1/$DOMIBUS_SQL_SCRIPTS_FILE"

mkdir -p downloads

if ! test -f ./downloads/$DOMIBUS_SQL_SCRIPTS_FILE; then
  wget -P ./downloads $DOMIBUS_SQL_SCRIPTS_URL
fi

unzip -d . ./downloads/$DOMIBUS_SQL_SCRIPTS_FILE

# Run the scripts on the current database

MYSQL_OPTIONS="--host=$DOMIBUS_DATABASE_SERVERNAME --port=$DOMIBUS_DATABASE_PORT --user=$MYSQL_USER --password=$MYSQL_PASSWORD"

mysql $MYSQL_OPTIONS -e "drop schema if exists $DOMIBUS_DATABASE_SCHEMA; create schema $DOMIBUS_DATABASE_SCHEMA; alter database $DOMIBUS_DATABASE_SCHEMA charset=utf8mb4 collate=utf8mb4_bin;"
mysql $MYSQL_OPTIONS -e "drop user if exists $DOMIBUS_DATASOURCE_USER; create user $DOMIBUS_DATASOURCE_USER identified by '$DOMIBUS_DATASOURCE_PASSWORD'; grant all on $DOMIBUS_DATABASE_SCHEMA.* to $DOMIBUS_DATASOURCE_USER; grant xa_recover_admin on *.* to $DOMIBUS_DATASOURCE_USER;"

mysql $MYSQL_OPTIONS $DOMIBUS_DATABASE_SCHEMA < ./sql-scripts/mysql-5.1.1.ddl
mysql $MYSQL_OPTIONS $DOMIBUS_DATABASE_SCHEMA < ./sql-scripts/mysql-5.1.1-data.ddl
