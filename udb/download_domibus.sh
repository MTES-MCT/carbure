#!/bin/sh
# Download domibus binary

# wget https://ec.europa.eu/digital-building-blocks/artifact/content/repositories/public/eu/domibus/domibus-distribution/5.0.4/domibus-distribution-5.0.4-tomcat-full.zip
# wget https://ec.europa.eu/digital-building-blocks/artifact/content/repositories/public/eu/domibus/domibus-distribution/5.0.4/domibus-distribution-5.0.4-sample-configuration-and-testing.zip
# wget https://dev.mysql.com/get/Downloads/Connector-J/mysql-connector-j-8.0.32.zip

# unzip -d . domibus-distribution-5.0.4-tomcat-full.zip
# unzip -d ./domibus domibus-distribution-5.0.4-sample-configuration-and-testing.zip
# unzip -d /tmp mysql-connector-j-8.0.32.zip

mkdir -p downloads
cd downloads

if ! test -f ./domibus-msh-distribution-5.1.1-tomcat-full.zip; then
  wget https://ec.europa.eu/digital-building-blocks/artifact/repository/eDelivery/eu/domibus/domibus-msh-distribution/5.1.1/domibus-msh-distribution-5.1.1-tomcat-full.zip
fi

if ! test -f ./domibus-msh-distribution-5.1.1-sql-scripts.zip; then
  wget https://ec.europa.eu/digital-building-blocks/artifact/repository/eDelivery/eu/domibus/domibus-msh-distribution/5.1.1/domibus-msh-distribution-5.1.1-sql-scripts.zip
fi

if ! test -f ./domibus-msh-distribution-5.1.1-sample-configuration-and-testing.zip; then
  wget https://ec.europa.eu/digital-building-blocks/artifact/repository/eDelivery/eu/domibus/domibus-msh-distribution/5.1.1/domibus-msh-distribution-5.1.1-sample-configuration-and-testing.zip
fi

if ! test -f mysql-connector-j-8.0.32.zip; then
  wget https://dev.mysql.com/get/Downloads/Connector-J/mysql-connector-j-8.0.32.zip
fi


unzip -d .. domibus-msh-distribution-5.1.1-tomcat-full.zip
unzip -d .. domibus-msh-distribution-5.1.1-sql-scripts.zip
unzip -d ../domibus domibus-msh-distribution-5.1.1-sample-configuration-and-testing.zip
unzip -d /tmp mysql-connector-j-8.0.32.zip

cd ..

mv /tmp/mysql-connector-j-8.0.32/mysql-connector-j-8.0.32.jar ./domibus/lib

chmod +x ./domibus/bin/*.sh