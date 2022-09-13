web: sh web/entrypoint.sh
worker: python3 web/manage.py run_huey
clock: huey_consumer cron.schedule.huey --workers=2 --logfile=./huey-cron.log