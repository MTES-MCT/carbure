#!/bin/bash
envsubst '$$DJANGO_DATABASE $$METABASE_RO_USER $$METABASE_RO_PWD' < $CARBURE_HOME/scripts/db_metabase_ro_user.tpl > $CARBURE_HOME/scripts/db_metabase_ro_user.sql

