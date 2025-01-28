from django.db.models import Case, CharField, Value, When
from django.db.models.functions import Coalesce
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
                name="entity_id",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Authorised entity ID.",
                required=True,
            ),
            OpenApiParameter(
                name="filter",
                type=str,
                enum=["status", "sector", "customs_category", "biofuel", "type", "from_to", "depot"],
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
        elif filter == "type":
            column = "type"
        elif filter == "from_to":
            column = "entities"
        elif filter == "depot":
            column = "depots"
        else:  # raise an error for unknown filters
            raise ValidationError({"message": "Filter '%s' does not exist for ticket sources" % filter})

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
        )
        values = queryset.values_list(column, flat=True).distinct()
        results = [v for v in values if v]
        data = set(results)
        return Response(list(data))
