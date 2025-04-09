from django.db.models import Case, CharField, Value, When
from django.db.models.functions import Cast, Coalesce, Concat, ExtractMonth, ExtractYear
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response


class FilterActionMixin:
    @extend_schema(
        operation_id="filter_elec_operations",
        description="Retrieve content of a specific filter",
        filters=True,
        parameters=[
            OpenApiParameter(
                name="filter",
                type=str,
                enum=["status", "type", "from_to", "operation", "period"],
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
        entity_id = self.request.query_params.get("entity_id")

        if not filter:
            raise Exception("No filter was specified")

        if filter in query_params:
            query_params.pop(filter)

        filterset = self.filterset_class(query_params, queryset=self.get_queryset(), request=request)
        queryset = filterset.qs

        filters = {
            "status": "status",
            "operation": "operations",
            "from_to": "entities",
            "type": "types",
            "period": "created_at",
        }

        column = filters.get(filter)
        if not column:
            raise Exception(f"Filter '{filter}' does not exist for operations")

        queryset = queryset.annotate(
            entities=Coalesce(
                "credited_entity__name",
                "debited_entity__name",
            ),
            types=Case(
                When(type__in=["ACQUISITION", "ACQUISITION_FROM_CPO"], then=Value("CREDIT")),
                When(type__in=["CESSION", "TENEUR"], then=Value("DEBIT")),
                default=Value(None),
                output_field=CharField(),
            ),
            operations=Case(
                When(type="CESSION", credited_entity_id=entity_id, then=Value("ACQUISITION")),
                When(type="CESSION", then=Value("CESSION")),
                When(type="INCORPORATION", then=Value("INCORPORATION")),
                When(type="TENEUR", then=Value("TENEUR")),
                When(type="ACQUISITION_FROM_CPO", then=Value("ACQUISITION_FROM_CPO")),
                default=Value(None),
                output_field=CharField(),
            ),
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
