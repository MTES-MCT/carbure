from django.db.models import Case, CharField, Value, When
from django.db.models.functions import Cast, Coalesce, Concat
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from saf.models.constants import SAF_BIOFUEL_TYPES


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
        queryset = self.filter_queryset(self.get_queryset())

        filter = self.request.query_params.get("filter")

        if not filter:
            raise ValidationError({"message": "No filter was specified"})

        if filter == "status":
            column = "status"
        elif filter == "sector":
            column = "sector"
        elif filter == "customs_category":
            column = "customs_category"
        elif filter == "biofuel":
            column = "biofuel__code"
        elif filter == "operation":
            column = "operations"
        elif filter == "from_to":
            column = "entities"
        elif filter == "depot":
            column = "depots"
        elif filter == "type":
            column = "types"
        elif filter == "period":
            column = "periods"
        else:  # raise an error for unknown filters
            raise ValidationError({"message": "Filter '%s' does not exist for ticket sources" % filter})

        entity_id = self.request.query_params.get("entity_id")

        queryset = queryset.annotate(
            entities=Coalesce(
                "credited_entity__name",
                "debited_entity__name",
            ),
            depots=Coalesce(
                "from_depot__name",
                "to_depot__name",
            ),
            sector=Case(
                When(biofuel__compatible_essence=True, then=Value("ESSENCE")),
                When(biofuel__compatible_diesel=True, then=Value("DIESEL")),
                When(biofuel__code__in=SAF_BIOFUEL_TYPES, then=Value("SAF")),
                default=Value(None),
                output_field=CharField(),
            ),
            types=Case(
                When(type__in=["INCORPORATION", "MAC_BIO", "LIVRAISON_DIRECTE", "ACQUISITION"], then=Value("CREDIT")),
                When(type__in=["CESSION", "TENEUR", "EXPORTATION", "DEVALUATION"], then=Value("DEBIT")),
                default=Value(None),
                output_field=CharField(),
            ),
            operations=Case(
                When(type="CESSION", credited_entity_id=entity_id, then=Value("ACQUISITION")),
                When(type="CESSION", then=Value("CESSION")),
                When(type="INCORPORATION", then=Value("INCORPORATION")),
                When(type="TENEUR", then=Value("TENEUR")),
                When(type="LIVRAISON_DIRECTE", then=Value("LIVRAISON_DIRECTE")),
                When(type="MAC_BIO", then=Value("MAC_BIO")),
                When(type="EXPORTATION", then=Value("EXPORTATION")),
                When(type="DEVALUATION", then=Value("DEVALUATION")),
                default=Value(None),
                output_field=CharField(),
            ),
            periods=Concat(
                Cast("created_at__year", output_field=CharField()),
                Case(
                    When(
                        created_at__month__lt=10,
                        then=Concat(Value("0"), Cast("created_at__month", output_field=CharField())),
                    ),
                    default=Cast("created_at__month", output_field=CharField()),
                    output_field=CharField(),
                ),
            ),
        )
        values = queryset.values_list(column, flat=True).distinct()
        results = [v for v in values if v]
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
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(status="ACCEPTED")

        filter = self.request.query_params.get("filter")

        if not filter:
            raise ValidationError({"message": "No filter was specified"})

        if filter == "sector":
            column = "sector"
        elif filter == "customs_category":
            column = "customs_category"
        elif filter == "biofuel":
            column = "biofuel__code"
        else:  # raise an error for unknown filters
            raise ValidationError({"message": "Filter '%s' does not exist for ticket sources" % filter})

        queryset = queryset.annotate(
            sector=Case(
                When(biofuel__compatible_essence=True, then=Value("ESSENCE")),
                When(biofuel__compatible_diesel=True, then=Value("DIESEL")),
                When(biofuel__code__in=SAF_BIOFUEL_TYPES, then=Value("SAF")),
                default=Value(None),
                output_field=CharField(),
            ),
        )
        values = queryset.values_list(column, flat=True).distinct()
        results = [v for v in values if v]
        data = set(results)
        return Response(list(data))
