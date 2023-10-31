#!/bin/bash

# Inject env variables inside the domibus.properties file

PROPERTIES_FILE=./domibus/conf/domibus/domibus.properties

inject_env() {
  local property_key="$1"
  local property_value="$2"
  sed -i -e "s/$property_key=.*/$property_key=$property_value/" $PROPERTIES_FILE
}

toggle_comment() {
  local starts_with="$1"
  sed -i -e "s/#$starts_with/$starts_with/" $PROPERTIES_FILE
}

# setup identification and security values
inject_env "domibus.security.keystore.location" "\${domibus.config.location}\/keystores\/${DOMIBUS_SECURITY_KEYSTORE}_keystore.jks"
inject_env "domibus.security.keystore.password" "$DOMIBUS_SECURITY_KEYSTORE_PASSWORD"
inject_env "domibus.security.key.private.alias" "$DOMIBUS_SECURITY_KEY_PRIVATE_ALIAS"
inject_env "domibus.security.key.private.password" "$DOMIBUS_SECURITY_KEY_PRIVATE_PASSWORD"
inject_env "domibus.security.truststore.location" "\${domibus.config.location}\/keystores\/${DOMIBUS_SECURITY_TRUSTSTORE}_truststore.jks"
inject_env "domibus.security.truststore.password" "$DOMIBUS_SECURITY_TRUSTSTORE_PASSWORD"
inject_env "domibus.database.serverName" "$DOMIBUS_DATABASE_SERVERNAME"
inject_env "domibus.database.port" "$DOMIBUS_DATABASE_PORT"
inject_env "domibus.database.schema" "$DOMIBUS_DATABASE_SCHEMA"
inject_env "domibus.datasource.user" "$DOMIBUS_DATASOURCE_USER"
inject_env "domibus.datasource.password" "$DOMIBUS_DATASOURCE_PASSWORD"

# enable MySQL access
toggle_comment "domibus.datasource.driverClassName=com.mysql"
toggle_comment "domibus.datasource.url=jdbc\:mysql"
toggle_comment "domibus.datasource.user"
toggle_comment "domibus.datasource.password"

# allow public key retrieval
sed -i -e "s/domibus.datasource.url=jdbc\:mysql.*/&\&allowPublicKeyRetrieval=true/" $PROPERTIES_FILE