import os
import django
from datetime import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import CarbureNotification, Entity


def create_declaration_reminder() -> None:
    notifications = []

    today = datetime.today()
    period = today.year * 100 + today.month

    entities = Entity.objects.filter(
        entity_type__in=[Entity.OPERATOR, Entity.PRODUCER, Entity.TRADER, Entity.POWER_OR_HEAT_PRODUCER]
    ).prefetch_related("sustainabilitydeclaration_set")

    for entity in entities:
        declarations = entity.sustainabilitydeclaration_set.filter(period__year=today.year, period__month=today.month)

        # no declaration found for the current period, or not declared yet
        if declarations.count() == 0 or not declarations[0].declared:
            notifications.append(
                CarbureNotification(
                    dest=entity,
                    type=CarbureNotification.DECLARATION_REMINDER,
                    datetime=today,
                    send_by_email=True,
                    meta={"year": today.year, "period": period},
                )
            )

    CarbureNotification.objects.bulk_create(notifications)


if __name__ == "__main__":
    create_declaration_reminder()
