wget https://ec.europa.eu/digital-building-blocks/artifact/content/repositories/public/eu/domibus/domibus-distribution/5.0.4/domibus-distribution-5.0.4-tomcat-full.zip
wget https://ec.europa.eu/digital-building-blocks/artifact/content/repositories/public/eu/domibus/domibus-distribution/5.0.4/domibus-distribution-5.0.4-sample-configuration-and-testing.zip
wget https://dev.mysql.com/get/Downloads/Connector-J/mysql-connector-j-8.0.32.zip

unzip -d . domibus-distribution-5.0.4-tomcat-full.zip
unzip -d ./domibus domibus-distribution-5.0.4-sample-configuration-and-testing.zip
unzip -d /tmp mysql-connector-j-8.0.32.zip

mv /tmp/mysql-connector-j-8.0.32/mysql-connector-j-8.0.32.jar ./domibus/lib

rm *.zip

chmod +x ./domibus/bin/*.sh

bash ./domibus/bin/catalina.sh run