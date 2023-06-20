#!/bin/bash

shopt -s expand_aliases # allow aliases inside script
alias carbure-mysql="mysql --host=carbure-mariadb --port=3306 --user=root --password=$MYSQL_ROOT_PASSWORD"

carbure-mysql -e "drop schema if exists $MYSQL_DATABASE; create schema $MYSQL_DATABASE; alter database $MYSQL_DATABASE charset=utf8mb4 collate=utf8mb4_bin;"
carbure-mysql -e "drop user if exists $MYSQL_USER; create user $MYSQL_USER identified by 'edelivery'; grant all on $MYSQL_DATABASE.* to $MYSQL_USER; grant xa_recover_admin on *.* to $MYSQL_USER;"

carbure-mysql $MYSQL_DATABASE < /app/sql-scripts/mysql-5.0.4.ddl
carbure-mysql $MYSQL_DATABASE < /app/sql-scripts/mysql-5.0.4-data.ddl

