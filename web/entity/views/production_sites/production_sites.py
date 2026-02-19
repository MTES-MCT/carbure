from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework.viewsets import ModelViewSet

from core.exceptions import ResourceConflict
from core.models import CarbureLot, Entity
from doublecount.permissions import HasDoubleCountingAdminRights
from entity.permissions import HasProducerRights, HasProducerWriteRights
from entity.serializers.production_sites import EntityProductionSiteSerializer, EntityProductionSiteWriteSerializer
from transactions.models.production_site import ProductionSite
from transactions.models.site import Site


@extend_schema(
    parameters=[
        OpenApiParameter(
            "entity_id",
            OpenApiTypes.INT,
            OpenApiParameter.QUERY,
            description="Entity ID",
            required=True,
        ),
        OpenApiParameter(
            "company_id",
            OpenApiTypes.INT,
            OpenApiParameter.QUERY,
            description="Entity ID",
        ),
    ],
)
class ProductionSiteViewSet(ModelViewSet[Site]):
    queryset = ProductionSite.objects.filter(site_type=Site.PRODUCTION_BIOLIQUID)
    serializer_class = EntityProductionSiteSerializer
    permission_classes = [HasProducerRights | HasDoubleCountingAdminRights]
    lookup_field = "id"

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [HasProducerWriteRights()]

        return super().get_permissions()

    def get_queryset(self):
        queryset = super().get_queryset()

        entity = self.request.entity
        if entity.entity_type == Entity.PRODUCER:
            queryset = queryset.filter(created_by=entity)
        elif "company_id" in self.request.query_params:
            queryset = queryset.filter(created_by_id=self.request.query_params.get("company_id"))

        return (
            queryset.order_by("id")
            .select_related("country")
            .prefetch_related(
                "productionsiteinput_set__matiere_premiere",
                "productionsiteoutput_set__biocarburant",
                "productionsitecertificate_set__certificate__certificate",
            )
        )

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return EntityProductionSiteWriteSerializer

        return super().get_serializer_class()

    def get_serializer_context(self):
        return {"entity_id": self.request.entity.pk}

    def perform_destroy(self, production_site):
        lots = CarbureLot.objects.filter(
            carbure_production_site=production_site,
            lot_status__in=[CarbureLot.ACCEPTED, CarbureLot.FROZEN],
        )

        if lots.count() > 0:
            raise ResourceConflict(
                _("Impossible de supprimer ce site de production, des lots de biocarburant y sont associés.")
            )

        production_site.delete()
