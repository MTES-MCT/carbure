#!/bin/bash

# Set the port used by the Domibus server

sed -i "s/port=\"8080\"/port=\"$PORT\"/" ./domibus/conf/server.xml
