import traceback

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
from core.carburetypes import CarbureSanityCheckErrors
from core.models import CarbureLot, Entity, GenericError
from transactions.models import Depot, EntitySite


class AddDepotSerializer(serializers.Serializer):
    delivery_site_id = serializers.CharField(required=True)
    ownership_type = serializers.ChoiceField(choices=EntitySite.TYPE_OWNERSHIP, required=True)
    blending_is_outsourced = serializers.BooleanField(default=False, required=False)
    blending_entity_id = serializers.CharField(required=False)


class AddDepotActionMixin:
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
        request=AddDepotSerializer,
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
    @action(detail=False, methods=["post"], url_path="add")
    def add(self, request):
        entity_id = self.request.query_params.get("entity_id")
        entity = Entity.objects.get(id=entity_id)
        serializer = AddDepotSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        delivery_site_id = serializer.validated_data.get("delivery_site_id")
        ownership_type = serializer.validated_data.get("ownership_type")
        blending_is_outsourced = serializer.validated_data.get("oblending_is_outsourced", False)
        blending_entity_id = serializer.validated_data.get("oblending_entity_id")
        try:
            ds = Depot.objects.get(customs_id=delivery_site_id)
        except Exception:
            return Response(
                {
                    "status": "error",
                    "message": "Could not find delivery site",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        blender = None
        if blending_is_outsourced:
            try:
                blender = Entity.objects.get(id=blending_entity_id, entity_type=Entity.OPERATOR)
            except Exception:
                return Response(
                    {
                        "status": "error",
                        "message": "Could not find outsourcing blender",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        try:
            EntitySite.objects.update_or_create(
                entity=entity,
                site=ds,
                defaults={
                    "ownership_type": ownership_type,
                    "blending_is_outsourced": blending_is_outsourced,
                    "blender": blender,
                },
            )
            lots = CarbureLot.objects.filter(carbure_client=entity, carbure_delivery_site=ds)
            background_bulk_scoring(lots)
            background_bulk_sanity_checks(lots)
            GenericError.objects.filter(lot__in=lots, error=CarbureSanityCheckErrors.DEPOT_NOT_CONFIGURED).delete()
        except Exception:
            traceback.print_exc()
            return Response(
                {
                    "status": "error",
                    "message": "Could not link entity to delivery site",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({"status": "success"})
