import datetime
import re
from api.v4.helpers import get_prefetched_data
from core.models import CarbureLot, CarbureLotReliabilityScore, GenericError

from django.db import transaction
from core.common import find_normalized
from transactions.sanity_checks.sanity_checks import bulk_sanity_checks, sanity_checks

# definitions

oct2015 = datetime.date(year=2015, month=10, day=5)
jan2021 = datetime.date(year=2021, month=1, day=1)
july1st2021 = datetime.date(year=2021, month=7, day=1)
dae_pattern = re.compile("^([a-zA-Z0-9/]+$)")


def bulk_scoring(lots, prefetched_data=None):
    if not prefetched_data:
        prefetched_data = get_prefetched_data()
    # delete scoring entries for the lots
    lotids = [l.id for l in lots]
    CarbureLotReliabilityScore.objects.filter(lot_id__in=lotids).delete()
    # recalc score
    clrs = []
    # bulk update lots
    with transaction.atomic():
        for l in lots:
            clrs_entries = l.recalc_reliability_score(prefetched_data)
            clrs += clrs_entries
        CarbureLot.objects.bulk_update(lots, ["data_reliability_score"])
        CarbureLotReliabilityScore.objects.bulk_create(clrs)
