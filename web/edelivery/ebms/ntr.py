import re

from core.models import Entity


def from_national_trade_register(ntr):
    country_code, _code_scheme, _code_scheme_end_mark, registration_id = (
        re.compile(r"([A-Z]{2})_([A-Z_]+)_(CD|MBN)(.+)").search(ntr).groups()
    )
    return Entity.objects.filter(registered_country__code_pays=country_code, registration_id=registration_id).last()
