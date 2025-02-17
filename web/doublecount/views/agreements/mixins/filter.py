from datetime import datetime

from django.db.models.query_utils import Q
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
        status = request.query_params.get("status")
        year = self.request.query_params.get("year", datetime.now().year)

        if not filter:
            raise Exception("No filter was specified")

        if filter in query_params:
            query_params.pop(filter)

        filterset = self.filterset_class(query_params, queryset=self.get_queryset())
        queryset = filterset.qs
        if status == "active":
            queryset = queryset.filter(Q(valid_from__year__lte=year) & Q(valid_until__year__gte=year)).order_by(
                "production_site__name"
            )
        elif status == "expired":
            queryset = queryset.filter(Q(valid_until__year__lt=year))
        elif status == "incoming":
            queryset = queryset.filter(Q(valid_from__year__gt=year))

        filters = {
            "certificate_id": "certificate_id",
            "producers": "production_site__created_by__name",
            "production_sites": "production_site__name",
        }

        column = filters.get(filter)
        if not column:
            raise Exception(f"Filter '{filter}' does not exist for tickets")

        values = queryset.values_list(column, flat=True).distinct()
        results = [v for v in values if v]
        data = set(results)
        return Response(list(data))
