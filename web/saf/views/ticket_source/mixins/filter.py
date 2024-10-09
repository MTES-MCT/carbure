from django.db.models.functions import Coalesce
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
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
        queryset = self.filter_queryset(self.get_queryset())

        filter = self.request.query_params.get("filter")

        if not filter:
            raise ValidationError({"message": "No filter was specified"})

        if filter == "clients":
            column = "saf_tickets__client__name"
        elif filter == "periods":
            column = "delivery_period"
        elif filter == "feedstocks":
            column = "feedstock__code"
        elif filter == "countries_of_origin":
            column = "country_of_origin__code_pays"
        elif filter == "production_sites":
            column = "carbure_production_site__name"
        elif filter == "delivery_sites":
            column = "parent_lot__carbure_delivery_site__name"
        elif filter == "suppliers":
            column = "parent_supplier"
        else:  # raise an error for unknown filters
            raise ValidationError({"message": "Filter '%s' does not exist for ticket sources" % filter})

        queryset = queryset.annotate(
            parent_supplier=Coalesce(
                "parent_lot__carbure_supplier__name",
                "parent_lot__unknown_supplier",
                "parent_ticket__supplier__name",
            )
        )
        values = queryset.values_list(column, flat=True).distinct()
        results = [v for v in values if v]
        data = set(results)
        return Response(list(data))
