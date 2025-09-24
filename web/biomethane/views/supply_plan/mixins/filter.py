from rest_framework.request import Request

from core.filters import FiltersActionFactory


def get_filters(request: Request):
    filters = {
        "type": "input_type",
        "source": "source",
        "category": "input_category",
    }

    return filters


FiltersActionMixin = FiltersActionFactory(get_filters)
