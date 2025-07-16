from django.db.models import F, Sum
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from core.models import Entity
from core.pagination import MetadataPageNumberPagination
from saf.filters import TicketSourceFilter
from saf.models import SafTicketSource
from saf.permissions import (
    HasSafAdminRights,
    HasSafOperatorRights,
    HasSafOperatorWriteRights,
    HasSafTraderRights,
    HasSafTraderWriteRights,
)
from saf.serializers import SafTicketSourcePreviewSerializer, SafTicketSourceSerializer

from .mixins import ActionMixin


class SafTicketSourcePagination(MetadataPageNumberPagination):
    aggregate_fields = {
        "total_available_volume": Sum(F("total_volume") - F("assigned_volume")),
    }


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
class SafTicketSourceViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet, ActionMixin):
    lookup_field = "id"
    queryset = SafTicketSource.objects.all()
    permission_classes = [HasSafOperatorRights | HasSafTraderRights | HasSafAdminRights]
    serializer_class = SafTicketSourceSerializer
    pagination_class = SafTicketSourcePagination
    filterset_class = TicketSourceFilter
    search_fields = [
        "carbure_id",
        "saf_tickets__client__name",
        "feedstock__name",
        "biofuel__name",
        "country_of_origin__name",
        "carbure_production_site__name",
        "unknown_production_site",
    ]

    def get_permissions(self):
        if self.action in ["grouped_assign", "assign"]:
            return [(HasSafOperatorWriteRights | HasSafTraderWriteRights)()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "list":
            return SafTicketSourcePreviewSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        queryset = super().get_queryset()

        entity = self.request.entity
        if entity.entity_type in (Entity.OPERATOR, Entity.SAF_TRADER):
            queryset = queryset.filter(added_by=entity)

        return queryset.prefetch_related("saf_tickets", "saf_tickets__client").select_related(
            "feedstock",
            "biofuel",
            "country_of_origin",
            "carbure_production_site",
        )
