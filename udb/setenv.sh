#!/bin/sh
#Please change CATALINA_HOME to the right folder
export CATALINA_HOME=/app/domibus
JAVA_OPTS="$JAVA_OPTS -Ddomibus.config.location=$CATALINA_HOME/conf/domibus"
