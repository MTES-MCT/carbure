#! /usr/bin/env bash

# setup static files and database
python3 ./web/manage.py collectstatic --noinput
bash ./bin/post_deploy.sh

# start dev server and huey consumer
python3 web/manage.py run_huey --simple &
gunicorn --bind 0.0.0.0:80 --workers 2 --chdir ./web carbure.wsgi -
