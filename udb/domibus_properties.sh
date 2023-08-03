#!/bin/sh
# Replace the env variables used inside the domibus.properties file

sed -i -e "s/\$DOMIBUS_SECURITY_KEYSTORE_PASSWORD/$DOMIBUS_SECURITY_KEYSTORE_PASSWORD/" domibus.properties
sed -i -e "s/\$DOMIBUS_SECURITY_KEY_PRIVATE_ALIAS/$DOMIBUS_SECURITY_KEY_PRIVATE_ALIAS/" domibus.properties
sed -i -e "s/\$DOMIBUS_SECURITY_KEY_PRIVATE_PASSWORD/$DOMIBUS_SECURITY_KEY_PRIVATE_PASSWORD/" domibus.properties
sed -i -e "s/\$DOMIBUS_SECURITY_TRUST_PASSWORD/$DOMIBUS_SECURITY_TRUST_PASSWORD/" domibus.properties
sed -i -e "s/\$DOMIBUS_DATABASE_SERVERNAME/$DOMIBUS_DATABASE_SERVERNAME/" domibus.properties
sed -i -e "s/\$DOMIBUS_DATABASE_PORT/$DOMIBUS_DATABASE_PORT/" domibus.properties
sed -i -e "s/\$DOMIBUS_DATABASE_SCHEMA/$DOMIBUS_DATABASE_SCHEMA/" domibus.properties
sed -i -e "s/\$DOMIBUS_DATASOURCE_USER/$DOMIBUS_DATASOURCE_USER/" domibus.properties
sed -i -e "s/\$DOMIBUS_DATASOURCE_PASSWORD/$DOMIBUS_DATASOURCE_PASSWORD/" domibus.properties
