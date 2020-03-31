#!/bin/bash


# delete current staging or dev database and create an empty one
mysql -u root -p$MYSQL_ROOT_PASSWORD $MYSQL_DATABASE <<EOF
DROP DATABASE $MYSQL_DATABASE;
CREATE DATABASE $MYSQL_DATABASE;
EOF

