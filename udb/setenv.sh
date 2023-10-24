#!/bin/sh
# script to setup env variables for domibus

export CATALINA_HOME=/app/domibus
JAVA_OPTS="$JAVA_OPTS -Xms128m -Xmx2048m -Ddomibus.config.location=$CATALINA_HOME/conf/domibus"
