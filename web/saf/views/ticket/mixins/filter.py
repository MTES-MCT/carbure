from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response


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

        if not filter:
            raise Exception("No filter was specified")

        if filter in query_params:
            query_params.pop(filter)

        filterset = self.filterset_class(query_params, queryset=self.get_queryset())
        queryset = filterset.qs

        filters = {
            "supplier": "supplier__name",
            "period": "assignment_period",
            "feedstock": "feedstock__code",
            "consumption_type": "consumption_type",
            "client": "client__name",
            "country_of_origin": "country_of_origin__code_pays",
            "production_site": "carbure_production_site__name",
        }

        column = filters.get(filter)
        if not column:
            raise Exception(f"Filter '{filter}' does not exist for tickets")

        values = queryset.values_list(column, flat=True).distinct()
        return Response({v for v in values if v is not None})
