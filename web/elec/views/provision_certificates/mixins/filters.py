from rest_framework.request import Request

from core.filters import FiltersActionFactory
from core.models import Entity


def get_filters(request: Request):
    filters = {
        "quarter": "quarter",
        "operating_unit": "operating_unit",
        "source": "source",
        "cpo": "cpo__name",
    }

    if request.entity.entity_type == Entity.CPO:
        filters.pop("cpo")

    return filters


FiltersActionMixin = FiltersActionFactory(get_filters)
