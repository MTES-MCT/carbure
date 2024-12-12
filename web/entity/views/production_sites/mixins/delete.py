from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
)
from rest_framework import status
from rest_framework.response import Response

from core.models import CarbureLot, Entity
from transactions.models import ProductionSite


class DeleteActionMixin:
    @extend_schema(
        parameters=[
            OpenApiParameter(
                "entity_id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Entity ID",
                required=True,
            ),
        ],
        responses={
            200: OpenApiResponse(
                response={"status": "success"},
                description="Request successful.",
            ),
            400: OpenApiResponse(
                response={"message": ""},
                description="Bad request.",
            ),
        },
        examples=[
            OpenApiExample(
                "Success example",
                value={"status": "success"},
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                "Bad request",
                value={"message": ""},
                response_only=True,
                status_codes=["400"],
            ),
        ],
    )
    def destroy(self, request, id=None):
        entity_id = self.request.query_params.get("entity_id")
        entity = Entity.objects.get(id=entity_id)

        try:
            ps = ProductionSite.objects.get(id=id, created_by=entity)
        except Exception as e:
            print(e)
            return Response(
                {"message": "Unknown Production Site"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        lots = CarbureLot.objects.filter(
            carbure_production_site=ps,
            lot_status__in=[CarbureLot.ACCEPTED, CarbureLot.FROZEN],
        )

        if lots.count() > 0:
            msg = "Validated lots associated with this production site. Cannot delete"
            return Response({"message": msg}, status=status.HTTP_400_BAD_REQUEST)
        ps.delete()
        return Response({"status": "success"})
