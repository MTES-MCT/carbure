from rest_framework.request import Request

from core.filters import FiltersActionFactory
from core.models import Entity

CPO_FILTERS = {
    "status": "status",
    "operator": "client__name",
}

ADMIN_FILTERS = {
    **CPO_FILTERS,
    "cpo": "supplier__name",
}


def get_filters(request: Request):
    if request.entity.entity_type in (Entity.ADMIN, Entity.EXTERNAL_ADMIN):
        return ADMIN_FILTERS
    else:
        return CPO_FILTERS


FiltersActionMixin = FiltersActionFactory(get_filters)
