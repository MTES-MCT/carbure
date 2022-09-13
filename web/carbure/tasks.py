import subprocess
import datetime
from huey import crontab
from huey.contrib.djhuey import periodic_task, db_periodic_task, db_task

from api.v4.sanity_checks import bulk_sanity_checks, bulk_scoring


@db_task()
def background_bulk_sanity_checks(lots, prefetched_data=None):
    bulk_sanity_checks(lots, prefetched_data)


@db_task()
def background_bulk_scoring(lots, prefetched_data=None):
    bulk_scoring(lots, prefetched_data)


@periodic_task(crontab(hour=23, minute=45))
def backup_prod_db() -> None:
    subprocess.run(["bash", "/app/scripts/backup/backup_prod_db.sh"])


@db_periodic_task(crontab(day_of_week="Sun", hour=4, minute=0))
def download_2bs_certificates() -> None:
    subprocess.run(["bash", "/app/cron/download_2bs_certificates.sh"])


@db_periodic_task(crontab(day_of_week="Sun", hour=5, minute=0))
def download_iscc_certificates() -> None:
    subprocess.run(["bash", "/app/cron/download_iscc_certificates.sh"])


# @db_periodic_task(crontab(day_of_week="Sun", hour=6, minute=0))
# def download_redcert_certificates() -> None:
#     subprocess.run(["bash", "/app/cron/download_redcert_certificates.sh"])


@db_periodic_task(crontab(hour="19,20,21,22,23", minute=30))
def send_notification_emails() -> None:
    subprocess.run(["python3", "/app/scripts/emails/send_notifications_v3.py"])


@db_periodic_task(crontab(day=23, hour=8, minute=0))
def send_declaration_reminder() -> None:
    subprocess.run(["python3", "/app/cron/declaration_reminder.py"])


@db_periodic_task(crontab(day=14, hour=1, minute=30))
def load_ml_data() -> None:
    subprocess.run(["python3", "/app/web/ml/scripts/load_data.py"])


@db_periodic_task(crontab(day=15, hour=1, minute=30))
def calculate_ml_scores() -> None:
    today = datetime.datetime.today()
    first = today.replace(day=1)
    last_month = first - datetime.timedelta(days=1)
    period = last_month.year * 100 + last_month.month
    subprocess.run(["python3", "/app/web/ml/scripts/calc_ml_score.py", "--period", str(period)])
