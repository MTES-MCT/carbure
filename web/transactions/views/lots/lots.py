from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from apikey.authentication import APIKeyAuthentication
from core.models import CarbureLot, Entity, UserRights
from core.serializers import CarbureLotAdminSerializer, CarbureLotPublicSerializer
from transactions.filters import LotsFilter
from transactions.permissions import HasAdminRights, HasUserRights

from .mixins import ActionMixin


class LotsViewSet(GenericViewSet, ActionMixin):
    lookup_field = "id"
    ENTITY_TYPES = [
        Entity.OPERATOR,
        Entity.PRODUCER,
        Entity.TRADER,
        Entity.POWER_OR_HEAT_PRODUCER,
    ]
    permission_classes = (
        IsAuthenticated,
        HasUserRights([UserRights.ADMIN, UserRights.RW], ENTITY_TYPES),
    )
    serializer_class = CarbureLotPublicSerializer
    filterset_class = LotsFilter
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
        if self.request:
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
            "add_comment",
            "toggle_warning",
            "template",
            "summary",
            "list",
            "retrieve",
            "export",
            "filters",
            "declarations",
        ]:
            return (
                HasUserRights(
                    None,
                    [
                        Entity.OPERATOR,
                        Entity.PRODUCER,
                        Entity.TRADER,
                        Entity.POWER_OR_HEAT_PRODUCER,
                        Entity.ADMIN,
                        Entity.AUDITOR,
                    ],
                ),
            )
        if self.action in ["accept_consumption"]:
            return [
                HasUserRights([UserRights.RW, UserRights.ADMIN], [Entity.POWER_OR_HEAT_PRODUCER]),
            ]
        if self.action in ["update_many", "delete_many", "map", "admin_declarations"]:
            return [HasAdminRights()]
        if self.action in ["mark_conform", "mark_non_conform"]:
            return [HasUserRights(None, [Entity.AUDITOR])]
        if self.action in ["toggle_pin"]:
            return [HasUserRights(None, [Entity.AUDITOR, Entity.ADMIN])]
        return super().get_permissions()

    def get_serializer_class(self):
        if getattr(self, "swagger_fake_view", False):
            return CarbureLotPublicSerializer

        entity_id = self.request.query_params.get("entity_id")

        entity = get_object_or_404(Entity, id=entity_id)

        if entity.entity_type in (Entity.ADMIN, Entity.AUDITOR):
            return CarbureLotAdminSerializer
        else:
            return CarbureLotPublicSerializer

    def get_queryset(self):
        queryset = CarbureLot.objects.none()
        if getattr(self, "swagger_fake_view", False):
            return queryset
        if self.request and not self.request.user.is_anonymous:
            queryset = CarbureLot.objects.select_related(
                "carbure_producer",
                "carbure_supplier",
                "carbure_client",
                "added_by",
                "carbure_vendor",
                "carbure_production_site",
                "carbure_production_site__created_by",
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

            correction = self.request.query_params.get("correction", False)
            history = self.request.query_params.get("history", False)
            if correction == "true":
                queryset = queryset.filter(
                    Q(
                        correction_status__in=[
                            CarbureLot.IN_CORRECTION,
                            CarbureLot.FIXED,
                        ]
                    )
                    | Q(lot_status=CarbureLot.REJECTED)
                )

            elif history != "true" and entity.entity_type not in (
                Entity.ADMIN,
                Entity.AUDITOR,
            ):
                queryset = queryset.exclude(lot_status__in=[CarbureLot.FROZEN, CarbureLot.ACCEPTED])
            if entity.entity_type == Entity.AUDITOR:
                rights = self.request.session.get("rights")
                allowed_entities = [entity for entity in rights if rights[entity] == UserRights.AUDITOR]
                queryset = queryset.exclude(lot_status__in=[CarbureLot.DRAFT, CarbureLot.DELETED])
                queryset = queryset.filter(
                    Q(carbure_client__in=allowed_entities)
                    | Q(carbure_supplier__in=allowed_entities)
                    | Q(added_by__in=allowed_entities)
                )

            if not export:
                return queryset.prefetch_related(
                    "genericerror_set",
                    "carbure_production_site__productionsitecertificate_set",
                )

        return queryset
