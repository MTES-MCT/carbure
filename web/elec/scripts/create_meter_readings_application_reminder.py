import os
import django
from datetime import date

from elec.helpers.meter_readings_application_quarter import get_application_quarter

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import CarbureNotification, Entity
import calendar


def create_meter_readings_application_reminder() -> None:
    notifications = []

    today = date.today()
    # get current quarter to
    current_quarter = get_application_quarter(today)
    print("current_quarter: ", current_quarter)
    # all elec entites who have meter readings application to submit
    entities = Entity.objects.filter(entity_type__in=[Entity.CPO])
    print("entities: ", entities)

    # for entity in entities:
    #     declarations = entity.sustainabilitydeclaration_set.filter(period__year=today.year, period__month=today.month)

    #     # no declaration found for the current period, or not declared yet
    #     if declarations.count() == 0 or not declarations[0].declared:
    #         notifications.append(
    #             CarbureNotification(
    #                 dest=entity,
    #                 type=CarbureNotification.METER_READINGS_APPLICATION_STARTED,
    #                 datetime=today,
    #                 send_by_email=True,
    #                 meta={"year": today.year, "period": period},
    #             )
    #         )

    # CarbureNotification.objects.bulk_create(notifications)


if __name__ == "__main__":
    create_meter_readings_application_reminder()
