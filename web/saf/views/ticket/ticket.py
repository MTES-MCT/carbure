from django.db.models import Q, Sum
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from core.models import Entity
from core.pagination import MetadataPageNumberPagination
from saf.filters import TicketFilter
from saf.models import SafTicket
from saf.permissions import (
    HasAirlineRights,
    HasAirlineWriteRights,
    HasSafAdminRights,
    HasSafOperatorRights,
    HasSafOperatorWriteRights,
    HasSafTraderRights,
    HasSafTraderWriteRights,
)
from saf.serializers import SafTicketPreviewSerializer, SafTicketSerializer

from .mixins import ActionMixin


class SafTicketPagination(MetadataPageNumberPagination):
    aggregate_fields = {
        "total_volume": Sum("volume"),
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
class SafTicketViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet, ActionMixin):
    lookup_field = "id"
    queryset = SafTicket.objects.all()
    permission_classes = [HasAirlineRights | HasSafOperatorRights | HasSafTraderRights | HasSafAdminRights]
    serializer_class = SafTicketSerializer
    filterset_class = TicketFilter
    pagination_class = SafTicketPagination
    search_fields = [
        "carbure_id",
        "supplier__name",
        "client__name",
        "feedstock__name",
        "biofuel__name",
        "country_of_origin__name",
        "agreement_reference",
        "carbure_production_site__name",
        "unknown_production_site",
    ]

    def get_permissions(self):
        if self.action == "accept":
            return [HasAirlineWriteRights()]
        if self.action == "reject":
            return [(HasAirlineWriteRights | HasSafOperatorWriteRights | HasSafTraderWriteRights)()]
        if self.action in ("cancel", "credit_source"):
            return [(HasSafOperatorWriteRights | HasSafTraderWriteRights)()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "list":
            return SafTicketPreviewSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        queryset = super().get_queryset()
        entity = self.request.entity

        if entity.entity_type == Entity.AIRLINE:
            queryset = queryset.filter(client=entity)

        if entity.entity_type in (Entity.SAF_TRADER, Entity.OPERATOR):
            queryset = queryset.filter(Q(client=entity) | Q(supplier=entity))

        return queryset.select_related(
            "parent_ticket_source",
            "feedstock",
            "biofuel",
            "country_of_origin",
            "carbure_production_site",
            "supplier",
            "client",
            "reception_airport",
        )

    @extend_schema(responses={200: SafTicketPreviewSerializer})
    def list(self, request):
        return super().list(request)
