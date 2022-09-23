#!/bin/bash
envsubst '$$DJANGO_DATABASE $$DJANGO_DB_USER $$DJANGO_DB_PASSWORD' < $CARBURE_HOME/scripts/db_test_rw_user.tpl > $CARBURE_HOME/scripts/db_test_rw_user.sql

