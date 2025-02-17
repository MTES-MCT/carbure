from django.db.models import Q
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, PolymorphicProxySerializer, extend_schema
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from core.models import Entity, UserRights
from saf.filters import TicketFilter
from saf.models import SafTicket
from saf.permissions import HasUserRights
from saf.serializers import (
    SafTicketAirlineSerializer,
    SafTicketBaseSerializer,
    SafTicketDetailsAirlineSerializer,
    SafTicketDetailsBaseSerializer,
)

from .mixins import ActionMixin


class SafTicketViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet, ActionMixin):
    lookup_field = "id"
    permission_classes = (
        IsAuthenticated,
        HasUserRights(None, [Entity.OPERATOR, Entity.AIRLINE]),
    )
    serializer_class = SafTicketBaseSerializer
    filterset_class = TicketFilter
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
        if self.action in ["reject", "accept"]:
            return [HasUserRights([UserRights.ADMIN, UserRights.RW])]
        if self.action == "cancel":
            return [HasUserRights([UserRights.ADMIN, UserRights.RW], [Entity.OPERATOR])]
        return super().get_permissions()

    def get_serializer_class(self):
        entity_id = self.request.query_params.get("entity_id")
        entity = Entity.objects.filter(pk=entity_id).first()
        is_airline = entity and entity.entity_type == Entity.AIRLINE

        if self.action == "list":
            return SafTicketAirlineSerializer if is_airline else SafTicketBaseSerializer
        elif self.action == "retrieve":
            return SafTicketDetailsAirlineSerializer if is_airline else SafTicketDetailsBaseSerializer

        return super().get_serializer_class()

    def get_queryset(self):
        queryset = SafTicket.objects.none()
        if self.request and not self.request.user.is_anonymous:
            queryset = SafTicket.objects.select_related(
                "parent_ticket_source",
                "feedstock",
                "biofuel",
                "country_of_origin",
                "carbure_production_site",
                "supplier",
                "client",
            )
        return queryset

    @extend_schema(
        responses={
            200: PolymorphicProxySerializer(
                many=True,
                component_name="SafTicket",
                serializers=[SafTicketBaseSerializer, SafTicketAirlineSerializer],
                resource_type_field_name=None,
            )
        },
    )
    def list(self, request):
        return super().list(request)

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
        responses={
            200: PolymorphicProxySerializer(
                component_name="SafTicketDetails",
                serializers=[SafTicketDetailsBaseSerializer, SafTicketDetailsAirlineSerializer],
                resource_type_field_name=None,
            )
        },
    )
    def retrieve(self, request, id):
        entity_id = self.request.query_params.get("entity_id")
        entity = Entity.objects.get(id=entity_id)
        if entity.entity_type == Entity.AIRLINE:
            ticket = SafTicket.objects.select_related("parent_ticket_source").get(id=id, client_id=entity_id)
        else:
            ticket_filter = Q(id=id) & (Q(supplier_id=entity_id) | Q(client_id=entity_id))
            ticket = get_object_or_404(SafTicket.objects.select_related("parent_ticket_source"), ticket_filter)

            if ticket.supplier_id != int(entity_id):
                ticket.parent_ticket_source = None

        serializer = self.get_serializer(ticket)
        return Response(serializer.data)
