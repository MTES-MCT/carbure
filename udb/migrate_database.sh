#!/bin/sh

shopt -s expand_aliases # allow aliases inside script
alias domibus-mysql="mysql --host=$DOMIBUS_DATABASE_SERVERNAME --port=$DOMIBUS_DATABASE_PORT --user=$MYSQL_USER --password=$MYSQL_PASSWORD"

domibus-mysql -e "drop schema if exists $DOMIBUS_DATABASE_SCHEMA; create schema $DOMIBUS_DATABASE_SCHEMA; alter database $DOMIBUS_DATABASE_SCHEMA charset=utf8mb4 collate=utf8mb4_bin;"
domibus-mysql -e "drop user if exists $DOMIBUS_DATASOURCE_USER; create user $DOMIBUS_DATASOURCE_USER identified by '$DOMIBUS_DATASOURCE_PASSWORD'; grant all on $DOMIBUS_DATABASE_SCHEMA.* to $DOMIBUS_DATASOURCE_USER; grant xa_recover_admin on *.* to $DOMIBUS_DATASOURCE_USER;"

# domibus-mysql $DOMIBUS_DATABASE_SCHEMA < /app/sql-scripts/mysql-5.0.4.ddl
# domibus-mysql $DOMIBUS_DATABASE_SCHEMA < /app/sql-scripts/mysql-5.0.4-data.ddl

domibus-mysql $DOMIBUS_DATABASE_SCHEMA < /app/sql-scripts/mysql-5.1.1.ddl
domibus-mysql $DOMIBUS_DATABASE_SCHEMA < /app/sql-scripts/mysql-5.1.1-data.ddl

