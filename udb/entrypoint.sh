#!/bin/sh

# Prepare config based on env and start the server

# bind properties file with env vars
bash ./setup/domibus_properties.sh

# set the port of the server
bash ./setup/set_domibus_port.sh

# run the server
bash ./domibus/bin/catalina.sh run
