#!/bin/bash

rm -rf ./domibus
mkdir ./domibus

wget -P ./domibus https://ec.europa.eu/digital-building-blocks/artifact/repository/eDelivery/eu/domibus/domibus-msh-distribution/5.1/domibus-msh-distribution-5.1-tomcat-full.zip
unzip -d ./domibus ./domibus/domibus-msh-distribution-5.1-tomcat-full.zip

MYSQL_OPTIONS="--host=$DOMIBUS_DATABASE_SERVERNAME --port=$DOMIBUS_DATABASE_PORT --user=$MYSQL_USER --password=$MYSQL_PASSWORD"

mysql $MYSQL_OPTIONS -e "drop schema if exists $DOMIBUS_DATABASE_SCHEMA; create schema $DOMIBUS_DATABASE_SCHEMA; alter database $DOMIBUS_DATABASE_SCHEMA charset=utf8mb4 collate=utf8mb4_bin;"
mysql $MYSQL_OPTIONS -e "drop user if exists $DOMIBUS_DATASOURCE_USER; create user $DOMIBUS_DATASOURCE_USER identified by '$DOMIBUS_DATASOURCE_PASSWORD'; grant all on $DOMIBUS_DATABASE_SCHEMA.* to $DOMIBUS_DATASOURCE_USER; grant xa_recover_admin on *.* to $DOMIBUS_DATASOURCE_USER;"

mysql $MYSQL_OPTIONS $DOMIBUS_DATABASE_SCHEMA < ./domibus/sql-scripts/mysql-5.1.ddl
mysql $MYSQL_OPTIONS $DOMIBUS_DATABASE_SCHEMA < ./domibus/sql-scripts/mysql-5.1-data.ddl

mysqldump $MYSQL_OPTIONS -databases $DOMIBUS_DATABASE_SCHEMA > ./domibus/dump.sql