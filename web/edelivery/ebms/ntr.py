import re

from core.models import Entity


def from_national_trade_register(ntr):
    registration_id = re.compile(r"FR_SIREN_CD(\d{9})").search(ntr).group(1)
    return Entity.objects.filter(registration_id=registration_id).last()
