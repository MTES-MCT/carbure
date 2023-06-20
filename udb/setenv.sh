#!/bin/sh
#Please change CATALINA_HOME to the right folder
export CATALINA_HOME=/app/domibus
JAVA_OPTS="$JAVA_OPTS -Xms4096m -Xmx4096m -Ddomibus.config.location=$CATALINA_HOME/conf/domibus"
