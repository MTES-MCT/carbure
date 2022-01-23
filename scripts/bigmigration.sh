#!/bin/bash

python3 $CARBURE_HOME/scripts/cleanup_before_migrationv4.py
python3 $CARBURE_HOME/web/manage.py migrate
python3 $CARBURE_HOME/scripts/check_etbe.py
python3 $CARBURE_HOME/scripts/check_etbe.py
python3 $CARBURE_HOME/scripts/recalc_stocks.py
python3 $CARBURE_HOME/scripts/migration_v4.py
