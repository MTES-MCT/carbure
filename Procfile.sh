#! /usr/bin/env bash

# collect backend static files
python web/manage.py collectstatic --noinput

# apply new migrations
python web/manage.py migrate --noinput

# fill database with static fixtures
python /app/web/fixtures/load_biocarburants.py
python /app/web/fixtures/load_countries.py
python /app/web/fixtures/load_matierespremieres.py
python /app/web/fixtures/load_sn_certificates.py

# run server with gunicorn
gunicorn --chdir ./web carbure.wsgi --log-file -
