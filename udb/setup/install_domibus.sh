#!/bin/bash

# Download domibus binary and extensions to have all the files ready before we can launch anything.

# Download and install the Domibus binary and dependencies

DOMIBUS_FULL_FILE="domibus-msh-distribution-5.1.1-tomcat-full.zip"
DOMIBUS_FULL_URL="https://ec.europa.eu/digital-building-blocks/artifact/repository/eDelivery/eu/domibus/domibus-msh-distribution/5.1.1/$DOMIBUS_FULL_FILE"

mkdir -p downloads

if ! test -f ./downloads/$DOMIBUS_FULL_FILE; then
  wget -P ./downloads $DOMIBUS_FULL_URL
fi

unzip -d . ./downloads/$DOMIBUS_FULL_FILE

# Download and install the MySQL connector to allow db connections

MYSQL_CONNECTOR_FILE="mysql-connector-j-8.0.32.zip"
MYSQL_CONNECTER_URL="https://dev.mysql.com/get/Downloads/Connector-J/$MYSQL_CONNECTOR_FILE"

if ! test -f ./downloads/$MYSQL_CONNECTOR_FILE; then
  wget -P ./downloads $MYSQL_CONNECTER_URL
fi

unzip -d /tmp ./downloads/$MYSQL_CONNECTOR_FILE
mv /tmp/mysql-connector-j-8.0.32/mysql-connector-j-8.0.32.jar ./domibus/lib

# Move the env setter script
cp ./setup/setenv.sh ./domibus/bin/

# Make the scripts executable
chmod +x ./domibus/bin/*.sh
