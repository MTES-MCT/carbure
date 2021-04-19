#!/bin/bash


# database model migration
python3 /app/web/manage.py migrate --noinput

# 'static' fixtures (countries, filiere de production, types de biocarburants...)
python3 /app/web/fixtures/load_biocarburants.py
python3 /app/web/fixtures/load_countries.py
python3 /app/web/fixtures/load_matierespremieres.py
python3 /app/web/fixtures/load_ghg_values.py
python3 /app/web/fixtures/load_sn_certificates.py

if [ "$IMAGE_TAG" = "local" ] ; then
    python3 /app/web/manage.py runserver 0.0.0.0:8001
else
    uwsgi --ini /app/web/carbure_uwsgi.ini --touch-reload=/app/web/carbure_uwsgi.ini
fi
