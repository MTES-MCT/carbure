#!/bin/bash


# database model migration
python3 /app/web/manage.py migrate --noinput

# 'static' fixtures (countries, filiere de production, types de biocarburants...)
python3 /app/web/manage.py loaddata /app/web/fixtures/countries.json
python3 /app/web/manage.py loaddata /app/web/fixtures/biocarburants.json
python3 /app/web/manage.py loaddata /app/web/fixtures/matierespremieres.json

uwsgi --ini /app/web/carbure_uwsgi.ini --touch-reload=/app/web/carbure_uwsgi.ini
