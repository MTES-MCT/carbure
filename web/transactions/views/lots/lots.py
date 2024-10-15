from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from apikey.authentication import APIKeyAuthentication
from core.models import CarbureLot, Entity, UserRights
from core.serializers import CarbureLotAdminSerializer, CarbureLotPublicSerializer
from transactions.filters import LotsFilter
from transactions.permissions import HasUserRights

from .mixins import ActionMixin


class LotsViewSet(GenericViewSet, ActionMixin):
    lookup_field = "id"
    # TODO fix permissions if needed
    permission_classes = (
        IsAuthenticated,
        HasUserRights(
            [UserRights.ADMIN, UserRights.RW],
            [Entity.OPERATOR, Entity.PRODUCER, Entity.TRADER],
        ),
    )
    serializer_class = CarbureLotPublicSerializer
    filterset_class = LotsFilter
    ordering_fields = [
        "id",
        "volume",
        "biofuel",
        "client",
        "supplier",
        "period",
        "feedstock",
        "ghg_reduction",
        "volume",
        "country_of_origin",
        "added_by",
    ]
    search_fields = [
        "feedstock__name",
        "biofuel__name",
        "carbure_producer__name",
        "unknown_producer",
        "carbure_id",
        "country_of_origin__name",
        "carbure_client__name",
        "unknown_client",
        "carbure_delivery_site__name",
        "unknown_delivery_site",
        "free_field",
        "transport_document_reference",
        "production_site_double_counting_certificate",
    ]

    def get_authenticators(self):
        method = self.request.method.lower()

        if method == "options":
            self.action = "metadata"
        else:
            self.action = self.action_map.get(method)
        if self.action in ["list", "add", "bulk_create"]:
            return [
                SessionAuthentication(),
                BasicAuthentication(),
                APIKeyAuthentication(),
            ]
        return super().get_authenticators()

    def get_permissions(self):
        # TODO fix permissions if needed
        if self.action in [
            "toggle_warning",
            "get_template",
            "get_lots_summary",
            "list",
            "filters",
            "details",
        ]:
            self.permission_classes = (
                IsAuthenticated,
                HasUserRights(None, [Entity.OPERATOR, Entity.PRODUCER, Entity.TRADER]),
            )
        if self.action in ["accept_consumption"]:
            return [
                IsAuthenticated,
                HasUserRights([UserRights.RW, UserRights.ADMIN], [Entity.POWER_OR_HEAT_PRODUCER]),
            ]
        return super().get_permissions()

    def get_serializer_class(self):
        entity_id = self.request.query_params.get("entity_id")

        entity = get_object_or_404(Entity, id=entity_id)

        if entity.entity_type in (Entity.ADMIN, Entity.AUDITOR):
            return CarbureLotAdminSerializer
        else:
            return CarbureLotPublicSerializer

    def get_queryset(self):
        queryset = CarbureLot.objects.select_related(
            "carbure_producer",
            "carbure_supplier",
            "carbure_client",
            "added_by",
            "carbure_vendor",
            "carbure_production_site",
            "carbure_production_site__producer",
            "carbure_production_site__country",
            "production_country",
            "carbure_dispatch_site",
            "carbure_dispatch_site__country",
            "dispatch_site_country",
            "carbure_delivery_site",
            "carbure_delivery_site__country",
            "delivery_site_country",
            "feedstock",
            "biofuel",
            "country_of_origin",
            "parent_lot",
            "parent_stock",
            "parent_stock__carbure_client",
            "parent_stock__carbure_supplier",
            "parent_stock__feedstock",
            "parent_stock__biofuel",
            "parent_stock__depot",
            "parent_stock__country_of_origin",
            "parent_stock__production_country",
        )
        export = self.request.query_params.get("export")

        entity_id = self.request.query_params.get("entity_id")
        entity = get_object_or_404(Entity, id=entity_id)

        correction = self.request.query_params.get("correction")
        history = self.request.query_params.get("history")

        if correction == "true":
            queryset = queryset.filter(
                Q(correction_status__in=[CarbureLot.IN_CORRECTION, CarbureLot.FIXED]) | Q(lot_status=CarbureLot.REJECTED)
            )

        elif history != "true" and entity.entity_type not in (
            Entity.ADMIN,
            Entity.AUDITOR,
        ):
            queryset = queryset.exclude(lot_status__in=[CarbureLot.FROZEN, CarbureLot.ACCEPTED])

        if not export:
            return queryset.prefetch_related(
                "genericerror_set",
                "carbure_production_site__productionsitecertificate_set",
            )

        return queryset
