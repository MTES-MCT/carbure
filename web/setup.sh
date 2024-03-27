#! /usr/bin/env bash

# collect static files
python3 ./web/manage.py collectstatic --noinput

# apply new migrations
python3 ./web/manage.py migrate --noinput

# fill database with static fixtures
python3 ./web/fixtures/load_biocarburants.py
python3 ./web/fixtures/load_countries.py
python3 ./web/fixtures/load_matierespremieres.py
python3 ./web/fixtures/load_sn_certificates.py