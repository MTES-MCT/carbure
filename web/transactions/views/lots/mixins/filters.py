from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from transactions.views.utils import get_lots_filters_data


class FiltesrMixin:
    @action(methods=["get"], detail=False)
    def filters(self, request, *args, **kwargs):
        field = self.request.query_params.get("field", False)
        if not field:
            raise ValidationError({"message": "Please specify the field for which you want the filters"})

        lots = self.filter_queryset(self.get_queryset())
        data = get_lots_filters_data(lots, field)

        if data is None:
            raise ValidationError({"message": "Could not find specified filter"})

        return Response(data)
