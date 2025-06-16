from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import Entity


class FiltersActionMixin:
    @extend_schema(
        filters=True,
        parameters=[
            OpenApiParameter(
                name="filter",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Filter string to apply",
            ),
        ],
        examples=[
            OpenApiExample(
                "Example of filters response.",
                value=[
                    "SHELL France",
                    "CIM SNC",
                    "ESSO SAF",
                    "TMF",
                    "TERF SAF",
                ],
                request_only=False,
                response_only=True,
            ),
        ],
        responses={
            200: {
                "type": "array",
                "items": {
                    "type": "string",
                },
            },
        },
    )
    @action(methods=["get"], detail=False)
    def filters(self, request):
        query_params = request.GET.copy()
        entity = request.entity

        filter = request.query_params.get("filter")

        if not filter:
            raise Exception("No filter was specified")

        if filter in query_params:
            query_params.pop(filter)

        filterset = self.filterset_class(query_params, queryset=self.get_queryset())
        queryset = filterset.qs

        filters = {
            "quarter": "quarter",
            "operating_unit": "operating_unit",
        }
        if entity.entity_type in (Entity.ADMIN, Entity.EXTERNAL_ADMIN):
            filters.update(
                {
                    "cpo": "cpo__name",
                }
            )

        column = filters.get(filter)
        if not column:
            raise Exception(f"Filter '{filter}' does not exist for tickets")

        values = queryset.values_list(column, flat=True).distinct()
        results = [v for v in values if v]
        data = set(results)
        return Response(list(data))
