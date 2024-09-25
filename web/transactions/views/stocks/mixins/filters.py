from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from transactions.views.utils import get_stock_filters_data


class FiltesrMixin:
    @action(methods=["get"], detail=False)
    def filters(self, request, *args, **kwargs):
        field = self.request.query_params.get("field", False)
        if not field:
            raise ValidationError({"message": "Please specify the field for which you want the filters"})

        stocks = self.filter_queryset(self.get_queryset())
        # TODO: black list
        data = get_stock_filters_data(stocks, field)

        if data is None:
            raise ValidationError({"message": "Could not find specified filter"})

        return Response(data)
