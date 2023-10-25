#!/bin/sh
# Download domibus binary and run config

# download and decompress domibus
sh ./download_domibus.sh

# bind properties file with env vars and move it to domibus
sh ./domibus_properties.sh
mv ./domibus.properties ./domibus/conf/domibus/domibus.properties

# set the port of the server
sed -i 's/port="8080"/port="80"/' ./domibus/conf/server.xml

# add the setenv.sh file
mv setenv.sh ./domibus/bin/setenv.sh

bash ./domibus/bin/catalina.sh run