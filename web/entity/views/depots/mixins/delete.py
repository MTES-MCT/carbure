from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
)
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response

from carbure.tasks import background_bulk_sanity_checks, background_bulk_scoring
from core.models import CarbureLot, Entity
from transactions.models import EntitySite


class DeleteDepotSerializer(serializers.Serializer):
    delivery_site_id = serializers.CharField(required=True)


class DeleteDepotActionMixin:
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
        request=DeleteDepotSerializer,
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
    @action(detail=False, methods=["post"], url_path="delete-depot")
    def delete_depot(self, request):
        entity_id = self.request.query_params.get("entity_id")
        entity = Entity.objects.get(id=entity_id)
        serializer = DeleteDepotSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        delivery_site_id = serializer.validated_data.get("delivery_site_id")

        try:
            EntitySite.objects.filter(entity=entity, site__customs_id=delivery_site_id).delete()
            lots = CarbureLot.objects.filter(
                carbure_client=entity,
                carbure_delivery_site__customs_id=delivery_site_id,
            )
            background_bulk_scoring(lots)
            background_bulk_sanity_checks(lots)
        except Exception:
            return Response(
                {"message": "Could not delete entity's delivery site"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"status": "success"})
