#!/bin/bash

# Run the custom initial migration script from inside a Scalingo container.
# This script differs from the one provided by Domibus by merging CREATE TABLE commands with PRIMARY KEY specification.
# This is necessary because of Scalingo's MySQL rules that requires new tables to have a PK defined on creation.
# The scalingo_migration.sql file should be generated from a local dev machine, see README for instructions.

MYSQL_OPTIONS="--host=$DOMIBUS_DATABASE_SERVERNAME --port=$DOMIBUS_DATABASE_PORT --user=$MYSQL_USER --password=$MYSQL_PASSWORD"

mysql $MYSQL_OPTIONS -e "drop schema if exists $DOMIBUS_DATABASE_SCHEMA; create schema $DOMIBUS_DATABASE_SCHEMA; alter database $DOMIBUS_DATABASE_SCHEMA charset=utf8mb4 collate=utf8mb4_bin;"
mysql $MYSQL_OPTIONS $DOMIBUS_DATABASE_SCHEMA < ./database/scalingo_migration.sql
