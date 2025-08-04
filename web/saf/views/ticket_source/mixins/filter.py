from django.db.models.functions import Coalesce
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
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

        if not filter:
            raise Exception("No filter was specified")

        if filter in query_params:
            query_params.pop(filter)

        filterset = self.filterset_class(query_params, queryset=self.get_queryset(), request=request)
        queryset = filterset.qs

        filters = {
            "client": "saf_tickets__client__name",
            "period": "delivery_period",
            "feedstock": "feedstock__code",
            "country_of_origin": "country_of_origin__code_pays",
            "production_site": "carbure_production_site__name",
            "delivery_site": "parent_lot__carbure_delivery_site__name",
        }

        if request.entity.entity_type in (Entity.ADMIN, Entity.EXTERNAL_ADMIN):
            filters.update(
                {
                    "supplier": "parent_supplier",
                    "added_by": "added_by__name",
                }
            )

        column = filters.get(filter)
        if not column:  # raise an error for unknown filters
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
