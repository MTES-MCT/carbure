import datetime
import subprocess
from os import environ as env

from django.core.management import call_command
from django.db.models.query import QuerySet
from huey import crontab
from huey.contrib.djhuey import db_periodic_task, db_task, periodic_task

from carbure.scripts.create_declaration_reminder import create_declaration_reminder
from carbure.scripts.send_notification_emails import send_notification_emails
from carbure.scripts.update_2bs_certificates import update_2bs_certificates
from carbure.scripts.update_iscc_certificates import update_iscc_certificates
from carbure.scripts.update_redcert_certificates import update_redcert_certificates
from elec.scripts.create_meter_readings_application_deadline_reminder import (
    create_meter_readings_application_deadline_reminder,
)
from elec.scripts.create_meter_readings_application_reminder import create_meter_readings_application_reminder
from ml.scripts.calc_ml_score import calc_ml_score
from ml.scripts.load_data import load_ml_data
from saf.models.saf_ticket_source import create_ticket_sources_from_lots
from tiruert.models.operation import create_tiruert_operations_from_lots
from transactions.sanity_checks.sanity_checks import bulk_sanity_checks, bulk_scoring


@db_task()
def background_bulk_sanity_checks(lots: QuerySet, prefetched_data: dict | None = None) -> None:
    bulk_sanity_checks(lots, prefetched_data)


@db_task()
def background_bulk_scoring(lots: QuerySet, prefetched_data: dict | None = None) -> None:
    bulk_scoring(lots, prefetched_data)


@db_task()
def background_create_ticket_sources_from_lots(lots: QuerySet) -> None:
    create_ticket_sources_from_lots(lots)


@db_task()
def background_create_tiruert_operations_from_lots(lots: QuerySet) -> None:
    create_tiruert_operations_from_lots(lots)


if env.get("IMAGE_TAG") == "prod":

    @periodic_task(crontab(hour=23, minute=45))
    def periodic_backup_prod_db() -> None:
        subprocess.run(["bash", "/app/scripts/database/backup_prod_db.sh"])

    @db_periodic_task(crontab(day_of_week=7, hour=3, minute=0))
    def periodic_update_2bs_certificates() -> None:
        update_2bs_certificates(email=True)

    @db_periodic_task(crontab(day_of_week=7, hour=4, minute=0))
    def periodic_update_iscc_certificates() -> None:
        update_iscc_certificates(email=True, latest=True)

    @db_periodic_task(crontab(day_of_week=7, hour=5, minute=0))
    def periodic_update_redcert_certificates() -> None:
        update_redcert_certificates(email=True)

    @db_periodic_task(crontab(day_of_week=7, hour=5, minute=10))
    def periodic_get_redcert_pdf_certificates() -> None:
        call_command("get_redcert_pdf", "--no-pdf")

    @db_periodic_task(crontab(hour="19,20,21,22,23", minute=30))
    def periodic_send_notification_emails() -> None:
        send_notification_emails()

    @db_periodic_task(crontab(day=23, hour=8, minute=0))
    def periodic_send_declaration_reminder() -> None:
        create_declaration_reminder()

    @db_periodic_task(crontab(day=14, hour=1, minute=30))
    def periodic_load_ml_data() -> None:
        load_ml_data()

    @db_periodic_task(crontab(day=15, hour=1, minute=30))
    def periodic_calculate_ml_scores() -> None:
        today = datetime.datetime.today()
        first = today.replace(day=1)
        last_month = first - datetime.timedelta(days=1)
        period = last_month.year * 100 + last_month.month
        calc_ml_score(period=period)

    @periodic_task(crontab(hour=6, minute=0))
    def restart_metabase_container() -> None:
        subprocess.run(["bash", "/app/scripts/scalingo/restart_metabase.sh"])

    # Elec
    @db_periodic_task(crontab(month="3,6,9,12", day=21, hour=8, minute=0))
    def periodic_send_meter_readings_application_reminder() -> None:
        create_meter_readings_application_reminder()

    @db_periodic_task(crontab(month="1,4,7,10", day=15, hour=8, minute=0))
    def periodic_send_meter_readings_application_deadline_reminder() -> None:
        create_meter_readings_application_deadline_reminder()

    # Read replica
    @periodic_task(crontab(hour=1, minute=45))
    def populate_read_replica() -> None:
        subprocess.run(["bash", "/app/scripts/database/restore_db.sh", "carbure-prod", env.get("READ_REPLICA_DATABASE_URL")])

    # Anonymization
    @periodic_task(crontab(day=1, hour=1, minute=0))
    def anonymize_inactive_users() -> None:
        call_command("anonymize_inactive_users")


if env.get("IMAGE_TAG") == "staging":

    @periodic_task(crontab(hour=0, minute=45))
    def restore_prod_db() -> None:
        subprocess.run(["bash", "/app/scripts/database/restore_db.sh"])
