#!/bin/bash


mysql -u $MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE < /tmp/backup.sql
