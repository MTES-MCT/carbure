#!/bin/sh
# script to setup env variables for domibus

# This script is supposed to be copied directly inside the domibus/bin directory.
# It should follow the template provided by Domibus (at domibus/bin/setenv.sh)

export CATALINA_HOME=$DOMIBUS_PATH
JAVA_OPTS="$JAVA_OPTS -Xms128m -Xmx1024m -Ddomibus.config.location=$CATALINA_HOME/conf/domibus"
