import os
import django
from datetime import date

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from elec.repositories.meter_reading_repository import MeterReadingRepository
from core.models import CarbureNotification
from elec.services.meter_readings_application_quarter import (
    get_application_quarter,
)


def create_meter_readings_application_deadline_reminder() -> None:

    today = date.today()
    # get current quarter to declare
    current_year, current_quarter = get_application_quarter(today)

    # all elec entites who have meter readings application to submit
    entities = MeterReadingRepository.get_entities_without_application(current_quarter, current_year)

    notifications = []
    for entity in entities:
        notifications.append(
            CarbureNotification(
                dest=entity,
                type=CarbureNotification.METER_READINGS_APP_ENDING_SOON,
                datetime=today,
                send_by_email=True,
                meta={"year": current_year, "quarter": current_quarter},
            )
        )

    CarbureNotification.objects.bulk_create(notifications)


if __name__ == "__main__":
    create_meter_readings_application_deadline_reminder()
