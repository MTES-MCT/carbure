#!/bin/sh
#Please change CATALINA_HOME to the right folder
export CATALINA_HOME=/app/domibus
JAVA_OPTS="$JAVA_OPTS -Xms128m -Xmx1024m -Ddomibus.config.location=$CATALINA_HOME/conf/domibus"
