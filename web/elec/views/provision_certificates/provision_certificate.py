from django.db.models import Sum
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from core.models import Entity
from core.pagination import MetadataPageNumberPagination
from elec.filters.provision_certificates import ProvisionCertificateFilter
from elec.models import ElecProvisionCertificate
from elec.permissions import HasCpoUserRights, HasElecAdminRights
from elec.serializers.elec_provision_certificate import ElecProvisionCertificateSerializer

from .mixins import ActionMixin


class ProvisionCertificatePagination(MetadataPageNumberPagination):
    aggregate_fields = {
        "available_energy": Sum("remaining_energy_amount"),
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
class ProvisionCertificateViewSet(ActionMixin, RetrieveModelMixin, ListModelMixin, GenericViewSet[ElecProvisionCertificate]):
    queryset = ElecProvisionCertificate.objects.all()
    serializer_class = ElecProvisionCertificateSerializer
    filterset_class = ProvisionCertificateFilter
    pagination_class = ProvisionCertificatePagination
    permission_classes = [IsAuthenticated & (HasCpoUserRights | HasElecAdminRights)]
    lookup_field = "id"
    search_fields = ["cpo__name", "operating_unit"]

    def get_permissions(self):
        if self.action in ("balance", "transfer"):
            return [IsAuthenticated(), HasCpoUserRights()]
        if self.action == "import_certificates":
            return [IsAuthenticated(), HasElecAdminRights()]

        return super().get_permissions()

    def get_queryset(self):
        queryset = super().get_queryset()

        entity = self.request.entity
        if entity.entity_type == Entity.CPO:
            queryset = ElecProvisionCertificate.objects.filter(cpo=entity)

        return queryset.select_related("cpo")
