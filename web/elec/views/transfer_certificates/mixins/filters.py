from rest_framework.request import Request

from core.filters import FiltersActionFactory
from core.models import Entity


def get_filters(request: Request):
    filters = {
        "month": "transfer_date__month",
        "operator": "client__name",
        "cpo": "supplier__name",
        "used_in_tiruert": "used_in_tiruert",
    }

    entity_type = request.entity.entity_type

    if entity_type == Entity.CPO:
        filters.pop("cpo")
        filters.pop("used_in_tiruert")

    if entity_type == Entity.OPERATOR:
        filters.pop("operator")

    return filters


FiltersActionMixin = FiltersActionFactory(get_filters)
