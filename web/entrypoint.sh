#! /usr/bin/env bash

# collect frontend static files
python3 ./web/manage.py collectstatic --noinput

# apply new migrations
python3 ./web/manage.py migrate --noinput

# fill database with static fixtures
python3 ./web/fixtures/load_biocarburants.py
python3 ./web/fixtures/load_countries.py
python3 ./web/fixtures/load_matierespremieres.py
python3 ./web/fixtures/load_sn_certificates.py

if [ "$IMAGE_TAG" = "local" ] ; then
  # start dev server and huey consumer
  python3 ./web/manage.py run_huey &
  python3 ./web/manage.py runserver 0.0.0.0:8000 &
  wait
else
  # start prod server with gunicorn
  gunicorn --chdir ./web carbure.wsgi --log-file -
fi
