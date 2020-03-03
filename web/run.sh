#!/bin/bash


# database model migration
python3 /app/web/manage.py migrate --noinput

# 'static' fixtures (countries, filiere de production, types de biocarburants...)
python3 /app/web/manage.py loaddata /app/web/fixtures/countries.json
python3 /app/web/manage.py loaddata /app/web/fixtures/biocarburants.json
python3 /app/web/manage.py loaddata /app/web/fixtures/matierespremieres.json

# test data: only load in dev environment
if [ "$IMAGE_TAG" = "dev" ] ;
then
    python3 /app/web/manage.py loaddata /app/web/fixtures/authtools_user.json
    python3 /app/web/manage.py loaddata /app/web/fixtures/entities.json
    python3 /app/web/manage.py loaddata /app/web/fixtures/userrights.json
    python3 /app/web/manage.py loaddata /app/web/fixtures/userpreferences.json
fi

uwsgi --ini /app/web/carbure_uwsgi.ini --touch-reload=/app/web/carbure_uwsgi.ini
