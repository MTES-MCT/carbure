import os

import django
from tqdm import tqdm

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import *  # noqa: E402


def freeze_old_declarations():
    declarations = SustainabilityDeclaration.objects.filter(period__lt="2022-01-01", declared=False)
    for declaration in tqdm(declarations):
        period_int = int(declaration.period.year * 100 + declaration.period.month)
        # ensure everything is in order
        pending_reception = CarbureLot.objects.filter(
            carbure_client=declaration.entity, period=period_int, lot_status=CarbureLot.PENDING
        ).count()
        if pending_reception > 0:
            continue  # skip
        pending_correction = CarbureLot.objects.filter(
            carbure_client=declaration.entity,
            period=period_int,
            lot_status__in=[CarbureLot.ACCEPTED],
            correction_status__in=[CarbureLot.IN_CORRECTION, CarbureLot.FIXED],
        ).count()
        if pending_correction > 0:
            continue  # skip
        lots_sent_rejected_or_drafts = CarbureLot.objects.filter(
            carbure_supplier=declaration.entity, period=period_int, lot_status=CarbureLot.REJECTED
        ).count()
        if lots_sent_rejected_or_drafts > 0:
            continue  # skip
        lots_sent_to_fix = CarbureLot.objects.filter(
            carbure_supplier=declaration.entity,
            period=period_int,
            lot_status__in=[CarbureLot.ACCEPTED],
            correction_status__in=[CarbureLot.IN_CORRECTION],
        ).count()
        if lots_sent_to_fix > 0:
            continue  # skip
        lots_received = CarbureLot.objects.filter(carbure_client=declaration.entity, period=period_int)
        lots_received.update(declared_by_client=True)
        lots_sent = CarbureLot.objects.filter(carbure_supplier=declaration.entity, period=period_int)
        lots_sent.update(declared_by_supplier=True)
        # freeze lots
        lots_to_freeze = CarbureLot.objects.filter(
            carbure_client=declaration.entity, period=period_int, declared_by_client=True, declared_by_supplier=True
        )
        lots_to_freeze.update(lot_status=CarbureLot.FROZEN)
        lots_to_freeze = CarbureLot.objects.filter(
            carbure_supplier=declaration.entity, period=period_int, declared_by_client=True, declared_by_supplier=True
        )
        lots_to_freeze.update(lot_status=CarbureLot.FROZEN)
        # mark declaration
        declaration.declared = True
        declaration.save()


if __name__ == "__main__":
    freeze_old_declarations()
