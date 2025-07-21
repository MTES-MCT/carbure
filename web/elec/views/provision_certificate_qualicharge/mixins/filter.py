from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response


class FilterActionMixin:
    @extend_schema(
        operation_id="filter_provision_certificates_qualicharge",
        description="Retrieve content of a specific filter",
        filters=True,
        parameters=[
            OpenApiParameter(
                name="filter",
                type=str,
                enum=["year", "validated_by", "operating_unit", "station_id", "date_from", "entity_id"],
                location=OpenApiParameter.QUERY,
                description="Filter string to apply",
                required=True,
            ),
        ],
        examples=[
            OpenApiExample(
                "Example of filters response.",
                value=[
                    "AMENAGEUR 1",
                    "AMENAGEUR 2",
                    "AMENAGEUR 3",
                    "AMENAGEUR 4",
                    "AMENAGEUR 5",
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

        filterset = self.filterset_class(query_params, queryset=self.get_queryset(), request=request)
        queryset = filterset.qs

        filters = {
            "year": "year",
            "validated_by": "validated_by",
            "operating_unit": "operating_unit",
            "station_id": "station_id",
            "date_from": "date_from",
            "entity_id": "cpo__name",
        }

        column = filters.get(filter)
        if not column:
            raise Exception(f"Filter '{filter}' does not exist for operations")

        values = queryset.values_list(column, flat=True).distinct()
        results = []
        for v in values:
            results.append(v)
        data = set(results)

        return Response(list(data))
