#! /usr/bin/env bash

# setup static files and database
bash ./bin/post_deploy.sh

# start dev server and huey consumer
python3 ./web/manage.py run_huey --simple --scheduler-interval 10 &
python3 ./web/manage.py runserver 0.0.0.0:8000
