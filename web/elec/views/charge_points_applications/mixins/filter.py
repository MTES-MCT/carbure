from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response


class FilterActionMixin:
    @action(methods=["get"], detail=False)
    def filters(self, request, *args, **kwargs):
        query_params = request.GET.copy()
        filter = request.query_params.get("filter")
        if not filter:
            raise ValidationError({"message": "No filter was specified"})

        if filter in query_params:
            query_params.pop(filter)

        filterset = self.filterset_class(query_params, queryset=self.get_queryset())
        queryset = filterset.qs

        filters = {
            "cpo": "cpo__name",
        }

        column = filters.get(filter)

        if not column:
            raise ValidationError({"message": f"Filter '{filter}' does not exist for tickets"})

        values = queryset.values_list(column, flat=True).distinct()

        return Response([v for v in values if v], status=status.HTTP_200_OK)
