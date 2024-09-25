from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.viewsets import GenericViewSet

from core.models import CarbureLot, Entity
from core.serializers import CarbureLotAdminSerializer, CarbureLotPublicSerializer
from transactions.filters import LotsFilter

from .mixins import ActionMixin


class LotsViewSet(GenericViewSet, ActionMixin):
    lookup_field = "id"
    serializer_class = CarbureLotPublicSerializer
    filterset_class = LotsFilter

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
