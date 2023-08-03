#!/bin/sh

# bind properties file with env vars and move it to domibus
sh ./domibus_properties.sh
mv ./domibus.properties ./domibus/conf/domibus/domibus.properties

bash ./domibus/bin/catalina.sh run