web: sh web/entrypoint.sh
worker: huey_consumer web.carbure.settings.huey --workers=2 --logfile=./huey-carbure.log
clock: huey_consumer cron.schedule.huey --workers=2 --logfile=./huey-cron.log