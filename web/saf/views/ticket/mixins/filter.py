from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import Entity


class FilterActionMixin:
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
    def filters(self, request, *args, **kwargs):
        query_params = request.GET.copy()

        filter = request.query_params.get("filter")
        entity_id = self.request.query_params.get("entity_id")

        if not filter:
            raise Exception("No filter was specified")

        if filter in query_params:
            query_params.pop(filter)

        filterset = self.filterset_class(query_params, queryset=self.get_queryset())
        queryset = filterset.qs

        filters = {
            "suppliers": "supplier__name",
            "periods": "assignment_period",
            "feedstocks": "feedstock__code",
        }
        entity = Entity.objects.get(id=entity_id)
        if entity.entity_type != Entity.AIRLINE:
            filters.update(
                {
                    "clients": "client__name",
                    "countries_of_origin": "country_of_origin__code_pays",
                    "production_sites": "carbure_production_site__name",
                }
            )

        column = filters.get(filter)
        if not column:
            raise Exception(f"Filter '{filter}' does not exist for tickets")

        values = queryset.values_list(column, flat=True).distinct()
        results = [v for v in values if v]
        data = set(results)
        return Response(list(data))
