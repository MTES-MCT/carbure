from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import status
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.response import Response

from core.carburetypes import CarbureError
from core.helpers import (
    get_known_certificates,
    get_lot_comments,
    get_lot_errors,
    get_lot_updates,
    get_transaction_distance,
)
from core.models import CarbureLot, CarbureStock, Entity
from core.serializers import (
    CarbureLotAdminSerializer,
    CarbureLotPublicSerializer,
    CarbureLotReliabilityScoreSerializer,
    CarbureStockPublicSerializer,
)
from core.traceability import LotNode
from transactions.serializers.power_heat_lot_serializer import (
    CarbureLotPowerOrHeatProducerAdminSerializer,
    CarbureLotPowerOrHeatProducerPublicSerializer,
)
from transactions.views.helpers import get_admin_lot_comments
from transactions.views.utils import get_lot_children, get_lot_parents


class RetrieveMixin(RetrieveModelMixin):
    @extend_schema(
        parameters=[
            OpenApiParameter(
                "entity_id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Entity ID",
                required=True,
            )
        ],
    )
    def retrieve(self, request, id=None):
        entity_id = self.request.query_params.get("entity_id")
        entity = get_object_or_404(Entity, id=entity_id)
        lot = self.get_object()
        if lot.carbure_client != entity and lot.carbure_supplier != entity and lot.added_by != entity:
            return Response(
                {"message": CarbureError.ENTITY_NOT_ALLOWED},
                status=status.HTTP_403_FORBIDDEN,
            )

        is_read_only, disabled_fields = LotNode(lot).get_disabled_fields(entity_id)
        data = {}
        if entity.entity_type == Entity.AUDITOR:
            data["lot"] = CarbureLotAdminSerializer(lot).data
        elif entity.entity_type == Entity.ADMIN:
            data["lot"] = CarbureLotPowerOrHeatProducerAdminSerializer(lot).data
        if entity.entity_type == Entity.POWER_OR_HEAT_PRODUCER:
            data["lot"] = CarbureLotPowerOrHeatProducerPublicSerializer(lot).data
        else:
            data["lot"] = CarbureLotPublicSerializer(lot).data

        if entity.entity_type in [Entity.AUDITOR, Entity.ADMIN]:
            data["parent_lot"] = CarbureLotAdminSerializer(lot.parent_lot).data if lot.parent_lot else None
            data["parent_stock"] = CarbureStockPublicSerializer(lot.parent_stock).data if lot.parent_stock else None
            data["children_lot"] = CarbureLotAdminSerializer(CarbureLot.objects.filter(parent_lot=lot), many=True).data
            data["children_stock"] = CarbureStockPublicSerializer(
                CarbureStock.objects.filter(parent_lot=lot), many=True
            ).data
            data["comments"] = get_lot_comments(lot)
        else:
            parents = get_lot_parents(lot, entity)
            children = get_lot_children(lot, entity)
            data.update(parents)
            data.update(children)
            data["updates"] = get_lot_updates(lot, entity)
            data["comments"] = get_lot_comments(lot, entity)

        if entity.entity_type == Entity.AUDITOR:
            data["updates"] = get_lot_updates(lot)
        elif entity.entity_type == Entity.ADMIN:
            data["updates"] = get_lot_updates(lot, entity)
            data["control_comments"] = get_admin_lot_comments(lot)
        else:
            data["updates"] = get_lot_updates(lot, entity)
            data["is_read_only"] = is_read_only
            data["disabled_fields"] = disabled_fields

        data["errors"] = get_lot_errors(lot, entity)
        data["distance"] = get_transaction_distance(lot)
        data["certificates"] = get_known_certificates(lot)

        data["score"] = CarbureLotReliabilityScoreSerializer(lot.carburelotreliabilityscore_set.all(), many=True).data

        return Response(data, status=status.HTTP_200_OK)
