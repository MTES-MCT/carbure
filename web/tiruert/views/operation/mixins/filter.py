from django.db.models import Case, CharField, Value, When
from django.db.models.functions import Cast, Coalesce, Concat, ExtractMonth, ExtractYear
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response

from saf.models.constants import SAF_BIOFUEL_TYPES
from tiruert.models.operation import Operation


class FilterActionMixin:
    @extend_schema(
        operation_id="filter_operations",
        description="Retrieve content of a specific filter",
        filters=True,
        parameters=[
            OpenApiParameter(
                name="filter",
                type=str,
                enum=["status", "sector", "customs_category", "biofuel", "type", "from_to", "depot", "operation", "period"],
                location=OpenApiParameter.QUERY,
                description="Filter string to apply",
                required=True,
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

        filterset = self.filterset_class(query_params, queryset=self.get_queryset(), request=request)
        queryset = filterset.qs

        filters = {
            "status": "status",
            "sector": "_sector",
            "customs_category": "customs_category",
            "biofuel": "biofuel__code",
            "operation": "_type",
            "from_to": "_entity",
            "depot": "_depot",
            "type": "_transaction",
            "period": "created_at",
        }

        column = filters.get(filter)
        if not column:
            raise Exception(f"Filter '{filter}' does not exist for operations")

        queryset = queryset.annotate(
            periods=Concat(
                ExtractYear("created_at", output_field=CharField()),
                Case(
                    When(
                        created_at__month__lt=10,
                        then=Concat(Value("0"), Cast("created_at__month", output_field=CharField())),
                    ),
                    default=ExtractMonth("created_at", output_field=CharField()),
                    output_field=CharField(),
                ),
            ),
        )

        values = queryset.values_list(column, flat=True).distinct()
        results = []
        for v in values:
            if v and column == "created_at":
                year = v.year
                month = v.month
                period = f"{year}{month:02d}"
                results.append(period)
            elif v:
                results.append(v)
        data = set(results)

        return Response(list(data))

    @extend_schema(
        operation_id="filter_balances",
        description="Retrieve content of a specific filter",
        filters=True,
        parameters=[
            OpenApiParameter(
                name="filter",
                type=str,
                enum=["sector", "customs_category", "biofuel"],
                location=OpenApiParameter.QUERY,
                description="Filter string to apply",
                required=True,
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
    @action(methods=["get"], detail=False, url_path="balance/filters")
    def filters_balance(self, request, *args, **kwargs):
        query_params = request.GET.copy()
        filter = request.query_params.get("filter")

        if not filter:
            raise Exception("No filter was specified")

        if filter in query_params:
            query_params.pop(filter)

        filterset = self.filterset_class(query_params, queryset=self.get_queryset(), request=request)
        queryset = filterset.qs

        filters = {
            "sector": "sector",
            "customs_category": "customs_category",
            "biofuel": "biofuel__code",
            "depot": "depots",
        }

        column = filters.get(filter)
        if not column:
            raise Exception(f"Filter '{filter}' does not exist for balances")

        queryset = queryset.annotate(
            sector=Case(
                When(biofuel__compatible_essence=True, then=Value(Operation.ESSENCE)),
                When(biofuel__compatible_diesel=True, then=Value(Operation.GAZOLE)),
                When(biofuel__code__in=SAF_BIOFUEL_TYPES, then=Value(Operation.CARBUREACTEUR)),
                default=Value(None),
                output_field=CharField(),
            ),
            depots=Coalesce(
                "from_depot__name",
                "to_depot__name",
            ),
        )
        values = queryset.values_list(column, flat=True).distinct()
        results = [v for v in values if v]
        data = set(results)
        return Response(list(data))
