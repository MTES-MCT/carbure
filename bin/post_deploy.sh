#! /usr/bin/env bash

# apply new migrations
python3 ./web/manage.py migrate --noinput

# fill database with static fixtures
python3 ./web/fixtures/load_biocarburants.py
python3 ./web/fixtures/load_countries.py
python3 ./web/fixtures/load_matierespremieres.py
python3 ./web/fixtures/load_sn_certificates.py
python3 ./web/fixtures/load_airports.py
python3 ./web/fixtures/load_fossil_fuel_categories.py
python3 ./web/fixtures/load_fossil_fuels.py
python3 ./web/fixtures/load_departments.py
